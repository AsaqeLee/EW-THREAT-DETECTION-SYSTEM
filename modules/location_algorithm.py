import numpy as np
from scipy.optimize import minimize, least_squares
from typing import List, Dict, Tuple, Optional
import math
from .geo_converter import GeoConverter

class LocationAlgorithm:
    """定位算法引擎 - 基于功率衰减模型的干扰源定位"""
    
    def __init__(self, geo_converter: GeoConverter = None):
        """初始化算法参数"""
        self.path_loss_exponent = 2.0  # 路径损耗指数
        self.reference_power = 100.0   # 参考功率 (dBm)
        self.reference_distance = 1.0  # 参考距离 (km)
        self.geo_converter = geo_converter or GeoConverter()
        
    def calculate_location(self, power_data: List[Dict],
                         normal_indices: Optional[List[int]] = None,
                         use_geo_coordinates: bool = False) -> Dict:
        """
        计算干扰源位置

        Args:
            power_data: 电台功率数据列表
            normal_indices: 正常电台的索引列表（用于排除异常数据）
            use_geo_coordinates: 是否使用地理坐标计算

        Returns:
            定位结果字典
        """
        if not power_data:
            return {'error': '没有功率数据'}

        # 如果没有指定正常电台索引，使用所有电台
        if normal_indices is None:
            normal_indices = list(range(len(power_data)))

        # 提取正常电台的数据
        valid_data = [power_data[i] for i in normal_indices]

        if len(valid_data) < 3:
            return {'error': '有效电台数量不足，至少需要3个电台进行定位'}

        # 准备数据
        if use_geo_coordinates and 'lat' in valid_data[0] and 'lon' in valid_data[0]:
            # 使用地理坐标
            stations_geo = np.array([[d['lat'], d['lon']] for d in valid_data])
            # 转换为本地坐标进行计算
            stations_pos = np.array([self.geo_converter.latlon_to_xy(d['lat'], d['lon']) for d in valid_data])
        else:
            # 使用本地坐标
            stations_pos = np.array([[d['x'], d['y']] for d in valid_data])
            stations_geo = None

        received_powers = np.array([d['power'] for d in valid_data])

        # 使用多种方法进行定位
        results = {}

        # 方法1: 最小二乘法
        ls_result = self._least_squares_location(stations_pos, received_powers)
        results['least_squares'] = ls_result

        # 方法2: 加权最小二乘法
        wls_result = self._weighted_least_squares_location(stations_pos, received_powers)
        results['weighted_least_squares'] = wls_result

        # 方法3: 质心法（作为初始估计）
        centroid_result = self._centroid_location(stations_pos, received_powers)
        results['centroid'] = centroid_result
        
        # 选择最佳结果（优先选择能容纳最多电台且残差合理的方法）
        best_method = self._select_best_method(results, len(valid_data))
        best_result = results[best_method]

        # 如果最佳方法的置信度太低，尝试进一步剔除异常值
        if best_result['confidence'] < 70 and len(valid_data) > 4:
            refined_result = self._refine_location_with_outlier_removal(
                stations_pos, received_powers, best_result
            )
            if refined_result['confidence'] > best_result['confidence']:
                best_result = refined_result
                best_method = 'refined_' + best_method

        # 转换结果坐标 - 始终包含经纬度坐标
        final_position = best_result['position'].copy()

        # 确保结果包含经纬度坐标
        if 'lat' not in final_position or 'lon' not in final_position:
            lat, lon = self.geo_converter.xy_to_latlon(final_position['x'], final_position['y'])
            final_position['lat'] = lat
            final_position['lon'] = lon

        # 如果使用地理坐标模式，确保坐标一致性
        if use_geo_coordinates and stations_geo is not None:
            # 重新转换以确保精度
            lat, lon = self.geo_converter.xy_to_latlon(final_position['x'], final_position['y'])
            final_position['lat'] = lat
            final_position['lon'] = lon

        return {
            'position': final_position,
            'confidence': best_result['confidence'],
            'residual': best_result['residual'],
            'method_used': best_method,
            'all_results': results,
            'valid_stations_count': len(valid_data),
            'excluded_stations': len(power_data) - len(valid_data),
            'quality_assessment': self._assess_location_quality(best_result, len(valid_data)),
            'coordinate_system': 'geographic' if use_geo_coordinates else 'local'
        }
    
    def _least_squares_location(self, stations_pos: np.ndarray, 
                              received_powers: np.ndarray) -> Dict:
        """最小二乘法定位"""
        def objective_function(pos):
            """目标函数：最小化预测功率与实际功率的差的平方和"""
            x, y = pos
            predicted_powers = []
            
            for i, (sx, sy) in enumerate(stations_pos):
                distance = np.sqrt((x - sx)**2 + (y - sy)**2)
                if distance < self.reference_distance:
                    distance = self.reference_distance
                
                path_loss = 10 * self.path_loss_exponent * np.log10(distance / self.reference_distance)
                predicted_power = self.reference_power - path_loss
                predicted_powers.append(predicted_power)
            
            predicted_powers = np.array(predicted_powers)
            return np.sum((predicted_powers - received_powers)**2)
        
        # 初始猜测：电台位置的质心
        initial_guess = np.mean(stations_pos, axis=0)
        
        # 优化
        result = minimize(objective_function, initial_guess, method='BFGS')
        
        # 计算置信度（基于残差）
        residual = result.fun
        confidence = max(0, 100 - residual / len(stations_pos))
        
        return {
            'position': {'x': float(result.x[0]), 'y': float(result.x[1])},
            'confidence': min(100, max(0, confidence)),
            'residual': float(residual),
            'success': result.success
        }
    
    def _weighted_least_squares_location(self, stations_pos: np.ndarray, 
                                       received_powers: np.ndarray) -> Dict:
        """加权最小二乘法定位"""
        def weighted_objective_function(pos):
            """加权目标函数：功率越高的电台权重越大"""
            x, y = pos
            weighted_error = 0
            
            for i, (sx, sy) in enumerate(stations_pos):
                distance = np.sqrt((x - sx)**2 + (y - sy)**2)
                if distance < self.reference_distance:
                    distance = self.reference_distance
                
                path_loss = 10 * self.path_loss_exponent * np.log10(distance / self.reference_distance)
                predicted_power = self.reference_power - path_loss
                
                # 权重：功率越高，权重越大
                weight = max(0.1, received_powers[i] / 100.0)
                error = (predicted_power - received_powers[i])**2
                weighted_error += weight * error
            
            return weighted_error
        
        # 初始猜测
        initial_guess = np.mean(stations_pos, axis=0)
        
        # 优化
        result = minimize(weighted_objective_function, initial_guess, method='BFGS')
        
        # 计算置信度
        residual = result.fun
        confidence = max(0, 100 - residual / len(stations_pos))
        
        return {
            'position': {'x': float(result.x[0]), 'y': float(result.x[1])},
            'confidence': min(100, max(0, confidence)),
            'residual': float(residual),
            'success': result.success
        }
    
    def _centroid_location(self, stations_pos: np.ndarray, 
                         received_powers: np.ndarray) -> Dict:
        """加权质心法定位"""
        # 将功率转换为权重（功率越高，权重越大）
        min_power = np.min(received_powers)
        weights = received_powers - min_power + 1  # 避免负权重
        weights = weights / np.sum(weights)  # 归一化
        
        # 计算加权质心
        centroid_x = np.sum(stations_pos[:, 0] * weights)
        centroid_y = np.sum(stations_pos[:, 1] * weights)
        
        # 计算残差（用于评估质量）
        residual = 0
        for i, (sx, sy) in enumerate(stations_pos):
            distance = np.sqrt((centroid_x - sx)**2 + (centroid_y - sy)**2)
            if distance < self.reference_distance:
                distance = self.reference_distance
            
            path_loss = 10 * self.path_loss_exponent * np.log10(distance / self.reference_distance)
            predicted_power = self.reference_power - path_loss
            residual += (predicted_power - received_powers[i])**2
        
        confidence = max(0, 100 - residual / len(stations_pos))
        
        return {
            'position': {'x': float(centroid_x), 'y': float(centroid_y)},
            'confidence': min(100, max(0, confidence)),
            'residual': float(residual),
            'success': True
        }
    
    def calculate_distance_from_power(self, received_power: float) -> float:
        """根据接收功率计算距离"""
        path_loss = self.reference_power - received_power
        distance = self.reference_distance * (10 ** (path_loss / (10 * self.path_loss_exponent)))
        return distance
    
    def validate_location_result(self, result: Dict, power_data: List[Dict]) -> Dict:
        """验证定位结果的合理性"""
        if 'position' not in result:
            return {'valid': False, 'reason': '没有位置信息'}

        pos = result['position']
        x, y = pos['x'], pos['y']

        # 检查位置是否在合理范围内（扩大范围）
        if x < -50 or x > 150 or y < -50 or y > 150:
            return {'valid': False, 'reason': '位置超出有效范围'}

        # 检查与电台的距离是否合理
        min_distance = float('inf')
        for station in power_data:
            distance = np.sqrt((x - station['x'])**2 + (y - station['y'])**2)
            min_distance = min(min_distance, distance)

        if min_distance < 1.0:
            return {'valid': False, 'reason': '位置过于接近电台'}

        return {'valid': True, 'reason': '位置合理'}

    def _select_best_method(self, results: Dict, valid_stations_count: int) -> str:
        """选择最佳定位方法"""
        # 评分标准：残差越小越好，但要考虑方法的稳定性
        method_scores = {}

        for method, result in results.items():
            if not result.get('success', False):
                method_scores[method] = float('inf')
                continue

            residual = result.get('residual', float('inf'))
            confidence = result.get('confidence', 0)

            # 综合评分：残差权重70%，置信度权重30%
            score = residual * 0.7 + (100 - confidence) * 0.3

            # 对于电台数量较多的情况，优先选择加权最小二乘法
            if valid_stations_count >= 6 and method == 'weighted_least_squares':
                score *= 0.9  # 给予10%的优势

            method_scores[method] = score

        return min(method_scores.keys(), key=lambda k: method_scores[k])

    def _refine_location_with_outlier_removal(self, stations_pos: np.ndarray,
                                            received_powers: np.ndarray,
                                            initial_result: Dict) -> Dict:
        """通过进一步剔除异常值来优化定位结果"""
        best_result = initial_result.copy()

        # 计算每个电台的预测误差
        pos = initial_result['position']
        x, y = pos['x'], pos['y']

        errors = []
        for i, (sx, sy) in enumerate(stations_pos):
            distance = np.sqrt((x - sx)**2 + (y - sy)**2)
            if distance < self.reference_distance:
                distance = self.reference_distance

            path_loss = 10 * self.path_loss_exponent * np.log10(distance / self.reference_distance)
            predicted_power = self.reference_power - path_loss
            error = abs(predicted_power - received_powers[i])
            errors.append((i, error))

        # 按误差排序，逐步剔除误差最大的电台
        errors.sort(key=lambda x: x[1], reverse=True)

        for remove_count in range(1, min(3, len(errors) - 3)):  # 最多剔除2个，至少保留3个
            # 剔除误差最大的电台
            exclude_indices = [errors[i][0] for i in range(remove_count)]
            include_indices = [i for i in range(len(stations_pos)) if i not in exclude_indices]

            if len(include_indices) < 3:
                break

            # 使用剩余电台重新计算
            refined_stations = stations_pos[include_indices]
            refined_powers = received_powers[include_indices]

            refined_result = self._weighted_least_squares_location(refined_stations, refined_powers)

            if refined_result['confidence'] > best_result['confidence']:
                best_result = refined_result
                best_result['excluded_outliers'] = remove_count

        return best_result

    def _assess_location_quality(self, result: Dict, valid_stations_count: int) -> Dict:
        """评估定位质量"""
        confidence = result.get('confidence', 0)
        residual = result.get('residual', float('inf'))

        if confidence >= 85:
            quality = 'EXCELLENT'
            reliability = 'HIGH'
        elif confidence >= 70:
            quality = 'GOOD'
            reliability = 'MEDIUM'
        elif confidence >= 50:
            quality = 'FAIR'
            reliability = 'LOW'
        else:
            quality = 'POOR'
            reliability = 'VERY_LOW'

        # 根据有效电台数量调整评估
        if valid_stations_count < 4:
            reliability = 'VERY_LOW'
        elif valid_stations_count >= 6:
            if quality in ['GOOD', 'EXCELLENT']:
                reliability = 'HIGH'

        return {
            'quality': quality,
            'reliability': reliability,
            'confidence_level': confidence,
            'residual_error': residual,
            'stations_used': valid_stations_count,
            'assessment': f'{quality} quality with {reliability} reliability'
        }

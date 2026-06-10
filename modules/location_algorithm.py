import numpy as np
from scipy.optimize import minimize
from typing import List, Dict, Tuple, Optional
import math
import random
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

        # --- Patch 03: Robust Localization Pipeline ---
        # Step 1: RANSAC 离群值过滤
        inlier_indices = self._ransac_outlier_filtering(stations_pos, received_powers)
        inlier_pos = stations_pos[inlier_indices]
        inlier_powers = received_powers[inlier_indices]

        # Step 2: 多起点鲁棒优化 (Multi-start BFGS)
        best_result = self._robust_minimize_location(inlier_pos, inlier_powers)
        best_method = "robust_bfgs_ransac"
        
        # Step 3: 质量评估
        quality_info = self._assess_location_quality(best_result, len(inlier_indices))

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
            'valid_stations_count': len(inlier_indices),
            'excluded_stations': len(power_data) - len(valid_data),
            'quality_assessment': quality_info,
            'coordinate_system': 'geographic' if use_geo_coordinates else 'local'
        }

    def _ransac_outlier_filtering(self, stations_pos: np.ndarray, received_powers: np.ndarray) -> List[int]:
        """
        RANSAC implementation to filter out outlier stations.
        Returns indices of inlier stations.
        """
        best_inliers = []
        n_stations = len(stations_pos)
        if n_stations < 4:
            return list(range(n_stations))

        iterations = 50
        threshold = 5.0  # dB residual threshold

        for _ in range(iterations):
            # Randomly sample 3 stations to fit a candidate model
            sample_idx = random.sample(range(n_stations), 3)
            
            # Quick centroid-based fit for the sample
            guess = np.mean(stations_pos[sample_idx], axis=0)
            
            # Count inliers for this model
            current_inliers = []
            for i in range(n_stations):
                dist = np.linalg.norm(guess - stations_pos[i])
                dist = max(dist, self.reference_distance)
                pred_p = self.reference_power - 10 * self.path_loss_exponent * np.log10(dist / self.reference_distance)
                if abs(pred_p - received_powers[i]) < threshold:
                    current_inliers.append(i)
            
            if len(current_inliers) > len(best_inliers):
                best_inliers = current_inliers
                
        return best_inliers if len(best_inliers) >= 3 else list(range(n_stations))

    def _robust_minimize_location(self, stations_pos: np.ndarray, received_powers: np.ndarray) -> Dict:
        """
        Robust optimization using Multi-start BFGS to avoid local minima.
        NOTE: 'stations_pos' are expected to be local flat projections (e.g., meters or km) 
        converted by GeoConverter. Euclidean distances are calculated in this local frame 
        to avoid spherical projection errors during optimization.
        """
        def objective(pos):
            total_err = 0
            for i, (sx, sy) in enumerate(stations_pos):
                # Euclidean distance in local projection frame
                dist = np.sqrt((pos[0] - sx)**2 + (pos[1] - sy)**2)
                dist = max(dist, self.reference_distance)
                # Power decay model (Log-distance path loss)
                pred = self.reference_power - 10 * self.path_loss_exponent * np.log10(dist / self.reference_distance)
                total_err += (pred - received_powers[i])**2
            return total_err

        # Starting points: 1. Centroid, 2. Max power station, 3-5. Jittered points
        centroid = np.mean(stations_pos, axis=0)
        max_power_idx = np.argmax(received_powers)
        starts = [
            centroid,
            stations_pos[max_power_idx],
            centroid + np.array([10, 10]),
            centroid + np.array([-10, -10])
        ]

        best_res = None
        for start_p in starts:
            res = minimize(objective, start_p, method='BFGS')
            # Select absolute minimum residual point even if optimization didn't perfectly converge
            if best_res is None or res.fun < best_res.fun:
                best_res = res

        residual = best_res.fun
        confidence = max(0, 100 - residual / len(stations_pos))
        return {
            'position': {'x': float(best_res.x[0]), 'y': float(best_res.x[1])},
            'confidence': min(100, max(0, confidence)),
            'residual': float(residual),
            'success': best_res.success
        }

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

    def calculate_distance_from_power(self, received_power: float) -> float:
        """根据接收功率计算距离"""
        path_loss = self.reference_power - received_power
        distance = self.reference_distance * (10 ** (path_loss / (10 * self.path_loss_exponent)))
        return distance

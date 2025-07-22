import numpy as np
from typing import List, Dict, Tuple
from scipy import stats
import math

class AnomalyDetector:
    """异常检测器 - 检测电台数据中的异常值"""
    
    def __init__(self):
        """初始化异常检测参数"""
        self.z_score_threshold = 2.5  # Z-score阈值
        self.iqr_multiplier = 1.5     # IQR异常检测倍数
        self.min_stations_for_detection = 4  # 进行异常检测的最小电台数
        
    def detect_anomalies(self, power_data: List[Dict]) -> Dict:
        """
        检测功率数据中的异常值
        
        Args:
            power_data: 电台功率数据列表
            
        Returns:
            异常检测结果
        """
        if len(power_data) < self.min_stations_for_detection:
            return {
                'anomaly_indices': [],
                'normal_indices': list(range(len(power_data))),
                'anomaly_details': [],
                'detection_method': 'insufficient_data',
                'summary': f'数据量不足，需要至少{self.min_stations_for_detection}个电台'
            }
        
        powers = np.array([d['power'] for d in power_data])
        
        # 使用多种方法检测异常
        anomaly_results = {}
        
        # 方法1: Z-score检测
        z_score_anomalies = self._z_score_detection(powers)
        anomaly_results['z_score'] = z_score_anomalies
        
        # 方法2: IQR检测
        iqr_anomalies = self._iqr_detection(powers)
        anomaly_results['iqr'] = iqr_anomalies
        
        # 方法3: 基于距离的检测
        distance_anomalies = self._distance_based_detection(power_data)
        anomaly_results['distance_based'] = distance_anomalies
        
        # 综合判断异常
        final_anomalies = self._combine_anomaly_results(anomaly_results, len(power_data))
        
        # 生成详细结果
        anomaly_details = []
        for idx in final_anomalies:
            station = power_data[idx]
            details = {
                'station_id': station['station_id'],
                'station_name': station['station_name'],
                'power': station['power'],
                'anomaly_type': self._classify_anomaly_type(station['power'], powers),
                'confidence': self._calculate_anomaly_confidence(idx, anomaly_results)
            }
            anomaly_details.append(details)
        
        normal_indices = [i for i in range(len(power_data)) if i not in final_anomalies]
        
        return {
            'anomaly_indices': final_anomalies,
            'normal_indices': normal_indices,
            'anomaly_details': anomaly_details,
            'detection_method': 'combined',
            'summary': f'检测到{len(final_anomalies)}个异常电台，{len(normal_indices)}个正常电台',
            'statistics': self._calculate_statistics(powers, final_anomalies)
        }
    
    def _z_score_detection(self, powers: np.ndarray) -> List[int]:
        """Z-score异常检测"""
        z_scores = np.abs(stats.zscore(powers))
        anomaly_indices = np.where(z_scores > self.z_score_threshold)[0].tolist()
        return anomaly_indices
    
    def _iqr_detection(self, powers: np.ndarray) -> List[int]:
        """IQR异常检测"""
        q1 = np.percentile(powers, 25)
        q3 = np.percentile(powers, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr
        
        anomaly_indices = []
        for i, power in enumerate(powers):
            if power < lower_bound or power > upper_bound:
                anomaly_indices.append(i)
        
        return anomaly_indices
    
    def _distance_based_detection(self, power_data: List[Dict]) -> List[int]:
        """基于距离的异常检测"""
        anomaly_indices = []
        
        # 计算每个电台到其他电台的平均距离
        for i, station_i in enumerate(power_data):
            distances = []
            for j, station_j in enumerate(power_data):
                if i != j:
                    # 计算功率差异与位置距离的比值
                    power_diff = abs(station_i['power'] - station_j['power'])
                    position_dist = math.sqrt(
                        (station_i['x'] - station_j['x'])**2 + 
                        (station_i['y'] - station_j['y'])**2
                    )
                    if position_dist > 0:
                        ratio = power_diff / position_dist
                        distances.append(ratio)
            
            if distances:
                avg_ratio = np.mean(distances)
                std_ratio = np.std(distances)
                
                # 如果某个电台的比值明显偏离平均值，可能是异常
                if std_ratio > 0:
                    z_score = abs(avg_ratio - np.mean([np.mean(distances) for distances in [distances]])) / std_ratio
                    if z_score > 2.0:  # 可调整的阈值
                        anomaly_indices.append(i)
        
        return anomaly_indices
    
    def _combine_anomaly_results(self, anomaly_results: Dict, total_stations: int) -> List[int]:
        """综合多种方法的异常检测结果"""
        # 统计每个电台被标记为异常的次数
        anomaly_votes = {}
        for method, indices in anomaly_results.items():
            for idx in indices:
                anomaly_votes[idx] = anomaly_votes.get(idx, 0) + 1

        # 计算每个方法的权重（基于方法的可靠性）
        method_weights = {
            'z_score': 0.35,
            'iqr': 0.35,
            'distance_based': 0.3
        }

        # 计算加权投票分数
        weighted_scores = {}
        for idx, votes in anomaly_votes.items():
            score = 0
            for method, indices in anomaly_results.items():
                if idx in indices:
                    score += method_weights.get(method, 0.33)
            weighted_scores[idx] = score

        # 设置阈值（至少30%的加权投票）
        threshold = 0.3

        # 根据加权分数确定异常
        final_anomalies = [idx for idx, score in weighted_scores.items() if score >= threshold]

        # 限制异常电台数量（最多不超过总数的1/3）
        max_anomalies = max(1, total_stations // 3)
        if len(final_anomalies) > max_anomalies:
            # 按加权分数排序，保留分数最高的异常
            final_anomalies.sort(key=lambda x: weighted_scores[x], reverse=True)
            final_anomalies = final_anomalies[:max_anomalies]

        # 确保至少保留5个正常电台用于定位（如果总数足够）
        min_normal_stations = min(5, total_stations - 1)
        if total_stations - len(final_anomalies) < min_normal_stations:
            # 减少异常电台数量，确保有足够的正常电台
            max_allowed_anomalies = total_stations - min_normal_stations
            if max_allowed_anomalies > 0:
                final_anomalies = final_anomalies[:max_allowed_anomalies]
            else:
                final_anomalies = []

        return final_anomalies
    
    def _classify_anomaly_type(self, power: float, all_powers: np.ndarray) -> str:
        """分类异常类型"""
        median_power = np.median(all_powers)
        std_power = np.std(all_powers)
        
        if power > median_power + 2 * std_power:
            return 'high_power'
        elif power < median_power - 2 * std_power:
            return 'low_power'
        else:
            return 'outlier'
    
    def _calculate_anomaly_confidence(self, idx: int, anomaly_results: Dict) -> float:
        """计算异常置信度"""
        votes = sum(1 for indices in anomaly_results.values() if idx in indices)
        total_methods = len(anomaly_results)
        confidence = (votes / total_methods) * 100
        return round(confidence, 1)
    
    def _calculate_statistics(self, powers: np.ndarray, anomaly_indices: List[int]) -> Dict:
        """计算统计信息"""
        normal_powers = np.array([powers[i] for i in range(len(powers)) if i not in anomaly_indices])
        
        stats_dict = {
            'total_stations': len(powers),
            'normal_stations': len(normal_powers),
            'anomaly_stations': len(anomaly_indices),
            'power_mean': float(np.mean(powers)),
            'power_std': float(np.std(powers)),
            'power_median': float(np.median(powers)),
            'normal_power_mean': float(np.mean(normal_powers)) if len(normal_powers) > 0 else 0,
            'normal_power_std': float(np.std(normal_powers)) if len(normal_powers) > 0 else 0
        }
        
        return stats_dict
    
    def validate_detection_result(self, result: Dict) -> Dict:
        """验证异常检测结果的合理性"""
        anomaly_count = len(result['anomaly_indices'])
        total_count = len(result['normal_indices']) + anomaly_count
        
        if anomaly_count == 0:
            return {'valid': True, 'reason': '未检测到异常'}
        
        if anomaly_count > total_count * 0.5:
            return {'valid': False, 'reason': '异常电台数量过多，可能检测有误'}
        
        if total_count - anomaly_count < 3:
            return {'valid': False, 'reason': '正常电台数量不足，无法进行可靠定位'}
        
        return {'valid': True, 'reason': '异常检测结果合理'}

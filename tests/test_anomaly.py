import pytest
from modules.anomaly_detector import AnomalyDetector

def test_anomaly_detection_logic():
    detector = AnomalyDetector()
    
    # 正常数据
    power_data = [
        {'station_id': 0, 'power': -50},
        {'station_id': 1, 'power': -52},
        {'station_id': 2, 'power': -51},
        {'station_id': 3, 'power': -49},
        {'station_id': 4, 'power': -10}  # 明显的异常值（功率过高）
    ]
    
    result = detector.detect_anomalies(power_data)
    
    assert 'normal_indices' in result
    assert 'anomaly_indices' in result
    assert 4 in result['anomaly_indices']
    assert 0 in result['normal_indices']

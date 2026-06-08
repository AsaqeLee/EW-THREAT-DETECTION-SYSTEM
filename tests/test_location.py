import pytest
import numpy as np
from modules.geo_converter import GeoConverter
from modules.location_algorithm import LocationAlgorithm

def test_location_accuracy():
    geo_converter = GeoConverter()
    algo = LocationAlgorithm(geo_converter)
    
    # 模拟电台数据
    stations = [
        {'id': 0, 'x': 0, 'y': 0},
        {'id': 1, 'x': 100, 'y': 0},
        {'id': 2, 'x': 0, 'y': 100},
        {'id': 3, 'x': 100, 'y': 100}
    ]
    
    target_x, target_y = 50, 50
    path_loss_exponent = 2.0
    
    power_data = []
    for s in stations:
        dist = np.sqrt((s['x'] - target_x)**2 + (s['y'] - target_y)**2)
        # 简化功率模型 P = P0 - 10 * n * log10(d)
        power = 0 - 10 * path_loss_exponent * np.log10(max(dist, 1))
        power_data.append({
            'station_id': s['id'],
            'power': power,
            'x': s['x'],
            'y': s['y']
        })
        
    normal_indices = list(range(len(stations)))
    result = algo.calculate_location(power_data, normal_indices, use_geo_coordinates=False)
    
    assert 'x' in result
    assert 'y' in result
    # 允许一定的数值误差
    assert abs(result['x'] - target_x) < 1.0
    assert abs(result['y'] - target_y) < 1.0

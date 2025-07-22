import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from .geo_converter import GeoConverter

class DataSimulator:
    """数据模拟器 - 生成8个电台的位置和功率数据"""
    
    def __init__(self, center_lat: float = 39.9042, center_lon: float = 116.4074):
        """初始化8个电台的固定位置"""
        # 初始化地理坐标转换器
        self.geo_converter = GeoConverter(center_lat, center_lon)

        # 8个电台分布在200x200km的区域内，形成较好的几何分布
        # 使用更大的坐标范围，以北京为中心
        initial_stations = [
            {'id': 1, 'name': 'SENSOR-1', 'x': -80, 'y': -80},
            {'id': 2, 'name': 'SENSOR-2', 'x': 80, 'y': -80},
            {'id': 3, 'name': 'SENSOR-3', 'x': 80, 'y': 80},
            {'id': 4, 'name': 'SENSOR-4', 'x': -80, 'y': 80},
            {'id': 5, 'name': 'SENSOR-5', 'x': 0, 'y': -80},
            {'id': 6, 'name': 'SENSOR-6', 'x': 80, 'y': 0},
            {'id': 7, 'name': 'SENSOR-7', 'x': 0, 'y': 80},
            {'id': 8, 'name': 'SENSOR-8', 'x': -80, 'y': 0}
        ]

        # 为每个电台计算经纬度坐标
        self.stations = []
        for station in initial_stations:
            lat, lon = self.geo_converter.xy_to_latlon(station['x'], station['y'])
            self.stations.append({
                'id': station['id'],
                'name': station['name'],
                'x': station['x'],
                'y': station['y'],
                'lat': lat,
                'lon': lon
            })

        print(f"Initialized {len(self.stations)} stations with coordinates:")

        # 信号传播参数
        self.path_loss_exponent = 2.0  # 路径损耗指数
        self.reference_power = 100.0   # 参考功率 (dBm)
        self.reference_distance = 1.0  # 参考距离 (km)
        self.noise_std = 2.0          # 噪声标准差
        
    def get_stations_info(self) -> List[Dict]:
        """获取所有电台信息"""
        return self.stations.copy()

    def update_station_position(self, station_id: int, x: float, y: float) -> bool:
        """更新电台位置

        Args:
            station_id: 电台ID
            x: 新的X坐标
            y: 新的Y坐标

        Returns:
            更新是否成功
        """
        for i, station in enumerate(self.stations):
            if station['id'] == station_id:
                self.stations[i]['x'] = x
                self.stations[i]['y'] = y
                return True
        return False

    def reset_stations_positions(self) -> None:
        """重置电台位置为默认布局"""
        initial_stations = [
            {'id': 1, 'name': 'SENSOR-1', 'x': -80, 'y': -80},
            {'id': 2, 'name': 'SENSOR-2', 'x': 80, 'y': -80},
            {'id': 3, 'name': 'SENSOR-3', 'x': 80, 'y': 80},
            {'id': 4, 'name': 'SENSOR-4', 'x': -80, 'y': 80},
            {'id': 5, 'name': 'SENSOR-5', 'x': 0, 'y': -80},
            {'id': 6, 'name': 'SENSOR-6', 'x': 80, 'y': 0},
            {'id': 7, 'name': 'SENSOR-7', 'x': 0, 'y': 80},
            {'id': 8, 'name': 'SENSOR-8', 'x': -80, 'y': 0}
        ]

        # 重新计算经纬度坐标
        self.stations = []
        for station in initial_stations:
            lat, lon = self.geo_converter.xy_to_latlon(station['x'], station['y'])
            self.stations.append({
                'id': station['id'],
                'name': station['name'],
                'x': station['x'],
                'y': station['y'],
                'lat': lat,
                'lon': lon
            })

        print(f"Reset {len(self.stations)} stations to default positions")

    def add_station(self, name: str, lat: float, lon: float) -> Dict:
        """添加新电台"""
        new_id = max([s['id'] for s in self.stations]) + 1 if self.stations else 1
        x, y = self.geo_converter.latlon_to_xy(lat, lon)

        new_station = {
            'id': new_id,
            'name': name,
            'lat': lat,
            'lon': lon,
            'x': x,
            'y': y
        }

        self.stations.append(new_station)
        return new_station

    def update_station(self, station_id: int, name: str = None, lat: float = None, lon: float = None) -> bool:
        """更新电台信息"""
        for i, station in enumerate(self.stations):
            if station['id'] == station_id:
                if name is not None:
                    self.stations[i]['name'] = name
                if lat is not None and lon is not None:
                    self.stations[i]['lat'] = lat
                    self.stations[i]['lon'] = lon
                    x, y = self.geo_converter.latlon_to_xy(lat, lon)
                    self.stations[i]['x'] = x
                    self.stations[i]['y'] = y
                return True
        return False

    def delete_station(self, station_id: int) -> bool:
        """删除电台"""
        for i, station in enumerate(self.stations):
            if station['id'] == station_id:
                del self.stations[i]
                return True
        return False

    def set_center_coordinates(self, lat: float, lon: float) -> None:
        """设置新的中心坐标并重新计算所有电台的XY坐标"""
        self.geo_converter.set_center(lat, lon)

        # 重新计算所有电台的XY坐标
        for i, station in enumerate(self.stations):
            if 'lat' in station and 'lon' in station:
                x, y = self.geo_converter.latlon_to_xy(station['lat'], station['lon'])
                self.stations[i]['x'] = x
                self.stations[i]['y'] = y
    
    def calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float], use_geo: bool = False) -> float:
        """
        计算两点间距离

        Args:
            pos1: 第一个点的坐标 (x,y) 或 (lat,lon)
            pos2: 第二个点的坐标 (x,y) 或 (lat,lon)
            use_geo: 是否使用地理坐标计算

        Returns:
            距离（公里）
        """
        if use_geo:
            # 使用Haversine公式计算地理坐标距离
            return self.geo_converter.haversine_distance(pos1[0], pos1[1], pos2[0], pos2[1])
        else:
            # 使用欧几里得距离计算平面坐标距离
            return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def calculate_received_power(self, interference_pos: Tuple[float, float],
                               station_pos: Tuple[float, float], use_geo: bool = False) -> float:
        """
        计算电台接收到的功率
        使用路径损耗模型: P_r = P_t - 10*n*log10(d/d0)
        """
        distance = self.calculate_distance(interference_pos, station_pos, use_geo)

        # 避免距离为0的情况
        if distance < self.reference_distance:
            distance = self.reference_distance

        # 计算路径损耗
        path_loss = 10 * self.path_loss_exponent * np.log10(distance / self.reference_distance)

        # 接收功率 = 发射功率 - 路径损耗
        received_power = self.reference_power - path_loss

        # 添加高斯噪声
        noise = np.random.normal(0, self.noise_std)

        return received_power + noise
    
    def generate_power_data(self, interference_pos: Tuple[float, float],
                          add_anomaly: bool = False, use_geo_coordinates: bool = False) -> List[Dict]:
        """
        生成所有电台的功率数据

        Args:
            interference_pos: 干扰源位置 (x, y) 或 (lat, lon)
            add_anomaly: 是否添加异常数据
            use_geo_coordinates: 是否使用地理坐标

        Returns:
            包含所有电台功率数据的列表
        """
        power_data = []
        
        # 如果需要添加异常，随机选择1-2个电台
        anomaly_stations = []
        if add_anomaly:
            num_anomalies = random.randint(1, 2)
            anomaly_stations = random.sample(range(len(self.stations)), num_anomalies)
        
        for i, station in enumerate(self.stations):
            if use_geo_coordinates:
                station_pos = (station['lat'], station['lon'])
            else:
                station_pos = (station['x'], station['y'])

            if i in anomaly_stations:
                # 生成异常数据
                power = self._generate_anomaly_power(interference_pos, station_pos, use_geo_coordinates)
                is_anomaly = True
            else:
                # 生成正常数据
                power = self.calculate_received_power(interference_pos, station_pos, use_geo_coordinates)
                is_anomaly = False
            
            power_data.append({
                'station_id': station['id'],
                'station_name': station['name'],
                'x': station['x'],
                'y': station['y'],
                'power': round(power, 2),
                'is_anomaly': is_anomaly
            })
        
        return power_data
    
    def _generate_anomaly_power(self, interference_pos: Tuple[float, float],
                              station_pos: Tuple[float, float], use_geo: bool = False) -> float:
        """
        生成异常功率数据
        异常类型：
        1. 功率过高（设备故障）
        2. 功率过低（信号阻塞）
        3. 随机噪声（环境干扰）
        """
        normal_power = self.calculate_received_power(interference_pos, station_pos, use_geo)
        
        anomaly_type = random.choice(['high', 'low', 'noise'])
        
        if anomaly_type == 'high':
            # 功率异常高
            return normal_power + random.uniform(15, 30)
        elif anomaly_type == 'low':
            # 功率异常低
            return normal_power - random.uniform(15, 25)
        else:
            # 随机噪声
            return normal_power + random.uniform(-20, 20)
    
    def generate_test_scenarios(self) -> List[Dict]:
        """生成测试场景"""
        scenarios = [
            {
                'name': '中心位置干扰',
                'interference_pos': (50, 50),
                'add_anomaly': False,
                'description': '干扰源位于区域中心'
            },
            {
                'name': '边角位置干扰',
                'interference_pos': (20, 20),
                'add_anomaly': False,
                'description': '干扰源位于区域边角'
            },
            {
                'name': '中心位置干扰+异常',
                'interference_pos': (50, 50),
                'add_anomaly': True,
                'description': '干扰源位于中心，包含异常电台数据'
            },
            {
                'name': '随机位置干扰+异常',
                'interference_pos': (random.uniform(20, 80), random.uniform(20, 80)),
                'add_anomaly': True,
                'description': '随机位置干扰源，包含异常数据'
            }
        ]
        
        return scenarios

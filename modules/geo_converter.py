import math
from typing import Tuple, Dict, List
import numpy as np

class GeoConverter:
    """地理坐标转换器 - 处理经纬度与本地坐标系统的转换"""
    
    def __init__(self, center_lat: float = 39.9042, center_lon: float = 116.4074):
        """
        初始化地理坐标转换器

        Args:
            center_lat: 中心纬度（默认北京）
            center_lon: 中心经度（默认北京）
        """
        self.center_lat = center_lat
        self.center_lon = center_lon

        # 地球半径（米）
        self.earth_radius = 6378137.0

        # 计算中心点的弧度
        self.center_lat_rad = math.radians(center_lat)
        self.center_lon_rad = math.radians(center_lon)

        # 计算纬度方向的米/度转换因子
        self.lat_to_meters = self.earth_radius * math.pi / 180.0

        # 计算经度方向的米/度转换因子（考虑纬度影响）
        self.lon_to_meters = self.lat_to_meters * math.cos(self.center_lat_rad)

        # 调试信息
        print(f"GeoConverter initialized with center: ({center_lat}, {center_lon})")
        print(f"Conversion factors: lat_to_meters={self.lat_to_meters}, lon_to_meters={self.lon_to_meters}")
    
    def set_center(self, lat: float, lon: float) -> None:
        """设置新的中心点"""
        self.center_lat = lat
        self.center_lon = lon
        self.center_lat_rad = math.radians(lat)
        self.center_lon_rad = math.radians(lon)
        self.lon_to_meters = self.lat_to_meters * math.cos(self.center_lat_rad)
    
    def latlon_to_xy(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        将经纬度转换为本地XY坐标（公里）

        Args:
            lat: 纬度
            lon: 经度

        Returns:
            (x, y) 坐标，单位为公里
        """
        # 计算相对于中心点的偏移（度）
        delta_lat = lat - self.center_lat
        delta_lon = lon - self.center_lon

        # 转换为米
        y_meters = delta_lat * self.lat_to_meters
        x_meters = delta_lon * self.lon_to_meters

        # 转换为公里
        x_km = x_meters / 1000.0
        y_km = y_meters / 1000.0

        print(f"LatLon to XY: ({lat}, {lon}) -> ({x_km:.2f}, {y_km:.2f})")

        return x_km, y_km
    
    def xy_to_latlon(self, x: float, y: float) -> Tuple[float, float]:
        """
        将本地XY坐标（公里）转换为经纬度

        Args:
            x: X坐标（公里）
            y: Y坐标（公里）

        Returns:
            (lat, lon) 经纬度
        """
        # 转换为米
        x_meters = x * 1000.0
        y_meters = y * 1000.0

        # 转换为度偏移
        delta_lat = y_meters / self.lat_to_meters
        delta_lon = x_meters / self.lon_to_meters

        # 计算绝对坐标
        lat = self.center_lat + delta_lat
        lon = self.center_lon + delta_lon

        print(f"XY to LatLon: ({x:.2f}, {y:.2f}) -> ({lat:.6f}, {lon:.6f})")

        return lat, lon
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        使用Haversine公式计算两点间的距离（公里）
        
        Args:
            lat1, lon1: 第一个点的经纬度
            lat2, lon2: 第二个点的经纬度
            
        Returns:
            距离（公里）
        """
        # 转换为弧度
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # 计算差值
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine公式
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # 距离（公里）
        distance = self.earth_radius * c / 1000.0
        
        return distance
    
    def euclidean_distance_km(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """
        计算本地坐标系统中两点间的欧几里得距离（公里）
        
        Args:
            x1, y1: 第一个点的XY坐标（公里）
            x2, y2: 第二个点的XY坐标（公里）
            
        Returns:
            距离（公里）
        """
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def convert_stations_to_xy(self, stations: List[Dict]) -> List[Dict]:
        """
        将电台列表从经纬度转换为XY坐标
        
        Args:
            stations: 包含经纬度的电台列表
            
        Returns:
            包含XY坐标的电台列表
        """
        converted_stations = []
        
        for station in stations:
            if 'lat' in station and 'lon' in station:
                x, y = self.latlon_to_xy(station['lat'], station['lon'])
                converted_station = station.copy()
                converted_station['x'] = x
                converted_station['y'] = y
                converted_stations.append(converted_station)
            elif 'x' in station and 'y' in station:
                # 已经是XY坐标，直接复制
                converted_stations.append(station.copy())
        
        return converted_stations
    
    def convert_stations_to_latlon(self, stations: List[Dict]) -> List[Dict]:
        """
        将电台列表从XY坐标转换为经纬度
        
        Args:
            stations: 包含XY坐标的电台列表
            
        Returns:
            包含经纬度的电台列表
        """
        converted_stations = []
        
        for station in stations:
            if 'x' in station and 'y' in station:
                lat, lon = self.xy_to_latlon(station['x'], station['y'])
                converted_station = station.copy()
                converted_station['lat'] = lat
                converted_station['lon'] = lon
                converted_stations.append(converted_station)
            elif 'lat' in station and 'lon' in station:
                # 已经是经纬度，直接复制
                converted_stations.append(station.copy())
        
        return converted_stations
    
    def get_bounds_for_area(self, size_km: float = 100) -> Dict:
        """
        获取指定大小区域的边界坐标
        
        Args:
            size_km: 区域大小（公里）
            
        Returns:
            包含边界坐标的字典
        """
        half_size = size_km / 2
        
        # 计算四个角的坐标
        sw_lat, sw_lon = self.xy_to_latlon(-half_size, -half_size)  # 西南角
        ne_lat, ne_lon = self.xy_to_latlon(half_size, half_size)    # 东北角
        
        return {
            'southwest': {'lat': sw_lat, 'lon': sw_lon},
            'northeast': {'lat': ne_lat, 'lon': ne_lon},
            'center': {'lat': self.center_lat, 'lon': self.center_lon},
            'size_km': size_km
        }
    
    def validate_coordinates(self, lat: float, lon: float, max_distance_km: float = 100) -> bool:
        """
        验证坐标是否在允许的范围内
        
        Args:
            lat: 纬度
            lon: 经度
            max_distance_km: 最大允许距离（公里）
            
        Returns:
            是否在允许范围内
        """
        distance = self.haversine_distance(self.center_lat, self.center_lon, lat, lon)
        return distance <= max_distance_km
    
    def get_grid_coordinates(self, grid_size: int = 10) -> List[Dict]:
        """
        生成网格坐标点，用于显示参考网格
        
        Args:
            grid_size: 网格大小（公里）
            
        Returns:
            网格点列表
        """
        grid_points = []
        
        # 生成从-50到50公里的网格点
        for x in range(-50, 51, grid_size):
            for y in range(-50, 51, grid_size):
                lat, lon = self.xy_to_latlon(x, y)
                grid_points.append({
                    'x': x,
                    'y': y,
                    'lat': lat,
                    'lon': lon
                })
        
        return grid_points

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import numpy as np
from datetime import datetime
import json

# 导入自定义模块
from modules.data_simulator import DataSimulator
from modules.location_algorithm import LocationAlgorithm
from modules.anomaly_detector import AnomalyDetector
from modules.geo_converter import GeoConverter

app = Flask(__name__)
CORS(app)

# 初始化组件
geo_converter = GeoConverter()
data_simulator = DataSimulator()
location_algorithm = LocationAlgorithm(geo_converter)
anomaly_detector = AnomalyDetector()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/stations')
def get_stations():
    """获取电台信息"""
    stations = data_simulator.get_stations_info()
    return jsonify(stations)

@app.route('/api/simulate_data')
def simulate_data():
    """模拟数据生成"""
    # 获取参数
    coord_mode = request.args.get('coord_mode', 'geographic')
    add_anomaly = request.args.get('add_anomaly', 'false').lower() == 'true'
    path_loss_exponent = float(request.args.get('path_loss_exponent', 2.0))

    if coord_mode == 'geographic':
        # 地理坐标模式 - 直接使用经纬度坐标
        target_lat = float(request.args.get('target_lat', 39.9042))
        target_lon = float(request.args.get('target_lon', 116.4074))
        # 直接使用经纬度坐标进行计算
        interference_pos = (target_lat, target_lon)
        # 同时计算XY坐标用于显示
        interference_x, interference_y = data_simulator.geo_converter.latlon_to_xy(target_lat, target_lon)
        interference_position = {
            'lat': target_lat,
            'lon': target_lon,
            'x': interference_x,
            'y': interference_y
        }
    else:
        # 网格坐标模式
        interference_x = float(request.args.get('interference_x', 50))
        interference_y = float(request.args.get('interference_y', 50))
        # 转换为地理坐标
        target_lat, target_lon = data_simulator.geo_converter.xy_to_latlon(interference_x, interference_y)
        # 使用XY坐标进行计算
        interference_pos = (interference_x, interference_y)
        interference_position = {
            'lat': target_lat,
            'lon': target_lon,
            'x': interference_x,
            'y': interference_y
        }

    # 更新数据模拟器的路径损耗指数
    data_simulator.path_loss_exponent = path_loss_exponent
    location_algorithm.path_loss_exponent = path_loss_exponent

    # 生成模拟数据
    power_data = data_simulator.generate_power_data(
        interference_pos=interference_pos,
        add_anomaly=add_anomaly,
        use_geo_coordinates=(coord_mode == 'geographic')
    )

    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'interference_position': interference_position,
        'power_data': power_data,
        'has_anomaly': add_anomaly,
        'path_loss_exponent': path_loss_exponent,
        'coord_mode': coord_mode
    })

@app.route('/api/locate_interference', methods=['POST'])
def locate_interference():
    """定位干扰源"""
    data = request.get_json()
    power_data = data.get('power_data', [])
    coord_mode = data.get('coord_mode', 'geographic')

    if not power_data:
        return jsonify({'error': '没有功率数据'}), 400

    # 异常检测
    anomaly_result = anomaly_detector.detect_anomalies(power_data)

    # 定位计算
    location_result = location_algorithm.calculate_location(
        power_data,
        anomaly_result['normal_indices'],
        use_geo_coordinates=(coord_mode == 'geographic')
    )

    return jsonify({
        'location': location_result,
        'anomaly_detection': anomaly_result,
        'timestamp': datetime.now().isoformat(),
        'coord_mode': coord_mode
    })

@app.route('/api/reset_stations')
def reset_stations():
    """重置电台位置"""
    data_simulator.reset_stations_positions()
    return jsonify({
        'status': 'success',
        'message': '电台位置已重置',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/convert_coordinates', methods=['POST'])
def convert_coordinates():
    """坐标转换"""
    data = request.get_json()

    if 'lat' in data and 'lon' in data:
        # 经纬度转XY
        lat = float(data['lat'])
        lon = float(data['lon'])
        x, y = geo_converter.latlon_to_xy(lat, lon)
        return jsonify({
            'x': x,
            'y': y,
            'lat': lat,
            'lon': lon
        })
    elif 'x' in data and 'y' in data:
        # XY转经纬度
        x = float(data['x'])
        y = float(data['y'])
        lat, lon = geo_converter.xy_to_latlon(x, y)
        return jsonify({
            'x': x,
            'y': y,
            'lat': lat,
            'lon': lon
        })
    else:
        return jsonify({
            'error': '无效的坐标数据'
        }), 400

@app.route('/api/stations', methods=['POST'])
def add_station():
    """添加新电台"""
    data = request.get_json()
    name = data.get('name', 'NEW_SENSOR')
    lat = float(data.get('lat'))
    lon = float(data.get('lon'))

    new_station = data_simulator.add_station(name, lat, lon)
    return jsonify({
        'status': 'success',
        'station': new_station,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stations/<int:station_id>', methods=['PUT'])
def update_station(station_id):
    """更新电台信息"""
    data = request.get_json()
    name = data.get('name')
    lat = data.get('lat')
    lon = data.get('lon')

    if lat is not None:
        lat = float(lat)
    if lon is not None:
        lon = float(lon)

    success = data_simulator.update_station(station_id, name, lat, lon)

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Station updated successfully',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Station not found'
        }), 404

@app.route('/api/stations/<int:station_id>', methods=['DELETE'])
def delete_station(station_id):
    """删除电台"""
    success = data_simulator.delete_station(station_id)

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Station deleted successfully',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Station not found'
        }), 404

@app.route('/api/center_coordinates', methods=['POST'])
def set_center_coordinates():
    """设置中心坐标"""
    data = request.get_json()
    lat = float(data.get('lat'))
    lon = float(data.get('lon'))

    data_simulator.set_center_coordinates(lat, lon)

    return jsonify({
        'status': 'success',
        'center': {'lat': lat, 'lon': lon},
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system_status')
def system_status():
    """系统状态"""
    return jsonify({
        'status': 'running',
        'stations_count': len(data_simulator.stations),
        'algorithm': 'least_squares',
        'path_loss_exponent': data_simulator.path_loss_exponent,
        'center_coordinates': {
            'lat': data_simulator.geo_converter.center_lat,
            'lon': data_simulator.geo_converter.center_lon
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

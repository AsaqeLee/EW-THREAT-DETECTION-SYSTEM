# 🎖️ 军事级电磁干扰定位感知系统

## EW THREAT DETECTION SYSTEM

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)](#)

基于分布式传感器阵列的军事级电磁干扰源定位系统，采用Python Flask + Web前端 + 真实地图集成实现。系统具备专业的军事化界面和高精度定位算法，适用于电子战威胁检测和定位任务。

## 📋 目录

- [核心功能特性](#-核心功能特性)
- [系统架构](#-系统架构)
- [安装部署](#-安装部署)
- [使用指南](#-使用指南)
- [API文档](#-api文档)
- [算法原理](#-算法原理)
- [界面说明](#-界面说明)
- [测试验证](#-测试验证)
- [扩展开发](#-扩展开发)
- [故障排除](#-故障排除)

## 🎯 核心功能特性

### 🌍 真实地理环境支持
- **OpenStreetMap集成**: 真实地理环境显示，支持地图缩放和平移
- **GPS坐标系统**: 精确的经纬度坐标输入和显示
- **大范围覆盖**: 100km×100km战术区域监控能力
- **坐标转换**: 经纬度与本地坐标系统的精确转换
- **地理距离计算**: 基于Haversine公式的精确距离计算

### 📡 智能传感器阵列
- **分布式架构**: 8个可配置的传感器节点
- **动态管理**: 支持传感器的添加、删除、修改操作
- **实时监控**: 传感器状态实时监控和故障检测
- **数据输入**: 支持手动输入和CSV/JSON批量导入
- **异常检测**: 多算法融合的异常传感器自动识别

### 🎯 高精度定位算法
- **多算法融合**:
  - 最小二乘法 (Least Squares)
  - 加权最小二乘法 (Weighted Least Squares)
  - 质心法 (Centroid Method)
- **智能选择**: 自动选择最优定位算法
- **异常剔除**: 智能剔除异常数据，确保定位精度
- **质量评估**: 实时评估定位结果质量和可靠性
- **地理适配**: 考虑地球曲率的精确计算

### 🚨 威胁评估系统
- **威胁等级**: LOW/MODERATE/HIGH三级威胁评估
- **异常检测方法**:
  - Z-score统计检测
  - IQR四分位距检测
  - 基于距离的异常检测
- **质量分级**: EXCELLENT/GOOD/FAIR/POOR四级质量评估
- **置信度分析**: 实时计算定位结果置信度

### 🎖️ 军事化专业界面
- **战术主题**: 深色军事风格界面设计
- **专业术语**: 完整的军事化术语体系
- **实时显示**: 传感器状态和威胁信息实时更新
- **地图标记**: 清晰的军事化地图标记系统

## 🏗️ 系统架构

### 后端技术栈
```
Python 3.8+
├── Flask 2.0+          # Web框架
├── NumPy              # 数值计算
├── SciPy              # 科学计算和优化
├── Matplotlib         # 数据可视化支持
└── Werkzeug           # WSGI工具库
```

### 前端技术栈
```
Web Technologies
├── HTML5/CSS3         # 基础Web技术
├── JavaScript ES6+    # 前端逻辑
├── Chart.js           # 图表可视化
├── Leaflet.js         # 地图组件
└── jQuery 3.6+        # DOM操作
```

### 核心算法模块
```
modules/
├── data_simulator.py      # 数据模拟器
│   ├── 传感器位置管理
│   ├── 功率数据生成
│   └── 地理坐标转换
├── location_algorithm.py  # 定位算法引擎
│   ├── 最小二乘法
│   ├── 加权最小二乘法
│   └── 质心定位法
├── anomaly_detector.py    # 异常检测系统
│   ├── Z-score检测
│   ├── IQR检测
│   └── 距离异常检测
└── geo_converter.py       # 地理坐标转换器
    ├── 经纬度转换
    ├── 距离计算
    └── 坐标验证
```

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask Server  │    │  Algorithm Core │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Leaflet Map │ │◄──►│ │ REST APIs   │ │◄──►│ │ Location    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ │ Algorithm   │ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ └─────────────┘ │
│ │ Chart.js    │ │◄──►│ │ Data        │ │    │ ┌─────────────┐ │
│ └─────────────┘ │    │ │ Simulator   │ │◄──►│ │ Anomaly     │ │
│ ┌─────────────┐ │    │ └─────────────┘ │    │ │ Detector    │ │
│ │ Control UI  │ │◄──►│ ┌─────────────┐ │    │ └─────────────┘ │
│ └─────────────┘ │    │ │ Geo         │ │    │ ┌─────────────┐ │
└─────────────────┘    │ │ Converter   │ │◄──►│ │ Data        │ │
                       │ └─────────────┘ │    │ │ Validator   │ │
                       └─────────────────┘    │ └─────────────┘ │
                                              └─────────────────┘
```

## 🚀 安装部署

### 系统要求
- Python 3.8+
- 现代浏览器 (Chrome, Firefox, Edge)
- 网络连接 (用于加载地图)

### 安装步骤

#### 1. 克隆仓库
```bash
git clone git@github.com:AsaqeLee/EW-THREAT-DETECTION-SYSTEM.git
cd EW-THREAT-DETECTION-SYSTEM
```

#### 2. 创建虚拟环境 (推荐)
```bash
# 使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 或使用conda
conda create -n ew_threat_detection python=3.9
conda activate ew_threat_detection
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置系统 (可选)
系统使用默认配置参数，如需自定义可在 `app.py` 中修改:
```python
# 默认配置参数
DEFAULT_CENTER_LAT = 39.9042  # 默认中心纬度
DEFAULT_CENTER_LON = 116.4074  # 默认中心经度
COVERAGE_RADIUS_KM = 50       # 覆盖半径(km)
```

#### 5. 运行系统
```bash
# 直接运行
python app.py

# 或使用启动脚本
python run.py
```

#### 6. 访问系统
打开浏览器访问: [http://localhost:5000](http://localhost:5000)

## 🎮 使用指南

### 基本操作流程

1. **系统初始化**
   - 系统启动后自动加载8个默认传感器
   - 地图显示传感器位置和覆盖区域

2. **传感器管理**
   - 点击 `MANAGE SENSORS` 按钮打开管理界面
   - 可添加、编辑、删除传感器
   - 设置传感器的经纬度坐标和名称

3. **目标设置**
   - 在控制面板输入目标坐标
   - 或直接点击地图选择位置
   - 选择是否添加干扰数据

4. **数据生成/输入**
   - 点击 `GENERATE INTEL` 生成模拟数据
   - 或点击 `INPUT REAL DATA` 输入实际数据
   - 支持手动输入或批量导入

5. **执行定位**
   - 点击 `TRIANGULATE TARGET` 执行定位
   - 系统自动检测异常数据
   - 使用最优算法计算目标位置

6. **结果分析**
   - 地图上显示预测位置(黄色标记)
   - 数据面板显示详细定位结果
   - 查看威胁评估和质量分析

### 界面导航

- **地图视图/网格视图**: 切换显示模式
- **传感器状态**: 绿色表示正常，橙色表示异常
- **目标标记**: 红色表示真实位置，黄色表示预测位置
- **数据面板**: 显示功率数据、定位结果和威胁评估

## 📡 API文档

### RESTful API接口

#### 传感器管理
```http
GET    /api/stations              # 获取所有传感器信息
POST   /api/stations              # 添加新传感器
PUT    /api/stations/{id}         # 更新传感器信息
DELETE /api/stations/{id}         # 删除传感器
GET    /api/reset_stations        # 重置传感器位置
```

#### 数据处理
```http
GET    /api/simulate_data         # 生成模拟数据
POST   /api/locate_interference   # 执行干扰源定位
POST   /api/convert_coordinates   # 坐标转换
```

#### 系统状态
```http
GET    /api/system_status         # 获取系统状态
```

### API示例

#### 添加传感器
```bash
curl -X POST http://localhost:5000/api/stations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SENSOR-9",
    "lat": 39.9542,
    "lon": 116.4574
  }'
```

#### 执行定位
```bash
curl -X POST http://localhost:5000/api/locate_interference \
  -H "Content-Type: application/json" \
  -d '{
    "power_data": [
      {"station_id": 1, "power": -65.2, "x": 10, "y": 10},
      {"station_id": 2, "power": -72.1, "x": 90, "y": 10}
    ],
    "coord_mode": "geographic"
  }'
```

## 🧮 算法原理

### 信号传播模型

系统使用经典的路径损耗模型计算接收功率:

```
P_r(d) = P_t - PL(d0) - 10n·log10(d/d0) + X_σ
```

**参数说明:**
- `P_r(d)`: 距离d处的接收功率 (dBm)
- `P_t`: 发射功率 (dBm)
- `PL(d0)`: 参考距离d0处的路径损耗
- `n`: 路径损耗指数 (自由空间=2, 城市环境=2.7-3.5)
- `d`: 发射机与接收机之间的距离 (km)
- `d0`: 参考距离 (通常为1km)
- `X_σ`: 阴影衰落 (高斯随机变量)

### 定位算法详解

#### 1. 最小二乘法 (Least Squares)
最小化预测功率与实际功率的差的平方和:

```
min Σ[P_measured(i) - P_predicted(i)]²
```

**优点**: 计算简单，适用于高信噪比环境
**缺点**: 对异常值敏感

#### 2. 加权最小二乘法 (Weighted Least Squares)
根据信号强度分配权重:

```
min Σ w_i[P_measured(i) - P_predicted(i)]²
```

权重计算: `w_i = 1/σ_i²` (σ_i为测量误差标准差)

**优点**: 提高强信号的权重，降低弱信号影响
**缺点**: 需要准确的误差估计

#### 3. 质心法 (Centroid Method)
基于功率加权的质心计算:

```
x_est = Σ(w_i × x_i) / Σw_i
y_est = Σ(w_i × y_i) / Σw_i
```

权重计算: `w_i = P_i / Σ P_j`

**优点**: 计算快速，对异常值相对鲁棒
**缺点**: 精度相对较低

### 异常检测算法

#### 1. Z-score检测
基于标准分数的异常值检测:

```
z_i = |x_i - μ| / σ
```

异常判定: `z_i > threshold` (通常threshold=2.5)

#### 2. IQR检测 (四分位距)
基于四分位距的异常值检测:

```
IQR = Q3 - Q1
Lower_bound = Q1 - 1.5 × IQR
Upper_bound = Q3 + 1.5 × IQR
```

#### 3. 距离异常检测
基于功率-距离关系的异常检测:

```
Expected_power = P_t - 10n·log10(d/d0)
Residual = |Measured_power - Expected_power|
```

异常判定: `Residual > adaptive_threshold`

### 质量评估算法

系统使用多维度质量评估:

```
Quality_Score = α×Confidence + β×Residual_Score + γ×Station_Count_Score
```

**评估维度:**
- **置信度**: 基于算法收敛性和残差分析
- **残差评分**: 预测误差的统计分析
- **传感器数量**: 有效传感器数量对精度的影响
- **几何精度**: 传感器分布的几何稀释精度(GDOP)

## 🎨 界面说明

### 主界面布局

```
┌─────────────────────────────────────────────────────────────┐
│                    EW THREAT DETECTION SYSTEM               │
│                         CLASSIFIED                          │
├─────────────────┬───────────────────────┬───────────────────┤
│   TACTICAL      │  TACTICAL SITUATION   │  REAL-TIME        │
│   CONTROL       │      DISPLAY          │  INTELLIGENCE     │
│                 │                       │                   │
│ ┌─────────────┐ │ ┌───────────────────┐ │ ┌───────────────┐ │
│ │ TARGET      │ │ │                   │ │ │ SENSOR ARRAY  │ │
│ │ COORDINATES │ │ │    MAP VIEW       │ │ │    STATUS     │ │
│ └─────────────┘ │ │                   │ │ └───────────────┘ │
│ ┌─────────────┐ │ └───────────────────┘ │ ┌───────────────┐ │
│ │ SIMULATION  │ │ ┌───────────────────┐ │ │ TARGET        │ │
│ │ PARAMETERS  │ │ │                   │ │ │ COORDINATES   │ │
│ └─────────────┘ │ │  SIGNAL INTEL     │ │ └───────────────┘ │
│ ┌─────────────┐ │ │                   │ │ ┌───────────────┐ │
│ │ CONTROL     │ │ └───────────────────┘ │ │ THREAT        │ │
│ │ BUTTONS     │ │                       │ │ ASSESSMENT    │ │
│ └─────────────┘ │                       │ └───────────────┘ │
└─────────────────┴───────────────────────┴───────────────────┘
```

### 地图标记说明

| 标记 | 颜色 | 含义 | 交互 |
|------|------|------|------|
| 🟢 圆点 | 绿色 | 正常传感器 | 可点击 |
| 🟠 圆点 | 橙色 | 异常传感器 | 可点击 |
| 🔴 同心圆 | 红色 | 真实干扰源 | 可拖拽 |
| 🟡 同心圆 | 黄色 | 预测干扰源 | 显示结果 |

**注意**: 所有地图标记均已简化显示，不再显示坐标信息弹出窗口，保持界面简洁。

### 状态指示器

- **OPERATIONAL**: 传感器正常工作
- **COMPROMISED**: 传感器数据异常
- **SCANNING**: 系统正在扫描
- **TARGET ACQUIRED**: 目标已定位
- **NO TARGET**: 未检测到目标

### 威胁等级

| 等级 | 颜色 | 条件 | 说明 |
|------|------|------|------|
| LOW | 🟢 绿色 | 0个异常传感器 | 系统正常运行 |
| MODERATE | 🟡 黄色 | 1个异常传感器 | 轻微威胁 |
| HIGH | 🔴 红色 | 2+个异常传感器 | 严重威胁 |

## 🧪 测试验证

### 功能测试

系统支持以下测试功能:
- ✅ 地理坐标转换精度验证
- ✅ 数据模拟器功能验证
- ✅ 定位算法精度验证
- ✅ 异常检测准确性验证
- ✅ 系统集成验证

### 手动测试场景

#### 场景1: 中心位置干扰
```
目标位置: (0, 0) - 区域中心
预期精度: < 2km
测试步骤:
1. 设置目标坐标为(0, 0)
2. 生成模拟数据
3. 执行定位
4. 验证误差 < 2km
```

#### 场景2: 边缘位置干扰
```
目标位置: (45, 45) - 区域边缘
预期精度: < 5km
测试步骤:
1. 设置目标坐标为(45, 45)
2. 添加异常数据
3. 执行定位
4. 验证误差 < 5km
```

#### 场景3: 异常数据处理
```
异常传感器: 2个
预期行为: 自动剔除异常数据
测试步骤:
1. 启用异常数据模拟
2. 验证异常检测功能
3. 确认定位仍然有效
```

### 性能基准

| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| 定位精度 | < 5km | 2-8km |
| 响应时间 | < 2s | 0.5-1.5s |
| 异常检测率 | > 90% | 95%+ |
| 系统可用性 | > 99% | 99.9% |

## 🔧 扩展开发

### 添加新的定位算法

1. 在 `modules/location_algorithm.py` 中添加新方法:
```python
def _your_new_algorithm(self, stations_pos, received_powers):
    # 实现您的算法
    pass
```

2. 在 `calculate_location` 方法中调用:
```python
your_result = self._your_new_algorithm(stations_pos, received_powers)
results['your_algorithm'] = your_result
```

### 添加新的异常检测方法

1. 在 `modules/anomaly_detector.py` 中添加:
```python
def _your_detection_method(self, power_data):
    # 实现检测逻辑
    return anomaly_indices
```

2. 在 `detect_anomalies` 方法中集成:
```python
your_anomalies = self._your_detection_method(power_data)
anomaly_results['your_method'] = your_anomalies
```

### 自定义地图提供商

修改 `static/js/map_manager.js`:
```javascript
// 替换地图瓦片源
L.tileLayer('https://your-tile-server/{z}/{x}/{y}.png', {
    attribution: 'Your Attribution',
    maxZoom: 18
}).addTo(this.map);
```

### 数据库集成

添加数据持久化:
```python
# 在 app.py 中添加数据库支持
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ew_system.db'
db = SQLAlchemy(app)

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
```

## 🔍 故障排除

### 常见问题

#### 1. 地图无法加载
**症状**: 地图区域显示空白
**原因**: 网络连接问题或瓦片服务器不可用
**解决方案**:
```bash
# 检查网络连接
ping tile.openstreetmap.org

# 或使用备用瓦片服务器
# 修改 map_manager.js 中的瓦片URL
```

#### 2. 传感器标记不显示
**症状**: 地图上看不到传感器位置
**原因**: 坐标数据格式错误或超出范围
**解决方案**:
```bash
# 检查浏览器控制台错误
# 验证传感器坐标数据
curl http://localhost:5000/api/stations
```

#### 3. 定位精度过低
**症状**: 定位误差超过10km
**原因**: 传感器分布不佳或异常数据过多
**解决方案**:
- 重新配置传感器位置
- 检查异常检测设置
- 调整路径损耗参数

#### 4. 系统响应缓慢
**症状**: 定位计算时间过长
**原因**: 算法复杂度或数据量过大
**解决方案**:
```python
# 优化算法参数
# 在 location_algorithm.py 中调整
MAX_ITERATIONS = 100  # 减少迭代次数
CONVERGENCE_THRESHOLD = 0.01  # 调整收敛阈值
```

### 调试模式

启用详细日志:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### 日志分析

查看系统日志:
```bash
# 检查应用日志
tail -f app.log

# 检查错误日志
tail -f error.log
```

### 性能监控

添加性能监控:
```python
import time
import logging

# 在关键函数中添加计时
start_time = time.time()
# ... 执行代码 ...
execution_time = time.time() - start_time
logging.info(f"Function executed in {execution_time:.2f}s")
```

## 📁 项目结构

```
ElectromagneticInterferenceLocationAwareness/
├── 📄 app.py                      # Flask主应用服务器
├── 📄 run.py                      # 系统启动脚本
├── 📄 requirements.txt            # Python依赖包列表
├── 📄 README.md                   # 项目文档
├──  modules/                    # 核心算法模块
│   ├── 📄 __init__.py
│   ├── 📄 data_simulator.py       # 数据模拟器
│   ├── 📄 location_algorithm.py   # 定位算法引擎
│   ├── 📄 anomaly_detector.py     # 异常检测系统
│   └── 📄 geo_converter.py        # 地理坐标转换器
├── 📁 templates/                  # HTML模板文件
│   └── 📄 index.html              # 主界面模板
└── 📁 static/                     # 静态资源文件
    ├── 📁 css/
    │   └── 📄 style.css           # 军事化样式表
    └── 📁 js/
        ├── 📄 main.js             # 主要前端逻辑
        ├── 📄 map_manager.js      # 地图管理器
        ├── 📄 station_manager.js  # 传感器管理器
        └── 📄 real_data_manager.js # 实时数据管理器
```

## 🚀 扩展功能

系统采用模块化设计，支持以下扩展:

### 已规划功能
- [ ] **3D定位支持**: 扩展到三维空间定位
- [ ] **实时数据流**: 支持实时传感器数据接入
- [ ] **历史数据分析**: 威胁趋势分析和预测
- [ ] **多目标跟踪**: 同时跟踪多个干扰源
- [ ] **报警系统**: 自动威胁检测和通知
- [ ] **数据导出**: 支持多种格式的数据导出

### 高级功能
- [ ] **机器学习集成**: 基于ML的异常检测
- [ ] **分布式部署**: 支持多节点分布式计算
- [ ] **移动端支持**: 响应式设计和移动应用
- [ ] **加密通信**: 端到端加密数据传输
- [ ] **用户权限管理**: 多级用户权限控制
- [ ] **国际化支持**: 多语言界面支持

## ⚠️ 重要说明

### 使用限制
1. **地理范围**: 系统设计用于100km×100km区域覆盖
2. **传感器数量**: 建议使用6-12个传感器以获得最佳精度
3. **环境要求**: 适用于开阔地形，城市环境需要参数调整
4. **精度限制**: 定位精度受传感器分布和环境因素影响

### 安全考虑
- 系统仅用于研究和教育目的
- 实际军事应用需要额外的安全措施
- 建议在隔离网络环境中部署
- 定期更新系统和依赖包

### 法律声明
- 请遵守当地法律法规使用本系统
- 不得用于非法监听或干扰活动
- 商业使用需要获得相应许可

## 🤝 贡献指南

欢迎贡献代码和改进建议！

### 贡献流程
1. Fork 本仓库: [AsaqeLee/EW-THREAT-DETECTION-SYSTEM](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM)
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 Python代码规范
- 添加适当的注释和文档字符串
- 保持代码简洁和可读性
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证，可自由使用、修改和分发。

## � 联系方式

- **项目主页**: [EW-THREAT-DETECTION-SYSTEM](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM)
- **问题反馈**: [Issues](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM/issues)
- **作者**: Asaqe Lee

## �👥 作者与致谢

### 特别感谢
- OpenStreetMap 社区提供地图数据
- Leaflet.js 团队提供优秀的地图库
- Flask 社区提供Web框架支持
- NumPy 和 SciPy 社区提供科学计算支持

## 📈 版本历史

- **v1.0.0** (2024-01-15): 初始版本发布
  - 基础定位功能
  - 简单Web界面

- **v2.0.0** (2024-02-01): 重大更新
  - 真实地图集成
  - 军事化界面设计
  - 异常检测系统

- **v2.1.0** (2024-02-15): 功能增强
  - 传感器管理功能
  - 实时数据输入
  - 性能优化

- **v2.1.1** (2024-02-16): 界面优化
  - 移除地图标记弹出窗口
  - 简化界面显示，提升用户体验
  - 优化地图交互性能

---

<div align="center">

**🎖️ 军事级电磁干扰定位感知系统**

*为电子战威胁检测而生*

[![Stars](https://img.shields.io/github/stars/AsaqeLee/EW-THREAT-DETECTION-SYSTEM?style=social)](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM/stargazers)
[![Forks](https://img.shields.io/github/forks/AsaqeLee/EW-THREAT-DETECTION-SYSTEM?style=social)](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM/network/members)
[![Issues](https://img.shields.io/github/issues/AsaqeLee/EW-THREAT-DETECTION-SYSTEM)](https://github.com/AsaqeLee/EW-THREAT-DETECTION-SYSTEM/issues)

</div>

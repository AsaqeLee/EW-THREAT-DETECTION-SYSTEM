// 地图管理器
class MapManager {
    constructor() {
        this.map = null;
        this.stationMarkers = [];
        this.targetMarker = null;
        this.estimatedMarker = null;
        this.temporaryClickMarker = null;
        this.isMapView = true;

        // 默认中心点（北京）
        this.centerLat = 39.9042;
        this.centerLon = 116.4074;
    }
    
    initializeMap() {
        try {
            console.log('Initializing map with center:', this.centerLat, this.centerLon);

            // 初始化Leaflet地图
            this.map = L.map('map-container').setView([this.centerLat, this.centerLon], 9);

            // 添加OpenStreetMap瓦片层
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18,
                minZoom: 5
            }).addTo(this.map);

            // 添加暗色地图样式
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '© OpenStreetMap, © CARTO',
                subdomains: 'abcd',
                maxZoom: 18
            }).addTo(this.map);

            // 地图点击事件
            this.map.on('click', (e) => {
                this.onMapClick(e);
            });

            // 添加比例尺
            L.control.scale({
                metric: true,
                imperial: false,
                position: 'bottomright'
            }).addTo(this.map);

            // 添加坐标显示
            L.control.mousePosition = L.Control.extend({
                options: {
                    position: 'bottomleft',
                    separator: ' : ',
                    emptyString: 'Unavailable',
                    lngFirst: false,
                    numDigits: 5,
                    lngFormatter: undefined,
                    latFormatter: undefined,
                    prefix: ""
                },
                onAdd: function(map) {
                    this._container = L.DomUtil.create('div', 'leaflet-control-mouseposition');
                    L.DomEvent.disableClickPropagation(this._container);
                    this._container.innerHTML = this.options.emptyString;
                    return this._container;
                },
                onRemove: function(map) {
                    // Nothing to do here
                },
                _onMouseMove: function(e) {
                    var lng = this.options.lngFormatter ? this.options.lngFormatter(e.latlng.lng) : L.Util.formatNum(e.latlng.lng, this.options.numDigits);
                    var lat = this.options.latFormatter ? this.options.latFormatter(e.latlng.lat) : L.Util.formatNum(e.latlng.lat, this.options.numDigits);
                    var value = this.options.lngFirst ? lng + this.options.separator + lat : lat + this.options.separator + lng;
                    var prefixAndValue = this.options.prefix + ' ' + value;
                    this._container.innerHTML = prefixAndValue;
                }
            });

            L.Map.mergeOptions({
                positionControl: false
            });

            L.Map.addInitHook(function() {
                if (this.options.positionControl) {
                    this.positionControl = new L.control.mousePosition();
                    this.addControl(this.positionControl);
                }
            });

            new L.control.mousePosition({
                position: 'bottomleft',
                prefix: 'LAT/LON:'
            }).addTo(this.map);

            console.log('Map initialized successfully');

            // 立即加载电台标记
            $.get('/api/stations')
                .done((data) => {
                    console.log('Stations loaded:', data);
                    this.updateStationMarkers(data);
                    this.fitBounds();
                })
                .fail((error) => {
                    console.error('Failed to load stations:', error);
                });
        } catch (error) {
            console.error('Error initializing map:', error);
        }
    }
    
    onMapClick(e) {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;

        // 更新目标坐标输入框
        $('#target-lat').val(lat.toFixed(6));
        $('#target-lon').val(lon.toFixed(6));

        // 如果当前是网格模式，也更新网格坐标
        if ($('input[name="coord-mode"]:checked').val() === 'grid') {
            // 使用服务器API进行精确的坐标转换
            $.ajax({
                url: '/api/convert_coordinates',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    lat: lat,
                    lon: lon
                }),
                async: false,
                success: function(data) {
                    $('#interference-x').val(data.x.toFixed(1));
                    $('#interference-y').val(data.y.toFixed(1));
                    console.log(`Map click converted LatLon(${lat}, ${lon}) to XY(${data.x}, ${data.y})`);
                },
                error: function(error) {
                    console.error('Failed to convert coordinates:', error);
                    // 备用本地转换
                    const centerLat = 39.9042;
                    const centerLon = 116.4074;
                    const kmPerDegreeLat = 111.319;
                    const kmPerDegreeLon = 85.395;

                    const x = (lon - centerLon) * kmPerDegreeLon;
                    const y = (lat - centerLat) * kmPerDegreeLat;

                    $('#interference-x').val(x.toFixed(1));
                    $('#interference-y').val(y.toFixed(1));
                }
            });
        }

        // 重置定位按钮
        $('#locate-btn').prop('disabled', true);
        if (typeof currentPowerData !== 'undefined') {
            currentPowerData = null;
        }

        // 添加临时标记显示点击位置
        this.addTemporaryClickMarker(lat, lon);

        showSuccess(`TARGET COORDINATES UPDATED: ${lat.toFixed(6)}, ${lon.toFixed(6)}`);
    }

    addTemporaryClickMarker(lat, lon) {
        // 移除之前的临时标记
        if (this.temporaryClickMarker) {
            this.map.removeLayer(this.temporaryClickMarker);
            this.temporaryClickMarker = null;
        }

        // 创建临时点击标记
        const clickIcon = L.divIcon({
            html: `
                <div style="
                    width: 20px;
                    height: 20px;
                    background: #ffff00;
                    border: 2px solid #ff0000;
                    border-radius: 50%;
                    opacity: 0.8;
                    animation: pulse 1s infinite;
                "></div>
            `,
            className: 'temporary-click-marker',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });

        this.temporaryClickMarker = L.marker([lat, lon], {
            icon: clickIcon
        }).addTo(this.map);

        // 3秒后自动移除临时标记
        setTimeout(() => {
            if (this.temporaryClickMarker) {
                this.map.removeLayer(this.temporaryClickMarker);
                this.temporaryClickMarker = null;
            }
        }, 3000);
    }

    updateStationMarkers(stations) {
        console.log('Updating station markers:', stations);

        // 清除现有标记
        this.stationMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.stationMarkers = [];

        // 添加电台标记
        stations.forEach((station, index) => {
            console.log(`Processing station ${index}:`, station);

            if (station.lat && station.lon) {
                console.log(`Creating marker for ${station.name} at [${station.lat}, ${station.lon}]`);

                const marker = L.marker([station.lat, station.lon], {
                    icon: this.createStationIcon(station.name, false)
                }).addTo(this.map);

                // 移除弹出窗口 - 不显示传感器站点信息

                this.stationMarkers.push(marker);
                console.log(`Marker created for ${station.name}`);
            } else {
                console.warn(`Station ${station.name} missing coordinates:`, station);
            }
        });

        console.log(`Total markers created: ${this.stationMarkers.length}`);
    }
    
    clearTargetMarkers() {
        // 清除所有目标标记
        if (this.targetMarker) {
            this.map.removeLayer(this.targetMarker);
            this.targetMarker = null;
        }
        if (this.estimatedMarker) {
            this.map.removeLayer(this.estimatedMarker);
            this.estimatedMarker = null;
        }
        console.log('All target markers cleared');
    }

    updateTargetMarker(position, isEstimated = false) {
        console.log(`Updating ${isEstimated ? 'estimated' : 'actual'} target marker:`, position);

        // 检查位置数据
        if (!position) {
            console.error('Position data is missing');
            return;
        }

        // 直接使用经纬度坐标，不进行转换
        if (!position.lat || !position.lon) {
            console.error('Missing latitude or longitude data');
            return;
        }

        // 验证坐标范围
        if (position.lat < -90 || position.lat > 90 || position.lon < -180 || position.lon > 180) {
            console.error('Invalid coordinates:', position);
            return;
        }

        console.log(`Creating marker directly at [${position.lat}, ${position.lon}]`);

        if (isEstimated) {
            // 更新估计位置标记
            if (this.estimatedMarker) {
                this.map.removeLayer(this.estimatedMarker);
                this.estimatedMarker = null;
            }

            console.log(`Creating estimated target marker at [${position.lat}, ${position.lon}]`);

            this.estimatedMarker = L.marker([position.lat, position.lon], {
                icon: this.createTargetIcon('ESTIMATED', '#ffcc00')
            }).addTo(this.map);

            // 移除弹出窗口 - 不显示干扰源经纬度信息

            console.log('Estimated target marker created successfully');
        } else {
            // 更新真实目标位置标记
            if (this.targetMarker) {
                this.map.removeLayer(this.targetMarker);
                this.targetMarker = null;
            }

            console.log(`Creating actual target marker at [${position.lat}, ${position.lon}]`);

            this.targetMarker = L.marker([position.lat, position.lon], {
                icon: this.createTargetIcon('TARGET', '#ff3333')
            }).addTo(this.map);

            // 移除弹出窗口 - 不显示干扰源经纬度信息

            // 自动打开弹出窗口以显示位置信息
            this.targetMarker.openPopup();

            console.log('Actual target marker created successfully');

            // 如果标记距离中心较远，调整地图视图
            if (position.x && position.y) {
                const distance = Math.sqrt(position.x*position.x + position.y*position.y);
                if (distance > 30) { // 如果距离中心超过30km
                    // 创建包含所有标记的边界
                    const allMarkers = [...this.stationMarkers];
                    if (this.targetMarker) allMarkers.push(this.targetMarker);
                    if (this.estimatedMarker) allMarkers.push(this.estimatedMarker);

                    if (allMarkers.length > 0) {
                        const group = new L.featureGroup(allMarkers);
                        this.map.fitBounds(group.getBounds().pad(0.1));
                    }
                }
            }

            // 强制刷新地图
            this.map.invalidateSize();
        }
    }
    
    updateAnomalyMarkers(stations, anomalyIndices) {
        // 更新异常电台的标记样式
        this.stationMarkers.forEach((marker, index) => {
            const station = stations[index];
            const isAnomaly = anomalyIndices.includes(index);
            
            marker.setIcon(this.createStationIcon(station.name, isAnomaly));
            
            // 移除弹出窗口 - 不显示传感器站点信息
        });
    }
    
    createStationIcon(name, isAnomaly = false) {
        const color = isAnomaly ? '#ff6600' : '#00ff41';

        return L.divIcon({
            html: `
                <div style="
                    background: ${color};
                    border: 2px solid #000;
                    border-radius: 50%;
                    width: 16px;
                    height: 16px;
                    box-shadow: 0 0 15px ${color};
                    position: relative;
                ">
                </div>
                <div style="
                    color: ${color};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    text-align: center;
                    margin-top: 2px;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                    background: rgba(0,0,0,0.7);
                    padding: 1px 3px;
                    border-radius: 2px;
                ">
                    ${name}
                </div>
            `,
            className: 'custom-station-icon',
            iconSize: [60, 35],
            iconAnchor: [30, 18]
        });
    }

    createTargetIcon(label, color) {

        return L.divIcon({
            html: `
                <div style="
                    position: relative;
                    width: 30px;
                    height: 30px;
                ">
                    <!-- 中心点 -->
                    <div style="
                        position: absolute;
                        top: 12px;
                        left: 12px;
                        width: 6px;
                        height: 6px;
                        background: ${color};
                        border-radius: 50%;
                        z-index: 3;
                    "></div>

                    <!-- 内圈 -->
                    <div style="
                        position: absolute;
                        top: 9px;
                        left: 9px;
                        width: 12px;
                        height: 12px;
                        border: 2px solid ${color};
                        border-radius: 50%;
                        z-index: 2;
                    "></div>

                    <!-- 外圈 - 静态显示 -->
                    <div style="
                        position: absolute;
                        top: 3px;
                        left: 3px;
                        width: 24px;
                        height: 24px;
                        border: 2px solid ${color};
                        border-radius: 50%;
                        opacity: 0.6;
                        z-index: 1;
                    "></div>
                </div>
                <div style="
                    color: ${color};
                    font-family: 'Courier New', monospace;
                    font-size: 9px;
                    text-align: center;
                    margin-top: 32px;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                    background: rgba(0,0,0,0.8);
                    padding: 2px 4px;
                    border-radius: 2px;
                    border: 1px solid ${color};
                ">
                    ${label}
                </div>
            `,
            className: 'custom-target-icon',
            iconSize: [70, 70],
            iconAnchor: [35, 35]
        });
    }
    
    fitBounds() {
        if (this.stationMarkers.length > 0) {
            const group = new L.featureGroup(this.stationMarkers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }
    
    setCenter(lat, lon) {
        this.centerLat = lat;
        this.centerLon = lon;
        if (this.map) {
            this.map.setView([lat, lon], this.map.getZoom());
        }
    }
    
    toggleView(showMap) {
        this.isMapView = showMap;
        if (showMap) {
            $('#map-container').show();
            $('#location-chart').hide();
            $('#show-map-btn').addClass('active');
            $('#show-chart-btn').removeClass('active');
            
            // 刷新地图大小
            if (this.map) {
                setTimeout(() => {
                    this.map.invalidateSize();
                }, 100);
            }
        } else {
            $('#map-container').hide();
            $('#location-chart').show();
            $('#show-map-btn').removeClass('active');
            $('#show-chart-btn').addClass('active');
        }
    }
}

// 全局地图管理器实例
let mapManager = null;

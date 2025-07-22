// 全局变量
let locationChart = null;
let powerChart = null;
let currentPowerData = null;
let stationsInfo = null;

// 页面加载完成后初始化
$(document).ready(function() {
    // 初始化管理器
    mapManager = new MapManager();
    stationManager = new StationManager();
    realDataManager = new RealDataManager();

    initializeCharts();
    loadStationsInfo();
    bindEvents();
    updateSystemStatus();

    // 初始化地图
    mapManager.initializeMap();

    // 初始化电台管理器
    stationManager.initialize();

    // 初始化实时数据管理器
    realDataManager.initialize();

    // 默认显示地图视图
    mapManager.toggleView(true);
});

// 初始化图表
function initializeCharts() {
    // 位置图表
    const locationCtx = document.getElementById('location-chart').getContext('2d');
    locationChart = new Chart(locationCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'SENSOR ARRAY',
                data: [],
                backgroundColor: 'rgba(0, 255, 65, 0.8)',
                borderColor: 'rgba(0, 255, 65, 1)',
                pointRadius: 8,
                pointHoverRadius: 10
            }, {
                label: 'ACTUAL TARGET',
                data: [],
                backgroundColor: 'rgba(255, 51, 51, 0.9)',
                borderColor: 'rgba(255, 51, 51, 1)',
                pointRadius: 12,
                pointHoverRadius: 14,
                pointStyle: 'triangle'
            }, {
                label: 'ESTIMATED TARGET',
                data: [],
                backgroundColor: 'rgba(255, 204, 0, 0.9)',
                borderColor: 'rgba(255, 204, 0, 1)',
                pointRadius: 12,
                pointHoverRadius: 14,
                pointStyle: 'star'
            }, {
                label: 'COMPROMISED SENSORS',
                data: [],
                backgroundColor: 'rgba(255, 102, 0, 0.8)',
                borderColor: 'rgba(255, 102, 0, 1)',
                pointRadius: 8,
                pointHoverRadius: 10,
                pointStyle: 'cross'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: -120,
                    max: 120,
                    title: {
                        display: true,
                        text: 'X-COORDINATE',
                        color: '#00ff41',
                        font: {
                            family: "'Courier New', monospace",
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        color: '#00ff41',
                        font: {
                            family: "'Courier New', monospace"
                        }
                    },
                    grid: {
                        color: 'rgba(0, 255, 65, 0.1)'
                    }
                },
                y: {
                    min: -120,
                    max: 120,
                    title: {
                        display: true,
                        text: 'Y-COORDINATE',
                        color: '#00ff41',
                        font: {
                            family: "'Courier New', monospace",
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        color: '#00ff41',
                        font: {
                            family: "'Courier New', monospace"
                        }
                    },
                    grid: {
                        color: 'rgba(0, 255, 65, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.parsed;
                            const dataset = context.dataset;
                            return `${dataset.label}: (${point.x.toFixed(1)}, ${point.y.toFixed(1)})`;
                        }
                    }
                }
            }
        }
    });

    // 功率图表
    const powerCtx = document.getElementById('power-chart').getContext('2d');
    powerChart = new Chart(powerCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: '接收功率 (dBm)',
                data: [],
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: '功率 (dBm)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
}

// 加载电台信息
function loadStationsInfo() {
    $.get('/api/stations')
        .done(function(data) {
            stationsInfo = data;
            updateLocationChart();
            // 更新地图上的电台标记
            if (mapManager && mapManager.map) {
                mapManager.updateStationMarkers(data);
                mapManager.fitBounds();
            }
        })
        .fail(function() {
            showError('无法加载电台信息');
        });
}

// 绑定事件
function bindEvents() {
    $('#simulate-btn').click(simulateData);
    $('#locate-btn').click(locateInterference);
    $('#reset-stations-btn').click(resetStationsPositions);

    // 输入框变化时重置定位按钮
    $('#interference-x, #interference-y, #target-lat, #target-lon, #add-anomaly, #path-loss-exponent').change(function() {
        $('#locate-btn').prop('disabled', true);
        currentPowerData = null;
    });

    // 图表点击事件 - 允许用户点击图表来设置干扰源位置
    if (locationChart) {
        locationChart.canvas.addEventListener('click', function(event) {
            const canvasPosition = Chart.helpers.getRelativePosition(event, locationChart);
            const dataX = locationChart.scales.x.getValueForPixel(canvasPosition.x);
            const dataY = locationChart.scales.y.getValueForPixel(canvasPosition.y);

            if (dataX >= -120 && dataX <= 120 && dataY >= -120 && dataY <= 120) {
                // 切换到网格坐标模式
                $('input[name="coord-mode"][value="grid"]').prop('checked', true);
                stationManager.toggleCoordinateMode();

                $('#interference-x').val(dataX.toFixed(1));
                $('#interference-y').val(dataY.toFixed(1));
                $('#locate-btn').prop('disabled', true);
                currentPowerData = null;
                showSuccess('TARGET COORDINATES UPDATED');
            }
        });
    }

    // 地图/图表切换按钮
    $('#show-map-btn').click(function() {
        mapManager.toggleView(true);
    });

    $('#show-chart-btn').click(function() {
        mapManager.toggleView(false);
    });
}

// 模拟数据生成
function simulateData() {
    const coordMode = $('input[name="coord-mode"]:checked').val();
    const addAnomaly = $('#add-anomaly').is(':checked');
    const pathLossExponent = parseFloat($('#path-loss-exponent').val());

    let requestParams = {
        coord_mode: coordMode,
        add_anomaly: addAnomaly,
        path_loss_exponent: pathLossExponent
    };

    if (coordMode === 'geographic') {
        const targetLat = parseFloat($('#target-lat').val());
        const targetLon = parseFloat($('#target-lon').val());

        if (isNaN(targetLat) || isNaN(targetLon)) {
            showError('请输入有效的经纬度坐标');
            return;
        }

        console.log(`Geographic mode: Using coordinates LAT=${targetLat}, LON=${targetLon}`);
        requestParams.target_lat = targetLat;
        requestParams.target_lon = targetLon;
    } else {
        const interferenceX = parseFloat($('#interference-x').val());
        const interferenceY = parseFloat($('#interference-y').val());

        if (isNaN(interferenceX) || isNaN(interferenceY)) {
            showError('请输入有效的网格坐标');
            return;
        }

        console.log(`Grid mode: Using coordinates X=${interferenceX}, Y=${interferenceY}`);
        requestParams.interference_x = interferenceX;
        requestParams.interference_y = interferenceY;
    }

    if (isNaN(pathLossExponent) || pathLossExponent < 1.0 || pathLossExponent > 5.0) {
        showError('路径损耗指数应在1.0-5.0之间');
        return;
    }

    // 添加时间戳防止缓存
    requestParams._t = Date.now();

    $('#simulate-btn').prop('disabled', true).text('GENERATING...');

    $.get('/api/simulate_data', requestParams)
    .done(function(data) {
        currentPowerData = data;
        updatePowerChart(data.power_data);
        updateLocationChart(data.interference_position);
        updatePowerDataDisplay(data.power_data);

        // 清除旧的目标标记
        if (mapManager && mapManager.map) {
            mapManager.clearTargetMarkers();
        }

        // 更新地图上的目标标记
        if (mapManager && mapManager.map && data.interference_position) {
            console.log('=== UPDATING TARGET MARKER ===');
            console.log('Interference position data:', data.interference_position);
            console.log('Map manager exists:', !!mapManager);
            console.log('Map exists:', !!mapManager.map);
            // 直接使用后端返回的经纬度坐标
            const position = {
                lat: data.interference_position.lat,
                lon: data.interference_position.lon,
                x: data.interference_position.x,
                y: data.interference_position.y
            };

            console.log('Using direct coordinates from server:', position);

            mapManager.updateTargetMarker(position, false);

            // 强制刷新地图视图
            setTimeout(() => {
                if (mapManager.map) {
                    mapManager.map.invalidateSize();
                }
            }, 100);
        }

        $('#locate-btn').prop('disabled', false);
        showSuccess('INTELLIGENCE DATA GENERATED');
    })
    .fail(function() {
        showError('数据生成失败');
    })
    .always(function() {
        $('#simulate-btn').prop('disabled', false).text('GENERATE INTEL');
    });
}

// 定位干扰源
function locateInterference() {
    if (!currentPowerData) {
        showError('请先生成模拟数据');
        return;
    }
    
    $('#locate-btn').prop('disabled', true).text('TRIANGULATING...');
    
    const coordMode = $('input[name="coord-mode"]:checked').val();

    $.ajax({
        url: '/api/locate_interference',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            power_data: currentPowerData.power_data,
            coord_mode: coordMode
        })
    })
    .done(function(data) {
        updateLocationResult(data);
        updateAnomalyResult(data.anomaly_detection);
        updateLocationChart(currentPowerData.interference_position, data.location.position, data.anomaly_detection.anomaly_indices);

        // 更新地图上的估计位置标记
        if (mapManager && mapManager.map && data.location.position) {
            console.log('Updating estimated target marker with position:', data.location.position);

            // 直接使用定位算法返回的经纬度坐标
            const position = {
                lat: data.location.position.lat,
                lon: data.location.position.lon,
                x: data.location.position.x,
                y: data.location.position.y
            };

            console.log('Using direct coordinates from location algorithm:', position);

            mapManager.updateTargetMarker(position, true);

            if (currentPowerData && currentPowerData.power_data) {
                console.log('Updating anomaly markers');
                mapManager.updateAnomalyMarkers(currentPowerData.power_data, data.anomaly_detection.anomaly_indices);
            }
        }

        showSuccess('TARGET TRIANGULATION COMPLETE');
    })
    .fail(function() {
        showError('定位失败');
    })
    .always(function() {
        $('#locate-btn').prop('disabled', false).text('TRIANGULATE TARGET');
    });
}

// 更新位置图表
function updateLocationChart(truePosition = null, estimatedPosition = null, anomalyIndices = []) {
    if (!stationsInfo) return;
    
    // 更新电台位置
    const normalStations = [];
    const anomalyStations = [];
    
    stationsInfo.forEach((station, index) => {
        const point = {x: station.x, y: station.y, label: station.name};
        if (anomalyIndices.includes(index)) {
            anomalyStations.push(point);
        } else {
            normalStations.push(point);
        }
    });
    
    locationChart.data.datasets[0].data = normalStations;
    locationChart.data.datasets[3].data = anomalyStations;
    
    // 更新真实干扰源位置
    if (truePosition) {
        locationChart.data.datasets[1].data = [{
            x: truePosition.x,
            y: truePosition.y,
            label: '真实位置'
        }];
    }
    
    // 更新估计干扰源位置
    if (estimatedPosition) {
        locationChart.data.datasets[2].data = [{
            x: estimatedPosition.x,
            y: estimatedPosition.y,
            label: '估计位置'
        }];
    }
    
    locationChart.update();
}

// 更新功率图表
function updatePowerChart(powerData) {
    const labels = powerData.map(d => d.station_name);
    const powers = powerData.map(d => d.power);
    const colors = powerData.map(d => d.is_anomaly ? 'rgba(255, 206, 86, 0.8)' : 'rgba(102, 126, 234, 0.8)');
    
    powerChart.data.labels = labels;
    powerChart.data.datasets[0].data = powers;
    powerChart.data.datasets[0].backgroundColor = colors;
    powerChart.update();
}

// 更新功率数据显示
function updatePowerDataDisplay(powerData) {
    let html = '<table style="width: 100%; font-size: 0.85em; border-collapse: collapse;">';
    html += '<tr style="border-bottom: 1px solid #00ff41;"><th style="color: #00ff41; padding: 5px;">SENSOR</th><th style="color: #00ff41; padding: 5px;">SIGNAL(dBm)</th><th style="color: #00ff41; padding: 5px;">STATUS</th></tr>';

    powerData.forEach(station => {
        const status = station.is_anomaly ?
            '<span style="color: #ff6600; font-weight: bold;">COMPROMISED</span>' :
            '<span style="color: #00ff41; font-weight: bold;">OPERATIONAL</span>';
        const powerColor = station.is_anomaly ? '#ff6600' : '#00ff41';
        html += `<tr style="border-bottom: 1px solid rgba(0,255,65,0.2);">
                    <td style="padding: 3px; color: ${powerColor};">${station.station_name.replace('电台', 'SENSOR-')}</td>
                    <td style="padding: 3px; color: ${powerColor}; text-align: center;">${station.power}</td>
                    <td style="padding: 3px;">${status}</td>
                 </tr>`;
    });

    html += '</table>';
    $('#power-data-display').html(html);
}

// 更新定位结果显示
function updateLocationResult(data) {
    const location = data.location;
    const quality = location.quality_assessment || {};

    let html = `
        <div style="color: #00ff41; margin-bottom: 8px;"><strong>TARGET COORDINATES:</strong></div>
        <div style="margin-left: 10px; color: #ffcc00;">X: ${location.position.x.toFixed(2)} | Y: ${location.position.y.toFixed(2)}</div>
        <div style="color: #00ff41; margin: 8px 0;"><strong>CONFIDENCE:</strong> <span style="color: ${location.confidence > 70 ? '#00ff41' : location.confidence > 50 ? '#ffcc00' : '#ff3333'}">${location.confidence.toFixed(1)}%</span></div>
        <div style="color: #00ff41;"><strong>ALGORITHM:</strong> ${location.method_used.toUpperCase()}</div>
        <div style="color: #00ff41;"><strong>ERROR MARGIN:</strong> ${location.residual.toFixed(2)}</div>
        <div style="color: #00ff41;"><strong>ACTIVE SENSORS:</strong> ${location.valid_stations_count}/8</div>
    `;

    if (location.excluded_stations > 0) {
        html += `<div style="color: #ff6600;"><strong>COMPROMISED:</strong> ${location.excluded_stations} SENSORS</div>`;
    }

    if (quality.quality) {
        const qualityColor = quality.quality === 'EXCELLENT' ? '#00ff41' :
                           quality.quality === 'GOOD' ? '#ffcc00' : '#ff6600';
        html += `<div style="color: ${qualityColor}; margin-top: 8px;"><strong>ASSESSMENT:</strong> ${quality.quality}</div>`;
    }

    $('#location-result-display').html(html);
}

// 更新异常检测结果显示
function updateAnomalyResult(anomalyData) {
    const threatLevel = anomalyData.anomaly_indices.length === 0 ? 'LOW' :
                      anomalyData.anomaly_indices.length === 1 ? 'MODERATE' : 'HIGH';
    const threatColor = threatLevel === 'LOW' ? '#00ff41' :
                      threatLevel === 'MODERATE' ? '#ffcc00' : '#ff3333';

    let html = `
        <div style="color: ${threatColor}; font-weight: bold; margin-bottom: 8px;">THREAT LEVEL: ${threatLevel}</div>
        <div style="color: #00ff41;"><strong>DETECTION METHOD:</strong> ${anomalyData.detection_method.toUpperCase()}</div>
        <div style="color: ${anomalyData.anomaly_indices.length > 0 ? '#ff6600' : '#00ff41'};"><strong>COMPROMISED SENSORS:</strong> ${anomalyData.anomaly_indices.length}</div>
        <div style="color: #00ff41;"><strong>OPERATIONAL SENSORS:</strong> ${anomalyData.normal_indices.length}</div>
    `;

    if (anomalyData.anomaly_details.length > 0) {
        html += '<div style="color: #00ff41; margin-top: 8px;"><strong>THREAT DETAILS:</strong></div>';
        anomalyData.anomaly_details.forEach(detail => {
            const anomalyType = detail.anomaly_type === 'high_power' ? 'SIGNAL AMPLIFICATION' :
                              detail.anomaly_type === 'low_power' ? 'SIGNAL SUPPRESSION' : 'SIGNAL CORRUPTION';
            html += `<div style="margin-left: 10px; color: #ff6600;">• ${detail.station_name.replace('电台', 'SENSOR-')}: ${anomalyType} (${detail.confidence}%)</div>`;
        });
    }

    $('#anomaly-result-display').html(html);
}

// 更新系统状态
function updateSystemStatus() {
    $.get('/api/system_status')
        .done(function(data) {
            $('#system-status').html(`系统状态: <span class="status-indicator status-normal"></span>${data.status}`);
            $('#last-update').text(`最后更新: ${new Date(data.timestamp).toLocaleTimeString()}`);
        });
}

// 显示成功消息
function showSuccess(message) {
    console.log('Success:', message);

    // 创建成功消息提示
    const notification = $(`
        <div class="notification success-notification" style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 255, 65, 0.9);
            color: #000;
            padding: 15px 20px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            z-index: 10000;
            box-shadow: 0 4px 8px rgba(0, 255, 65, 0.3);
            border: 1px solid #00ff41;
            animation: slideInRight 0.3s ease-out;
        ">
            ✓ ${message}
        </div>
    `);

    // 添加到页面
    $('body').append(notification);

    // 3秒后自动移除
    setTimeout(() => {
        notification.fadeOut(300, function() {
            $(this).remove();
        });
    }, 3000);
}

// 显示错误消息
function showError(message) {
    console.error('Error:', message);
    alert('错误: ' + message);
}

// 重置电台位置
function resetStationsPositions() {
    stationManager.resetStations();
}

// 定期更新系统状态
setInterval(updateSystemStatus, 30000);

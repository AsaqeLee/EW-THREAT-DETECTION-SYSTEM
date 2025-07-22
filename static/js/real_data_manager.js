// 实时数据管理器
class RealDataManager {
    constructor() {
        this.stations = [];
        this.powerData = [];
    }
    
    initialize() {
        this.bindEvents();
    }
    
    bindEvents() {
        // 打开实时数据对话框
        $('#real-data-btn').click(() => {
            this.showModal();
        });
        
        // 关闭对话框
        $('.close-real-data-modal').click(() => {
            this.hideModal();
        });
        
        // 点击对话框外部关闭
        $('#real-data-modal').click((e) => {
            if (e.target.id === 'real-data-modal') {
                this.hideModal();
            }
        });
        
        // 输入方法切换
        $('input[name="input-method"]').change(() => {
            this.toggleInputMethod();
        });
        
        // 应用数据
        $('#apply-real-data-btn').click(() => {
            this.applyRealData();
        });
        
        // 清除数据
        $('#clear-real-data-btn').click(() => {
            this.clearInputData();
        });
    }
    
    showModal() {
        // 加载电台信息
        this.loadStations();
        $('#real-data-modal').show();
    }
    
    hideModal() {
        $('#real-data-modal').hide();
    }
    
    loadStations() {
        $.get('/api/stations')
            .done((data) => {
                this.stations = data;
                this.updatePowerInputTable();
            })
            .fail(() => {
                showError('Failed to load stations');
            });
    }
    
    updatePowerInputTable() {
        const tbody = $('#power-input-tbody');
        tbody.empty();
        
        this.stations.forEach(station => {
            // 查找是否已有功率数据
            const existingData = this.powerData.find(d => d.station_id === station.id);
            const powerValue = existingData ? existingData.power : '';
            
            const row = $(`
                <tr>
                    <td>${station.id}</td>
                    <td>${station.name}</td>
                    <td>
                        <input type="number" class="power-input" 
                               data-station-id="${station.id}" 
                               value="${powerValue}" 
                               step="0.1" 
                               placeholder="Enter power (dBm)">
                    </td>
                </tr>
            `);
            tbody.append(row);
        });
    }
    
    toggleInputMethod() {
        const method = $('input[name="input-method"]:checked').val();
        
        if (method === 'manual') {
            $('#manual-input-section').show();
            $('#batch-input-section').hide();
        } else {
            $('#manual-input-section').hide();
            $('#batch-input-section').show();
        }
    }
    
    applyRealData() {
        const method = $('input[name="input-method"]:checked').val();
        
        if (method === 'manual') {
            this.applyManualData();
        } else {
            this.applyBatchData();
        }
    }
    
    applyManualData() {
        const powerData = [];
        let hasData = false;
        
        // 收集所有输入的功率数据
        $('.power-input').each(function() {
            const stationId = parseInt($(this).data('station-id'));
            const power = parseFloat($(this).val());
            
            if (!isNaN(power)) {
                hasData = true;
                powerData.push({
                    station_id: stationId,
                    power: power
                });
            }
        });
        
        if (!hasData) {
            showError('Please enter at least one power value');
            return;
        }
        
        this.powerData = powerData;
        this.processRealData();
    }
    
    applyBatchData() {
        const format = $('input[name="data-format"]:checked').val();
        const batchData = $('#batch-data').val().trim();
        
        if (!batchData) {
            showError('Please enter data');
            return;
        }
        
        try {
            let powerData = [];
            
            if (format === 'csv') {
                // 解析CSV格式
                const lines = batchData.split('\n');
                
                lines.forEach(line => {
                    const parts = line.trim().split(',');
                    if (parts.length >= 2) {
                        const stationId = parseInt(parts[0].trim());
                        const power = parseFloat(parts[1].trim());
                        
                        if (!isNaN(stationId) && !isNaN(power)) {
                            powerData.push({
                                station_id: stationId,
                                power: power
                            });
                        }
                    }
                });
            } else {
                // 解析JSON格式
                const jsonData = JSON.parse(batchData);
                
                if (Array.isArray(jsonData)) {
                    jsonData.forEach(item => {
                        if (item.station_id !== undefined && item.power !== undefined) {
                            const stationId = parseInt(item.station_id);
                            const power = parseFloat(item.power);
                            
                            if (!isNaN(stationId) && !isNaN(power)) {
                                powerData.push({
                                    station_id: stationId,
                                    power: power
                                });
                            }
                        }
                    });
                }
            }
            
            if (powerData.length === 0) {
                showError('No valid data found');
                return;
            }
            
            this.powerData = powerData;
            this.processRealData();
            
        } catch (error) {
            showError('Invalid data format: ' + error.message);
        }
    }
    
    processRealData() {
        // 构建完整的电台功率数据
        const fullPowerData = [];
        
        this.stations.forEach(station => {
            const powerEntry = this.powerData.find(d => d.station_id === station.id);
            
            if (powerEntry) {
                fullPowerData.push({
                    station_id: station.id,
                    station_name: station.name,
                    x: station.x,
                    y: station.y,
                    lat: station.lat,
                    lon: station.lon,
                    power: powerEntry.power,
                    is_anomaly: false  // 实际数据不标记异常
                });
            }
        });
        
        if (fullPowerData.length < 3) {
            showError('At least 3 stations with power data are required for triangulation');
            return;
        }
        
        // 设置为当前功率数据
        currentPowerData = {
            power_data: fullPowerData,
            timestamp: new Date().toISOString(),
            has_anomaly: false,
            coord_mode: 'geographic'
        };
        
        // 更新界面
        updatePowerChart(fullPowerData);
        updatePowerDataDisplay(fullPowerData);
        $('#locate-btn').prop('disabled', false);
        
        showSuccess('Real data applied successfully');
        this.hideModal();
    }
    
    clearInputData() {
        if ($('input[name="input-method"]:checked').val() === 'manual') {
            // 清除手动输入
            $('.power-input').val('');
        } else {
            // 清除批量输入
            $('#batch-data').val('');
        }
        
        this.powerData = [];
    }
}

// 全局实时数据管理器实例
let realDataManager = null;

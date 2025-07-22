// 电台管理器
class StationManager {
    constructor() {
        this.stations = [];
        this.editingStationId = null;
    }
    
    initialize() {
        this.bindEvents();
        this.loadStations();
    }
    
    bindEvents() {
        // 管理电台按钮
        $('#manage-stations-btn').click(() => {
            this.showModal();
        });
        
        // 关闭模态框
        $('.close-modal').click(() => {
            this.hideModal();
        });
        
        // 点击模态框外部关闭
        $('#stations-modal').click((e) => {
            if (e.target.id === 'stations-modal') {
                this.hideModal();
            }
        });
        
        // 添加电台
        $('#add-station-btn').click(() => {
            this.addStation();
        });
        
        // 更新电台
        $('#update-station-btn').click(() => {
            this.updateStation();
        });
        
        // 取消编辑
        $('#cancel-edit-btn').click(() => {
            this.cancelEdit();
        });
        
        // 坐标模式切换
        $('input[name="coord-mode"]').change(() => {
            this.toggleCoordinateMode();
        });
    }
    
    showModal() {
        this.loadStations();
        $('#stations-modal').show();
    }
    
    hideModal() {
        $('#stations-modal').hide();
        this.cancelEdit();
    }
    
    loadStations() {
        $.get('/api/stations')
            .done((data) => {
                this.stations = data;
                this.updateStationsTable();
            })
            .fail(() => {
                showError('Failed to load stations');
            });
    }
    
    updateStationsTable() {
        const tbody = $('#stations-tbody');
        tbody.empty();
        
        this.stations.forEach(station => {
            const row = $(`
                <tr>
                    <td>${station.id}</td>
                    <td>${station.name}</td>
                    <td>${station.lat ? station.lat.toFixed(6) : 'N/A'}</td>
                    <td>${station.lon ? station.lon.toFixed(6) : 'N/A'}</td>
                    <td>
                        <button class="action-btn" onclick="stationManager.editStation(${station.id})">EDIT</button>
                        <button class="action-btn delete" onclick="stationManager.deleteStation(${station.id})">DELETE</button>
                    </td>
                </tr>
            `);
            tbody.append(row);
        });
    }
    
    addStation() {
        const name = $('#station-name').val().trim();
        const lat = parseFloat($('#station-lat').val());
        const lon = parseFloat($('#station-lon').val());
        
        if (!name || isNaN(lat) || isNaN(lon)) {
            showError('Please fill in all fields with valid values');
            return;
        }
        
        $.ajax({
            url: '/api/stations',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: name,
                lat: lat,
                lon: lon
            })
        })
        .done(() => {
            showSuccess('Station added successfully');
            this.clearForm();
            this.loadStations();
            // 重新加载主界面的电台信息
            loadStationsInfo();
        })
        .fail(() => {
            showError('Failed to add station');
        });
    }
    
    editStation(stationId) {
        const station = this.stations.find(s => s.id === stationId);
        if (!station) return;
        
        this.editingStationId = stationId;
        
        $('#edit-station-id').val(stationId);
        $('#station-name').val(station.name);
        $('#station-lat').val(station.lat || '');
        $('#station-lon').val(station.lon || '');
        
        $('#add-station-btn').hide();
        $('#update-station-btn').show();
        $('#cancel-edit-btn').show();
    }
    
    updateStation() {
        const stationId = this.editingStationId;
        const name = $('#station-name').val().trim();
        const lat = parseFloat($('#station-lat').val());
        const lon = parseFloat($('#station-lon').val());
        
        if (!name || isNaN(lat) || isNaN(lon)) {
            showError('Please fill in all fields with valid values');
            return;
        }
        
        $.ajax({
            url: `/api/stations/${stationId}`,
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify({
                name: name,
                lat: lat,
                lon: lon
            })
        })
        .done(() => {
            showSuccess('Station updated successfully');
            this.cancelEdit();
            this.loadStations();
            // 重新加载主界面的电台信息
            loadStationsInfo();
        })
        .fail(() => {
            showError('Failed to update station');
        });
    }
    
    deleteStation(stationId) {
        if (!confirm('Are you sure you want to delete this station?')) {
            return;
        }
        
        $.ajax({
            url: `/api/stations/${stationId}`,
            method: 'DELETE'
        })
        .done(() => {
            showSuccess('Station deleted successfully');
            this.loadStations();
            // 重新加载主界面的电台信息
            loadStationsInfo();
        })
        .fail(() => {
            showError('Failed to delete station');
        });
    }
    
    cancelEdit() {
        this.editingStationId = null;
        this.clearForm();
        
        $('#add-station-btn').show();
        $('#update-station-btn').hide();
        $('#cancel-edit-btn').hide();
    }
    
    clearForm() {
        $('#edit-station-id').val('');
        $('#station-name').val('');
        $('#station-lat').val('');
        $('#station-lon').val('');
    }
    
    toggleCoordinateMode() {
        const mode = $('input[name="coord-mode"]:checked').val();
        
        if (mode === 'geographic') {
            $('#geographic-inputs').show();
            $('#grid-inputs').hide();
        } else {
            $('#geographic-inputs').hide();
            $('#grid-inputs').show();
        }
        
        // 重置定位按钮
        $('#locate-btn').prop('disabled', true);
        currentPowerData = null;
    }
    
    resetStations() {
        $.get('/api/reset_stations')
            .done(() => {
                this.loadStations();
                loadStationsInfo();
                showSuccess('Stations reset to default positions');
            })
            .fail(() => {
                showError('Failed to reset stations');
            });
    }
}

// 全局电台管理器实例
let stationManager = null;

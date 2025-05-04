// Chart.js configuration
Chart.defaults.color = '#e6edf3';
Chart.defaults.borderColor = '#30363d';

// Dashboard charts
let vehicleTypeChart;
let hourlyActivityChart;
let dailyActivityChart;
let topStationsChart;

function initDashboard() {
    createVehicleTypeChart();
    createHourlyActivityChart();
    createDailyActivityChart();
    createTopStationsChart();
    
    // Update charts immediately and then every minute
    updateCharts();
    setInterval(updateCharts, 60000);
}

function createVehicleTypeChart() {
    const ctx = document.getElementById('vehicleTypeChart').getContext('2d');
    vehicleTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Bus', 'Tram', 'Train', 'Metro', 'Ferry'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#3c9d61', // Bus
                    '#23a3da', // Tram
                    '#be62be', // Train
                    '#fd7e14', // Metro
                    '#6c757d'  // Ferry
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });
}

function createHourlyActivityChart() {
    const ctx = document.getElementById('hourlyActivityChart').getContext('2d');
    hourlyActivityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Will be filled with hours
            datasets: [{
                label: 'Vehicle Count',
                data: [],
                borderColor: '#23a3da',
                backgroundColor: 'rgba(35, 163, 218, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    }
                }
            }
        }
    });
}

function createDailyActivityChart() {
    const ctx = document.getElementById('dailyActivityChart').getContext('2d');
    dailyActivityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [], // Will be filled with dates
            datasets: [{
                label: 'Daily Vehicles',
                data: [],
                backgroundColor: '#3c9d61',
                borderColor: '#2d7f4b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    }
                }
            }
        }
    });
}

function createTopStationsChart() {
    const ctx = document.getElementById('topStationsChart').getContext('2d');
    topStationsChart = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: [], // Will be filled with station names
            datasets: [{
                label: 'Vehicle Count',
                data: [],
                backgroundColor: '#be62be',
                borderColor: '#a045a0',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    }
                }
            }
        }
    });
}

function updateCharts() {
    updateVehicleTypeChart();
    updateHourlyActivityChart();
    updateDailyActivityChart();
    updateTopStationsChart();
}

function updateVehicleTypeChart() {
    fetch('/api/stats/by_type')
        .then(response => response.json())
        .then(data => {
            // Process data
            const counts = [0, 0, 0, 0, 0]; // [Bus, Tram, Train, Metro, Ferry]
            
            data.forEach(item => {
                if (item.details && item.details.mode) {
                    switch (item.details.mode) {
                        case 'BUS': counts[0] = item.count; break;
                        case 'TRAM': counts[1] = item.count; break;
                        case 'TRAIN': counts[2] = item.count; break;
                        case 'SUBWAY': counts[3] = item.count; break;
                        case 'FERRY': counts[4] = item.count; break;
                    }
                }
            });
            
            // Update chart
            vehicleTypeChart.data.datasets[0].data = counts;
            vehicleTypeChart.update();
        })
        .catch(error => console.error('Error fetching vehicle type stats:', error));
}

function updateHourlyActivityChart() {
    // Get today's date
    const today = new Date().toISOString().split('T')[0];
    
    fetch(`/api/stats/hourly?date=${today}`)
        .then(response => response.json())
        .then(data => {
            // Process data
            const hours = [];
            const counts = [];
            
            // Sort by timestamp
            data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            
            data.forEach(item => {
                const hour = new Date(item.timestamp).getHours();
                hours.push(`${hour}:00`);
                counts.push(item.count);
            });
            
            // Update chart
            hourlyActivityChart.data.labels = hours;
            hourlyActivityChart.data.datasets[0].data = counts;
            hourlyActivityChart.update();
        })
        .catch(error => console.error('Error fetching hourly stats:', error));
}

function updateDailyActivityChart() {
    // Calculate date range (last 7 days)
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 6);
    
    const startDate = start.toISOString().split('T')[0];
    const endDate = end.toISOString().split('T')[0];
    
    fetch(`/api/stats/daily?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            // Process data
            const dates = [];
            const counts = [];
            
            // Sort by timestamp
            data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            
            data.forEach(item => {
                const date = new Date(item.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                dates.push(date);
                counts.push(item.count);
            });
            
            // Update chart
            dailyActivityChart.data.labels = dates;
            dailyActivityChart.data.datasets[0].data = counts;
            dailyActivityChart.update();
        })
        .catch(error => console.error('Error fetching daily stats:', error));
}

function updateTopStationsChart() {
    fetch('/api/stats/by_station?limit=10')
        .then(response => response.json())
        .then(data => {
            // Process data
            const stations = [];
            const counts = [];
            
            // Sort by count in descending order
            data.sort((a, b) => b.count - a.count);
            
            data.forEach(item => {
                if (item.details && item.details.station_name) {
                    stations.push(item.details.station_name);
                    counts.push(item.count);
                }
            });
            
            // Update chart
            topStationsChart.data.labels = stations;
            topStationsChart.data.datasets[0].data = counts;
            topStationsChart.update();
        })
        .catch(error => console.error('Error fetching station stats:', error));
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', initDashboard);
Chart.defaults.color = '#e6edf3';
Chart.defaults.borderColor = '#30363d';

let vehicleTypeChart;
let hourlyActivityChart;
let dailyActivityChart;
let topStationsChart;

function initDashboard() {
    createVehicleTypeChart();
    createHourlyActivityChart();
    createDailyActivityChart();
    createTopStationsChart();

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
                },
                datalabels: {
                    formatter: (value, context) => {
                        const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        const percentage = total ? ((value / total) * 100).toFixed(1) : 0;
                        return `${percentage}%`;
                    },
                    color: '#fff',
                    font: {
                        weight: 'bold'
                    }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}

function createHourlyActivityChart() {
    const ctx = document.getElementById('hourlyActivityChart').getContext('2d');
    hourlyActivityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
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
            scales: {
                y: { beginAtZero: true },
                x: {}
            }
        }
    });
}

function createDailyActivityChart() {
    const ctx = document.getElementById('dailyActivityChart').getContext('2d');
    dailyActivityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
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
            scales: {
                y: { beginAtZero: true },
                x: {}
            }
        }
    });
}

function createTopStationsChart() {
    const ctx = document.getElementById('topStationsChart').getContext('2d');
    topStationsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
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
            scales: {
                x: { beginAtZero: true },
                y: {}
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
        .then(res => res.json())
        .then(data => {
            const counts = [0, 0, 0, 0, 0];
            data.forEach(item => {
                switch (item.details.mode) {
                    case 'BUS': counts[0] = item.count; break;
                    case 'TRAM': counts[1] = item.count; break;
                    case 'TRAIN': counts[2] = item.count; break;
                    case 'SUBWAY': counts[3] = item.count; break;
                    case 'FERRY': counts[4] = item.count; break;
                }
            });
            vehicleTypeChart.data.datasets[0].data = counts;
            vehicleTypeChart.update();
        });
}

function updateHourlyActivityChart() {
    const today = new Date().toISOString().split('T')[0];
    fetch(`/api/stats/hourly?date=${today}`)
        .then(res => res.json())
        .then(data => {
            const labels = [];
            const values = [];
            data.forEach(entry => {
                const hour = new Date(entry.timestamp).getHours();
                labels.push(`${hour}:00`);
                values.push(entry.count);
            });
            hourlyActivityChart.data.labels = labels;
            hourlyActivityChart.data.datasets[0].data = values;
            hourlyActivityChart.update();
        });
}

function updateDailyActivityChart() {
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 6);

    const startDate = start.toISOString().split('T')[0];
    const endDate = end.toISOString().split('T')[0];

    fetch(`/api/stats/daily?start_date=${startDate}&end_date=${endDate}`)
        .then(res => res.json())
        .then(data => {
            const labels = [];
            const values = [];
            data.forEach(entry => {
                const date = new Date(entry.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                labels.push(date);
                values.push(entry.count);
            });
            dailyActivityChart.data.labels = labels;
            dailyActivityChart.data.datasets[0].data = values;
            dailyActivityChart.update();
        });
}

function updateTopStationsChart() {
    fetch('/api/stats/by_station?limit=10')
        .then(res => res.json())
        .then(data => {
            const labels = [];
            const values = [];
            data.forEach(entry => {
                labels.push(entry.details.station_name);
                values.push(entry.count);
            });
            topStationsChart.data.labels = labels;
            topStationsChart.data.datasets[0].data = values;
            topStationsChart.update();
        });
}

document.addEventListener('DOMContentLoaded', initDashboard);

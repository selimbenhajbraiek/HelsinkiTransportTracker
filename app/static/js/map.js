// Initialize map with Helsinki coordinates
let map;
let vehicleMarkers = {};
let stationMarkers = {};
let routeLines = {};
let refreshInterval;

// Vehicle and station icons
const vehicleIcons = {
    BUS: L.divIcon({
        className: 'vehicle-icon',
        html: '<div style="background-color: #3c9d61; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    TRAM: L.divIcon({
        className: 'vehicle-icon',
        html: '<div style="background-color: #23a3da; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    TRAIN: L.divIcon({
        className: 'vehicle-icon',
        html: '<div style="background-color: #be62be; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    SUBWAY: L.divIcon({
        className: 'vehicle-icon',
        html: '<div style="background-color: #fd7e14; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    }),
    FERRY: L.divIcon({
        className: 'vehicle-icon',
        html: '<div style="background-color: #6c757d; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    })
};

const stationIcon = L.divIcon({
    className: 'station-icon',
    html: '<div style="background-color: #ffffff; width: 8px; height: 8px; border-radius: 50%; border: 2px solid #30363d;"></div>',
    iconSize: [12, 12],
    iconAnchor: [6, 6]
});

function initMap() {
    // Create map centered on Helsinki
    map = L.map('map').setView([60.1699, 24.9384], 12);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Add legend
    addLegend();

    // Start fetching vehicles
    fetchVehicles();
    refreshInterval = setInterval(fetchVehicles, 10000); // Refresh every 10 seconds
}

function addLegend() {
    const legend = L.control({ position: 'bottomright' });

    legend.onAdd = function(map) {
        const div = L.DomUtil.create('div', 'legend');
        div.innerHTML = `
            <h6>Vehicle Types</h6>
            <div class="legend-item"><i class="bus-color"></i> Bus</div>
            <div class="legend-item"><i class="tram-color"></i> Tram</div>
            <div class="legend-item"><i class="train-color"></i> Train</div>
            <div class="legend-item"><i class="subway-color"></i> Metro</div>
            <div class="legend-item"><i class="ferry-color"></i> Ferry</div>
        `;
        return div;
    };

    legend.addTo(map);
}

function fetchVehicles() {
    fetch('/api/vehicles')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(vehicles => updateVehicles(vehicles))
        .catch(error => console.error('Error fetching vehicles:', error));
}

function updateVehicles(vehicles) {
    // Track currently active vehicles for cleanup
    const activeVehicles = {};

    // Update statistics
    let vehicleCounts = {
        total: vehicles.length,
        BUS: 0,
        TRAM: 0,
        TRAIN: 0,
        SUBWAY: 0,
        FERRY: 0
    };

    // Update vehicle markers
    vehicles.forEach(vehicle => {
        const vehicleId = vehicle.id;
        activeVehicles[vehicleId] = true;

        // Update statistics
        if (vehicle.mode) {
            vehicleCounts[vehicle.mode] = (vehicleCounts[vehicle.mode] || 0) + 1;
        }

        if (vehicleMarkers[vehicleId]) {
            // Update existing marker
            vehicleMarkers[vehicleId].setLatLng([vehicle.position.lat, vehicle.position.lng]);
            
            // Update popup content
            const popup = createVehiclePopup(vehicle);
            vehicleMarkers[vehicleId].bindPopup(popup);
            
            // Update heading
            if (vehicle.heading !== null && vehicle.heading !== undefined) {
                vehicleMarkers[vehicleId].setRotationAngle(vehicle.heading);
            }
        } else {
            // Create new marker
            const icon = vehicleIcons[vehicle.mode] || vehicleIcons.BUS;
            const marker = L.marker([vehicle.position.lat, vehicle.position.lng], {
                icon: icon,
                rotationAngle: vehicle.heading || 0
            });
            
            const popup = createVehiclePopup(vehicle);
            marker.bindPopup(popup);
            
            marker.addTo(map);
            vehicleMarkers[vehicleId] = marker;
        }
    });

    // Remove markers for vehicles no longer active
    for (const vehicleId in vehicleMarkers) {
        if (!activeVehicles[vehicleId]) {
            map.removeLayer(vehicleMarkers[vehicleId]);
            delete vehicleMarkers[vehicleId];
        }
    }

    // Update statistics display
    document.getElementById('activeVehicles').textContent = vehicleCounts.total;
    document.getElementById('busCount').textContent = vehicleCounts.BUS || 0;
    document.getElementById('tramCount').textContent = vehicleCounts.TRAM || 0;
    document.getElementById('trainCount').textContent = vehicleCounts.TRAIN || 0;
    document.getElementById('metroCount').textContent = vehicleCounts.SUBWAY || 0;
    document.getElementById('ferryCount').textContent = vehicleCounts.FERRY || 0;
}

function createVehiclePopup(vehicle) {
    const content = `
        <div class="vehicle-popup">
            <div class="vehicle-id">${vehicle.route_id || 'No route'} - Vehicle ${vehicle.vehicle_number || vehicle.id}</div>
            <div class="vehicle-details">
                <div>Type: ${vehicle.mode}</div>
                <div>Speed: ${vehicle.speed ? (vehicle.speed * 3.6).toFixed(1) + ' km/h' : 'N/A'}</div>
                <div>Heading: ${vehicle.heading ? vehicle.heading + '°' : 'N/A'}</div>
                <div>Trip ID: ${vehicle.trip_id || 'N/A'}</div>
            </div>
        </div>
    `;
    return content;
}

function getVehicleColor(mode) {
    const colors = {
        BUS: '#3c9d61',
        TRAM: '#23a3da',
        TRAIN: '#be62be',
        SUBWAY: '#fd7e14',
        FERRY: '#6c757d'
    };
    return colors[mode] || colors.BUS;
}

function showStations() {
    // Fetch all stations
    fetch('/api/stations')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(stations => {
            stations.forEach(station => {
                if (!stationMarkers[station.id]) {
                    const marker = L.marker([station.position.lat, station.position.lng], {
                        icon: stationIcon
                    });
                    
                    const popup = `
                        <div class="station-popup">
                            <div class="station-name">${station.name} ${station.code ? '(' + station.code + ')' : ''}</div>
                            <div class="station-details">
                                <div>Zone: ${station.zone_id || 'N/A'}</div>
                                <div>Platform: ${station.platform_code || 'N/A'}</div>
                                <div>Routes: ${station.routes ? station.routes.length : 0}</div>
                            </div>
                            ${station.routes && station.routes.length > 0 ? 
                                `<button class="btn btn-sm btn-primary mt-2" onclick="showRoute('${station.routes[0]}')">Show Route</button>` : 
                                ''}
                        </div>
                    `;
                    
                    marker.bindPopup(popup);
                    marker.addTo(map);
                    stationMarkers[station.id] = marker;
                }
            });
        })
        .catch(error => console.error('Error fetching stations:', error));
}

function showRoute(routeId) {
    if (routeLines[routeId]) {
        // Route is already displayed
        hideRoute(routeId);
        return;
    }
    
    fetch(`/api/route/${routeId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(route => {
            if (route.patterns && route.patterns.length > 0) {
                const pattern = route.patterns[0];
                const stopIds = pattern.stops;
                
                // Fetch all stops to get their coordinates
                Promise.all(stopIds.map(stopId => 
                    fetch(`/api/station/${stopId}`).then(res => res.json())
                ))
                .then(stops => {
                    const coordinates = stops.map(stop => [stop.position.lat, stop.position.lng]);
                    
                    // Draw the route line
                    const color = route.color ? `#${route.color}` : getVehicleColor(route.mode);
                    const routeLine = L.polyline(coordinates, {
                        color: color,
                        weight: 4,
                        opacity: 0.7,
                        className: 'route-line'
                    }).addTo(map);
                    
                    routeLines[routeId] = routeLine;
                    
                    // Fit map to route bounds
                    map.fitBounds(routeLine.getBounds(), {
                        padding: [50, 50]
                    });
                });
            }
        })
        .catch(error => console.error(`Error fetching route ${routeId}:`, error));
}

function hideRoute(routeId) {
    if (routeLines[routeId]) {
        map.removeLayer(routeLines[routeId]);
        delete routeLines[routeId];
    }
}

// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', initMap);
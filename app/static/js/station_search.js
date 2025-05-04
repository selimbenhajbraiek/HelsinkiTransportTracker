function initStationSearch() {
    const searchInput = document.getElementById('stationSearch');
    const searchButton = document.getElementById('searchButton');
    const resultsContainer = document.getElementById('searchResults');

    // Add event listeners
    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query, resultsContainer);
        }
    });

    searchInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                performSearch(query, resultsContainer);
            }
        }
    });
}

function performSearch(query, resultsElement) {
    // Show loading indicator
    resultsElement.innerHTML = '<div class="d-flex justify-content-center"><div class="loading"></div></div>';

    // Fetch search results
    fetch(`/api/stations/search?query=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(stations => {
            // Clear loading indicator
            resultsElement.innerHTML = '';

            if (stations.length === 0) {
                resultsElement.innerHTML = '<div class="alert alert-info">No stations found</div>';
                return;
            }

            // Display results
            stations.forEach(station => {
                const item = document.createElement('a');
                item.className = 'list-group-item list-group-item-action search-result-item';
                item.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="fw-bold">${station.name}</div>
                            <small>${station.code || ''} ${station.zone_id ? '(Zone ' + station.zone_id + ')' : ''}</small>
                        </div>
                        <span class="badge bg-primary rounded-pill">${station.routes ? station.routes.length : 0} routes</span>
                    </div>
                `;
                
                item.addEventListener('click', () => {
                    showStationOnMap(station.id);
                });
                
                resultsElement.appendChild(item);
            });
        })
        .catch(error => {
            console.error('Error searching stations:', error);
            resultsElement.innerHTML = '<div class="alert alert-danger">Error searching stations</div>';
        });
}

function showStationOnMap(stationId) {
    // Fetch station details
    fetch(`/api/station/${stationId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(station => {
            // Pan map to station location
            map.setView([station.position.lat, station.position.lng], 16);
            
            // Create station marker if doesn't exist
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
            
            // Open popup
            stationMarkers[station.id].openPopup();
        })
        .catch(error => console.error(`Error fetching station ${stationId}:`, error));
}

// Initialize station search functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', initStationSearch);
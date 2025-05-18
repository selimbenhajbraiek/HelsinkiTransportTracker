const stationMarkers = {};
let currentRouteLine = null;

function initStationSearch() {
    const searchInput = document.getElementById('stationSearch');
    const searchButton = document.getElementById('searchButton');
    const resultsContainer = document.getElementById('searchResults');

    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) performSearch(query, resultsContainer);
    });

    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) performSearch(query, resultsContainer);
        }
    });

    // Route search button logic
    const routeBtn = document.getElementById('routeSearchButton');
    if (routeBtn) {
        routeBtn.addEventListener('click', () => {
            const fromStation = document.getElementById('fromStation').value.trim();
            const toStation = document.getElementById('toStation').value.trim();

            if (!fromStation || !toStation) {
                alert("Please enter both station names.");
                return;
            }

            drawRouteBetweenStations(fromStation, toStation);
        });
    }
}

function performSearch(query, container) {
    container.innerHTML = '<div class="text-center py-2">Searching...</div>';

    fetch(`/api/stations/search?query=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(stations => {
            container.innerHTML = '';

            if (!stations.length) {
                container.innerHTML = '<div class="alert alert-warning">No stations found</div>';
                return;
            }

            stations.forEach(station => {
                const item = document.createElement('button');
                item.className = 'list-group-item list-group-item-action';
                item.innerHTML = `<strong>${station.name}</strong> ${station.zone_id ? ` – Zone ${station.zone_id}` : ''}`;
                item.onclick = () => showStationOnMap(station.id);
                container.appendChild(item);
            });
        })
        .catch(err => {
            console.error(err);
            container.innerHTML = '<div class="alert alert-danger">Error searching stations</div>';
        });
}

function showStationOnMap(id) {
    fetch(`/api/station/${id}`)
        .then(res => res.json())
        .then(station => {
            const { lat, lng } = station.position;

            map.setView([lat, lng], 16);

            if (stationMarkers[station.id]) {
                stationMarkers[station.id].remove();
            }

            const marker = L.marker([lat, lng]).addTo(map);
            marker.bindPopup(`
                <strong>${station.name}</strong><br>
                Zone: ${station.zone_id || 'N/A'}<br>
                Platform: ${station.platform_code || 'N/A'}<br>
                Routes: ${station.routes?.join(', ') || 'None'}
            `);
            marker.openPopup();

            stationMarkers[station.id] = marker;
        })
        .catch(error => {
            console.error('Failed to load station detail:', error);
        });
}


document.addEventListener('DOMContentLoaded', initStationSearch);

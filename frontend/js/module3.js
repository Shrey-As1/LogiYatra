/**
 * Module 3 — Route Optimization & Traffic Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('routeForm');
  const presetSelect = document.getElementById('hubPreset');
  const routeSpinner = document.getElementById('routeSpinner');
  const solveBtn = document.getElementById('solveRouteBtn');
  const routesListContainer = document.getElementById('routesListContainer');
  const primaryRouteStats = document.getElementById('primaryRouteStats');
  const mapDataSource = document.getElementById('mapDataSource');
  const coordsDisplay = document.getElementById('coordsDisplay');
  const trafficNotice = document.getElementById('trafficProviderNotice');
  const forwardBtn = document.getElementById('sendRouteToModule6Btn');

  const presets = {
    bhubaneswar: { oLat: 20.2961, oLon: 85.8245, dLat: 20.4625, dLon: 85.8828 },
    mumbai: { oLat: 18.9515, oLon: 72.9525, dLat: 18.7565, dLon: 73.8567 },
    delhi: { oLat: 28.5355, oLon: 77.2732, dLat: 28.5700, dLon: 77.3800 }
  };

  let currentRoutes = [];
  let selectedRoute = null;

  if (presetSelect) {
    presetSelect.addEventListener('change', () => {
      const val = presetSelect.value;
      if (presets[val]) {
        document.getElementById('originLat').value = presets[val].oLat;
        document.getElementById('originLon').value = presets[val].oLon;
        document.getElementById('destLat').value = presets[val].dLat;
        document.getElementById('destLon').value = presets[val].dLon;
      }
    });
  }

  // Check initial traffic provider
  checkProvider();
  async function checkProvider() {
    try {
      const health = await API.getHealth();
      const tomtom = health.providers && health.providers.tomtom_live_traffic;
      if (tomtom && tomtom.configured) {
        if (trafficNotice) trafficNotice.textContent = '🟢 TomTom Live Traffic API: Connected and active.';
      } else {
        if (trafficNotice) trafficNotice.textContent = 'ℹ️ TomTom API key is not configured in .env. Using OpenStreetMap road network & corridor free-flow speeds.';
      }
    } catch (e) {
      console.warn(e);
    }
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        if (routeSpinner) routeSpinner.style.display = 'inline-block';
        solveBtn.disabled = true;

        const origin = {
          lat: parseFloat(document.getElementById('originLat').value),
          lon: parseFloat(document.getElementById('originLon').value)
        };
        const destination = {
          lat: parseFloat(document.getElementById('destLat').value),
          lon: parseFloat(document.getElementById('destLon').value)
        };
        const k = parseInt(document.getElementById('kRoutes').value, 10);

        coordsDisplay.textContent = `${origin.lat}, ${origin.lon} → ${destination.lat}, ${destination.lon}`;

        const response = await API.getRoute(origin, destination, k);
        if (response && response.result) {
          const res = response.result;
          const best = res.best_route;
          const alts = res.alternatives || [];
          currentRoutes = [best, ...alts];
          selectedRoute = best;

          primaryRouteStats.textContent = `${best.distance_km} km · ${best.estimated_time_minutes} min`;
          mapDataSource.textContent = res.data_source || 'OSM Corridor Model';

          renderRouteCards(currentRoutes);
        }
      } catch (err) {
        alert(`Routing solve error: ${err.message}`);
      } finally {
        if (routeSpinner) routeSpinner.style.display = 'none';
        solveBtn.disabled = false;
      }
    });
  }

  function renderRouteCards(routes) {
    if (!routesListContainer) return;
    routesListContainer.innerHTML = '';

    routes.forEach((r, idx) => {
      const card = document.createElement('div');
      card.className = 'route-card' + (idx === 0 ? ' selected' : '');
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <strong style="color:#FFF;">${r.name || `Route ${idx+1}`}</strong>
            <span style="font-size:0.75rem; color:var(--text-dim); margin-left:8px;">Risk: ${(r.route_risk_score * 100).toFixed(0)}%</span>
          </div>
          <div style="text-align:right;">
            <strong style="color:var(--amber-primary);">${r.distance_km} km</strong>
            <span style="font-size:0.75rem; color:var(--text-muted); margin-left:6px;">${r.estimated_time_minutes} min</span>
          </div>
        </div>
      `;

      card.addEventListener('click', () => {
        document.querySelectorAll('.route-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedRoute = r;
        primaryRouteStats.textContent = `${r.distance_km} km · ${r.estimated_time_minutes} min`;
      });

      routesListContainer.appendChild(card);
    });
  }

  if (forwardBtn) {
    forwardBtn.addEventListener('click', () => {
      localStorage.setItem('logiyantra_m3_route', JSON.stringify({
        selected_route: selectedRoute,
        alternatives: currentRoutes,
        route_risk: selectedRoute ? selectedRoute.route_risk_score : 0.15,
        timestamp: new Date().toISOString()
      }));
      window.location.href = 'module6.html';
    });
  }
});

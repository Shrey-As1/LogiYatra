/**
 * Module 4 — Warehouse Congestion Prediction Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('congestionForm');
  const presetSelect = document.getElementById('congestionPreset');
  const spinner = document.getElementById('congSpinner');
  const predictBtn = document.getElementById('predictCongestionBtn');
  const probDisplay = document.getElementById('congestionProbDisplay');
  const statusText = document.getElementById('congestionStatusText');
  const badge = document.getElementById('congestionBadge');
  const forwardBtn = document.getElementById('sendCongToModule6Btn');

  let currentCongestionRisk = 0.5089;

  if (presetSelect) {
    presetSelect.addEventListener('change', () => {
      const mode = presetSelect.value;
      if (mode === 'normal') {
        document.getElementById('currentDockUtil').value = 0.40;
        document.getElementById('orderVolume').value = 220;
        document.getElementById('staffCount').value = 18;
        document.getElementById('truckArrivals').value = 8;
        document.getElementById('burstEvent').value = 0;
        document.getElementById('shiftChange').value = 0;
      } else if (mode === 'surge') {
        document.getElementById('currentDockUtil').value = 0.88;
        document.getElementById('orderVolume').value = 650;
        document.getElementById('staffCount').value = 12;
        document.getElementById('truckArrivals').value = 28;
        document.getElementById('burstEvent').value = 1;
        document.getElementById('shiftChange').value = 1;
      } else {
        document.getElementById('currentDockUtil').value = 0.65;
        document.getElementById('orderVolume').value = 380;
        document.getElementById('staffCount').value = 16;
        document.getElementById('truckArrivals').value = 14;
        document.getElementById('burstEvent').value = 0;
        document.getElementById('shiftChange').value = 0;
      }
    });
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        if (spinner) spinner.style.display = 'inline-block';
        predictBtn.disabled = true;

        const baseUtil = parseFloat(document.getElementById('currentDockUtil').value);
        const orderVol = parseFloat(document.getElementById('orderVolume').value);
        const staff = parseFloat(document.getElementById('staffCount').value);
        const trucks = parseFloat(document.getElementById('truckArrivals').value);
        const burst = parseFloat(document.getElementById('burstEvent').value);
        const shift = parseFloat(document.getElementById('shiftChange').value);

        // Generate synthetic sequence of 12 hourly observations leading to current state
        const observations = [];
        for (let i = 0; i < 12; i++) {
          const factor = (i + 1) / 12.0;
          observations.push({
            hour: (7 + i) % 24,
            dock_utilization: Math.max(0.1, Math.min(1.0, baseUtil * (0.8 + factor * 0.2))),
            order_volume: orderVol * (0.8 + factor * 0.2),
            staff_count: staff,
            truck_arrivals: trucks * (0.8 + factor * 0.2),
            burst_event: i === 11 ? burst : 0,
            shift_change: i === 11 ? shift : 0
          });
        }

        const response = await API.predictCongestion(observations);
        if (response && response.prediction) {
          const res = response.prediction;
          currentCongestionRisk = res.congestion_risk;
          probDisplay.innerHTML = `${(res.congestion_risk * 100).toFixed(2)}% <span class="stat-unit">risk</span>`;
          statusText.textContent = res.status + ' CONGESTION';

          badge.textContent = res.status;
          badge.className = 'badge ' + (
            res.status === 'CRITICAL' ? 'badge-critical' :
            res.status === 'HEAVY' ? 'badge-high' :
            res.status === 'MODERATE' ? 'badge-moderate' : 'badge-normal'
          );

          localStorage.setItem('logiyantra_m4_congestion', JSON.stringify({
            congestion_risk: currentCongestionRisk,
            status: res.status,
            timestamp: new Date().toISOString()
          }));
        }
      } catch (err) {
        alert(`Warehouse congestion prediction error: ${err.message}`);
      } finally {
        if (spinner) spinner.style.display = 'none';
        predictBtn.disabled = false;
      }
    });
  }

  if (forwardBtn) {
    forwardBtn.addEventListener('click', () => {
      localStorage.setItem('logiyantra_m4_congestion', JSON.stringify({
        congestion_risk: currentCongestionRisk,
        source: 'module4_manual_forward'
      }));
      window.location.href = 'module6.html';
    });
  }
});

/**
 * Module 2 — Delivery Delay Prediction Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('delayForm');
  const delaySpinner = document.getElementById('delaySpinner');
  const predictBtn = document.getElementById('predictDelayBtn');
  const probDisplay = document.getElementById('delayProbDisplay');
  const statusText = document.getElementById('delayStatusText');
  const badge = document.getElementById('delayRiskBadge');
  const forwardBtn = document.getElementById('sendDelayToModule6Btn');

  let currentDelayRisk = 0.0334;

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        if (delaySpinner) delaySpinner.style.display = 'inline-block';
        predictBtn.disabled = true;

        const testProbVal = document.getElementById('testProbability').value.trim();
        const payload = {};

        if (testProbVal !== '') {
          payload.test_probability = parseFloat(testProbVal);
        } else {
          payload['Shipping Mode'] = document.getElementById('shippingMode').value;
          payload['Days for shipment (scheduled)'] = Number(document.getElementById('scheduledDays').value);
          payload['Market'] = document.getElementById('orderMarket').value;
          payload['Type'] = document.getElementById('orderType').value;
          payload['Product Price'] = Number(document.getElementById('productPrice').value);
        }

        const response = await API.predictDeliveryDelay(payload);
        if (response && response.result) {
          const res = response.result;
          currentDelayRisk = res.delay_probability;
          probDisplay.innerHTML = `${(res.delay_probability * 100).toFixed(2)}% <span class="stat-unit">probability</span>`;

          if (res.predicted_late) {
            statusText.textContent = 'DELAYED (RISK BREACH)';
            statusText.style.color = 'var(--red-critical)';
          } else {
            statusText.textContent = 'ON-TIME SHIPMENT';
            statusText.style.color = 'var(--mint-positive)';
          }

          badge.textContent = res.risk_level + ' RISK';
          badge.className = 'badge ' + (
            res.risk_level === 'CRITICAL' ? 'badge-critical' :
            res.risk_level === 'HIGH' ? 'badge-high' :
            res.risk_level === 'MEDIUM' ? 'badge-moderate' : 'badge-normal'
          );

          localStorage.setItem('logiyantra_m2_delay', JSON.stringify({
            delay_risk: currentDelayRisk,
            risk_level: res.risk_level,
            timestamp: new Date().toISOString()
          }));
        }
      } catch (err) {
        alert(`Delivery delay prediction error: ${err.message}`);
      } finally {
        if (delaySpinner) delaySpinner.style.display = 'none';
        predictBtn.disabled = false;
      }
    });
  }

  if (forwardBtn) {
    forwardBtn.addEventListener('click', () => {
      localStorage.setItem('logiyantra_m2_delay', JSON.stringify({
        delay_risk: currentDelayRisk,
        source: 'module2_manual_forward'
      }));
      window.location.href = 'module6.html';
    });
  }
});

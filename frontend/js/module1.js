/**
 * Module 1 — Demand Forecasting Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('demandForm');
  const btnSpinner = document.getElementById('btnSpinner');
  const predictBtn = document.getElementById('predictDemandBtn');
  const weeklyDisplay = document.getElementById('weeklyDemandDisplay');
  const dailyDisplay = document.getElementById('dailyDemandDisplay');
  const sendToModule5Btn = document.getElementById('sendToModule5Btn');

  let currentDailyDemand = 2334.63;

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        if (btnSpinner) btnSpinner.style.display = 'inline-block';
        predictBtn.disabled = true;

        const payload = {
          Store: Number(document.getElementById('storeNum').value),
          Dept: Number(document.getElementById('deptNum').value),
          sales_lag_1: Number(document.getElementById('salesLag1').value),
          Size: Number(document.getElementById('storeSize').value),
          is_holiday: Number(document.getElementById('isHoliday').value),
          CPI: Number(document.getElementById('cpi').value),
          Unemployment: Number(document.getElementById('unemployment').value),
        };

        const response = await API.predictDemand(payload);
        if (response && response.result) {
          const res = response.result;
          weeklyDisplay.innerHTML = `${Number(res.forecast_weekly_demand).toLocaleString()} <span class="stat-unit">units</span>`;
          dailyDisplay.textContent = `${Number(res.forecast_daily_demand).toLocaleString()} units/day`;
          currentDailyDemand = res.forecast_daily_demand;

          // Save forecast to localStorage for Module 5
          localStorage.setItem('logiyantra_m1_forecast', JSON.stringify({
            daily_demand: currentDailyDemand,
            weekly_demand: res.forecast_weekly_demand,
            timestamp: new Date().toISOString()
          }));
        }
      } catch (err) {
        alert(`Demand prediction error: ${err.message}`);
      } finally {
        if (btnSpinner) btnSpinner.style.display = 'none';
        predictBtn.disabled = false;
      }
    });
  }

  if (sendToModule5Btn) {
    sendToModule5Btn.addEventListener('click', () => {
      localStorage.setItem('logiyantra_m1_forecast', JSON.stringify({
        daily_demand: currentDailyDemand,
        source: 'module1_manual_forward'
      }));
      window.location.href = 'module5.html';
    });
  }
});

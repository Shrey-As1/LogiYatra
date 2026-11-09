/**
 * Module 5 — Inventory Optimization Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('inventoryForm');
  const optimizeBtn = document.getElementById('optimizeInventoryBtn');
  const orderQtyDisplay = document.getElementById('orderQtyDisplay');
  const orderRecText = document.getElementById('orderRecommendationText');
  const badge = document.getElementById('inventoryStatusBadge');
  const safetyStockDisplay = document.getElementById('safetyStockDisplay');
  const ropDisplay = document.getElementById('ropDisplay');
  const targetStockDisplay = document.getElementById('targetStockDisplay');
  const daysOfSupplyDisplay = document.getElementById('daysOfSupplyDisplay');
  const demandSourceNotice = document.getElementById('demandSourceNotice');
  const forwardBtn = document.getElementById('sendInvToModule6Btn');

  let currentResult = null;

  // Check if Module 1 saved a forecast in localStorage
  const m1Saved = localStorage.getItem('logiyantra_m1_forecast');
  if (m1Saved) {
    try {
      const data = JSON.parse(m1Saved);
      if (data.daily_demand) {
        document.getElementById('dailyDemand').value = data.daily_demand;
        if (demandSourceNotice) {
          demandSourceNotice.innerHTML = `🟢 <strong>Imported from Module 01:</strong> ${Number(data.daily_demand).toLocaleString()} units/day forecast.`;
          demandSourceNotice.style.color = 'var(--mint-positive)';
        }
      }
    } catch (e) {
      console.warn(e);
    }
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        optimizeBtn.disabled = true;

        const payload = {
          current_stock: parseFloat(document.getElementById('currentStock').value),
          forecast_daily_demand: parseFloat(document.getElementById('dailyDemand').value),
          lead_time_days: parseFloat(document.getElementById('leadTimeDays').value),
          safety_stock_days: parseFloat(document.getElementById('safetyDays').value),
          review_period_days: parseFloat(document.getElementById('reviewDays').value),
          pack_size: parseFloat(document.getElementById('packSize').value)
        };

        const response = await API.optimizeInventory(payload);
        if (response && response.result) {
          const res = response.result;
          currentResult = res;

          orderQtyDisplay.innerHTML = `${Number(res.recommended_order_quantity).toLocaleString()} <span class="stat-unit">units</span>`;
          orderRecText.textContent = res.recommendation;

          safetyStockDisplay.textContent = `${Number(res.safety_stock_units).toLocaleString()} units (${res.safety_stock_days} days)`;
          ropDisplay.textContent = `${Number(res.reorder_point).toLocaleString()} units`;
          targetStockDisplay.textContent = `${Number(res.target_stock).toLocaleString()} units`;
          daysOfSupplyDisplay.textContent = `${res.days_of_supply} days on-hand`;

          badge.textContent = res.status;
          badge.className = 'badge ' + (
            res.status === 'CRITICAL_REPLENISH' ? 'badge-critical' :
            res.status === 'REPLENISH' ? 'badge-high' : 'badge-normal'
          );

          localStorage.setItem('logiyantra_m5_inventory', JSON.stringify({
            status: res.status,
            reorder_qty: res.recommended_order_quantity,
            current_stock: res.current_stock,
            reorder_point: res.reorder_point,
            timestamp: new Date().toISOString()
          }));
        }
      } catch (err) {
        alert(`Inventory calculation error: ${err.message}`);
      } finally {
        optimizeBtn.disabled = false;
      }
    });
  }

  if (forwardBtn) {
    forwardBtn.addEventListener('click', () => {
      if (!currentResult) {
        alert('Please calculate inventory recommendations first.');
        return;
      }
      localStorage.setItem('logiyantra_m5_inventory', JSON.stringify({
        status: currentResult.status,
        inventory_result: currentResult,
        stock_level: currentResult.current_stock,
        reorder_point: currentResult.reorder_point,
        source: 'module5_manual_forward'
      }));
      window.location.href = 'module6.html';
    });
  }
});

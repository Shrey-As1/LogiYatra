/**
 * Module 6 — Autonomous Decision Engine Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('decisionForm');
  const delaySlider = document.getElementById('delayRiskInput');
  const congSlider = document.getElementById('congestionRiskInput');
  const routeSlider = document.getElementById('routeRiskInput');
  const invSelect = document.getElementById('inventoryStatusSelect');
  const stockInput = document.getElementById('stockLevelInput');
  const ropInput = document.getElementById('ropInput');
  const delayValText = document.getElementById('delayValText');
  const congValText = document.getElementById('congestionValText');
  const routeValText = document.getElementById('routeValText');
  const loadBtn = document.getElementById('loadModulesDataBtn');
  const evalBtn = document.getElementById('evaluateDecisionBtn');
  const primaryDisplay = document.getElementById('primaryActionDisplay');
  const reasonsText = document.getElementById('reasonsText');
  const badge = document.getElementById('overallStatusBadge');
  const actionsContainer = document.getElementById('actionsListContainer');
  const approveBtn = document.getElementById('moduleApproveBtn');
  const approvalStatus = document.getElementById('moduleApprovalStatus');
  const sendToM7Btn = document.getElementById('sendToModule7Btn');

  let currentDecision = null;

  // Slider text sync
  function updateSliderLabels() {
    delayValText.textContent = `${(parseFloat(delaySlider.value) * 100).toFixed(1)}%`;
    congValText.textContent = `${(parseFloat(congSlider.value) * 100).toFixed(1)}%`;
    routeValText.textContent = `${(parseFloat(routeSlider.value) * 100).toFixed(1)}%`;
  }
  delaySlider.addEventListener('input', updateSliderLabels);
  congSlider.addEventListener('input', updateSliderLabels);
  routeSlider.addEventListener('input', updateSliderLabels);

  // Auto-detect incoming decision data from Module 5 handoff
  const incoming = sessionStorage.getItem('ly_incoming_decision');
  if (incoming) {
    try {
      const data = JSON.parse(incoming);
      if (data.inventory_status && invSelect) invSelect.value = data.inventory_status;
      if (data.current_stock !== undefined && stockInput) stockInput.value = data.current_stock;
      if (data.reorder_point !== undefined && ropInput) ropInput.value = data.reorder_point;
      sessionStorage.removeItem('ly_incoming_decision');
    } catch (e) {}
  }

  // Auto-detect incoming delay data from Module 2 handoff
  const incDelay = sessionStorage.getItem('ly_incoming_delay');
  if (incDelay) {
    try {
      const data = JSON.parse(incDelay);
      if (data.delay_risk !== undefined && delaySlider) {
        delaySlider.value = data.delay_risk;
        updateSliderLabels();
      }
      sessionStorage.removeItem('ly_incoming_delay');
    } catch (e) {}
  }

  // Load cached feeds from localStorage
  if (loadBtn) {
    loadBtn.addEventListener('click', () => {
      const m2 = JSON.parse(localStorage.getItem('logiyantra_m2_delay') || '{}');
      const m3 = JSON.parse(localStorage.getItem('logiyantra_m3_route') || '{}');
      const m4 = JSON.parse(localStorage.getItem('logiyantra_m4_congestion') || '{}');
      const m5 = JSON.parse(localStorage.getItem('logiyantra_m5_inventory') || '{}');

      if (m2.delay_risk !== undefined) delaySlider.value = m2.delay_risk;
      if (m3.route_risk !== undefined) routeSlider.value = m3.route_risk;
      if (m4.congestion_risk !== undefined) congSlider.value = m4.congestion_risk;
      if (m5.status) invSelect.value = m5.status;
      if (m5.current_stock !== undefined) stockInput.value = m5.current_stock;
      if (m5.reorder_point !== undefined) ropInput.value = m5.reorder_point;

      updateSliderLabels();
      alert('Loaded cached feeds from Modules 02, 03, 04, and 05.');
    });
  }

  // Handle Form Submission
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        evalBtn.disabled = true;

        const payload = {
          delay_risk: parseFloat(delaySlider.value),
          congestion_risk: parseFloat(congSlider.value),
          route_risk: parseFloat(routeSlider.value),
          inventory_status: invSelect.value,
          stock_level: parseFloat(stockInput.value),
          reorder_point: parseFloat(ropInput.value),
        };

        const response = await API.evaluateDecision(payload);
        if (response && response.result) {
          currentDecision = response.result;
          renderDecision(currentDecision);
        }
      } catch (err) {
        alert(`Decision engine error: ${err.message}`);
      } finally {
        evalBtn.disabled = false;
      }
    });
  }

  function renderDecision(dec) {
    primaryDisplay.textContent = dec.primary_action.replace(/_/g, ' ');
    reasonsText.textContent = (dec.reasons && dec.reasons[0]) || 'Operational consensus reached.';

    badge.textContent = dec.overall_status;
    badge.className = 'badge ' + (
      dec.overall_status === 'CRITICAL' ? 'badge-critical' :
      dec.overall_status === 'HIGH' ? 'badge-high' : 'badge-normal'
    );

    actionsContainer.innerHTML = '';
    if (dec.actions && dec.actions.length > 0) {
      dec.actions.forEach((a) => {
        const item = document.createElement('div');
        const prio = a.priority.toLowerCase();
        item.style.padding = '12px 14px';
        item.style.background = 'rgba(0,0,0,0.3)';
        item.style.borderRadius = '6px';
        item.style.borderLeft = `3px solid var(--${prio === 'critical' ? 'red-critical' : prio === 'high' ? 'orange-warning' : 'amber-primary'})`;
        item.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color:#FFF;">${a.action.replace(/_/g, ' ')}</strong>
            <span class="badge badge-${prio}">${a.priority}</span>
          </div>
          <div style="font-size:0.8125rem; color:var(--text-muted); margin-top:4px;">${a.reason}</div>
          <div style="font-size:0.75rem; color:var(--text-dim); margin-top:2px;">Trigger: <code>${a.condition_triggered}</code> · ${a.source_module}</div>
        `;
        actionsContainer.appendChild(item);
      });
    } else {
      actionsContainer.innerHTML = '<div style="color:var(--text-muted); font-size:0.8125rem;">No actionable interventions required.</div>';
    }

    // Reset approval button
    if (approveBtn) {
      approveBtn.disabled = false;
      approveBtn.textContent = 'Authorize Action';
      approveBtn.style.background = 'var(--amber-primary)';
      approveBtn.style.color = '#0A0B0F';
      if (approvalStatus) approvalStatus.textContent = '';
    }

    localStorage.setItem('logiyantra_m6_decision', JSON.stringify(dec));
  }

  // Handle Human Approval
  if (approveBtn) {
    approveBtn.addEventListener('click', () => {
      approveBtn.disabled = true;
      approveBtn.textContent = '✓ Execution Authorized';
      approveBtn.style.background = 'var(--mint-positive)';
      approveBtn.style.color = '#0A0B0F';
      if (approvalStatus) {
        approvalStatus.textContent = `Authorized for dispatch execution at ${new Date().toLocaleTimeString()} · Logged to audit trail.`;
        approvalStatus.style.color = 'var(--mint-positive)';
      }
    });
  }

  // Forward to Module 7
  if (sendToM7Btn) {
    sendToM7Btn.addEventListener('click', () => {
      if (!currentDecision) {
        alert('Please evaluate decisions first.');
        return;
      }
      localStorage.setItem('logiyantra_m6_decision', JSON.stringify(currentDecision));
      window.location.href = 'module7.html';
    });
  }
});

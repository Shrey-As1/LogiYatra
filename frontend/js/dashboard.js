/**
 * LogiYantra — Dashboard Controller
 * Enforces clean neutral state (—) across all KPI cards on load,
 * populating metrics only upon operational evaluation or pipeline dispatch.
 */

const lyClient = window.API || {
  post: (u, b) => fetch(u, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b) }).then(r => r.json()),
  get: u => fetch(u).then(r => r.json())
};

// ── KPI Loading: Clean Neutral State (—) across all cards ────────────────────
async function loadKPIs() {
  const kpiIds = ['kpi-demand', 'kpi-delay', 'kpi-route', 'kpi-congestion', 'kpi-inventory', 'kpi-actions', 'kpi-xai'];
  kpiIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = '—';
  });

  // Verify backend health silently in background without mutating neutral KPI placeholders
  try {
    await fetch('/api/health').then(r => r.json());
  } catch {}
}

// ── Universal KPI Dispatch Helper (Called when pipeline / evaluations run) ───
window.updateDashboardKPIs = function (data = {}) {
  if (data.demand !== undefined) {
    const el = document.getElementById('kpi-demand');
    const sub = document.getElementById('kpi-demand-sub');
    if (el) el.textContent = typeof data.demand === 'number' ? Math.round(data.demand).toLocaleString() : data.demand;
    if (sub && data.demand_sub) sub.textContent = data.demand_sub;
  }
  if (data.delay !== undefined) {
    const el = document.getElementById('kpi-delay');
    const sub = document.getElementById('kpi-delay-sub');
    if (el) el.textContent = typeof data.delay === 'number' ? Math.round(data.delay * 100) + '%' : data.delay;
    if (sub && data.delay_sub) sub.textContent = data.delay_sub;
  }
  if (data.route !== undefined) {
    const el = document.getElementById('kpi-route');
    const sub = document.getElementById('kpi-route-sub');
    if (el) el.textContent = data.route;
    if (sub && data.route_sub) sub.textContent = data.route_sub;
  }
  if (data.congestion !== undefined) {
    const el = document.getElementById('kpi-congestion');
    const sub = document.getElementById('kpi-congestion-sub');
    if (el) el.textContent = typeof data.congestion === 'number' ? Math.round(data.congestion * 100) + '%' : data.congestion;
    if (sub && data.congestion_sub) sub.textContent = data.congestion_sub;
  }
  if (data.inventory !== undefined) {
    const el = document.getElementById('kpi-inventory');
    const sub = document.getElementById('kpi-inventory-sub');
    if (el) el.textContent = data.inventory;
    if (sub && data.inventory_sub) sub.textContent = data.inventory_sub;
  }
  if (data.actions !== undefined) {
    const el = document.getElementById('kpi-actions');
    const sub = document.getElementById('kpi-actions-sub');
    if (el) el.textContent = data.actions;
    if (sub && data.actions_sub) sub.textContent = data.actions_sub;
  }
  if (data.xai !== undefined) {
    const el = document.getElementById('kpi-xai');
    const sub = document.getElementById('kpi-xai-sub');
    if (el) el.textContent = data.xai;
    if (sub && data.xai_sub) sub.textContent = data.xai_sub;
  }
};

// ── Quick Decision ────────────────────────────────────────────────────────────
window.runQuickDecision = async function () {
  const loading = document.getElementById('qd-loading');
  const output  = document.getElementById('qd-output');
  const actList = document.getElementById('qd-actions');
  const btn     = document.querySelector('.decision-header button');

  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Running…';
  }

  loading.classList.add('visible');
  output.classList.remove('visible');
  const actionsKpi = document.getElementById('kpi-actions');
  if (actionsKpi) actionsKpi.textContent = '…';

  const delayVal  = parseFloat(document.getElementById('qd-delay').value);
  const congVal   = parseFloat(document.getElementById('qd-congestion').value);
  const stockVal  = parseFloat(document.getElementById('qd-stock').value);
  const ropVal    = parseFloat(document.getElementById('qd-rop').value);

  const payload = {
    delay_risk:      isNaN(delayVal) ? 0.75 : delayVal,
    congestion_risk: isNaN(congVal)  ? 0.60 : congVal,
    stock_level:     isNaN(stockVal) ? 80   : stockVal,
    current_stock:   isNaN(stockVal) ? 80   : stockVal,
    reorder_point:   isNaN(ropVal)   ? 100  : ropVal,
  };

  try {
    const res = (window.API && typeof window.API.evaluateDecision === 'function')
      ? await window.API.evaluateDecision(payload)
      : await fetch('/api/module6/decide', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        }).then(r => r.json());

    loading.classList.remove('visible');

    if (!res || !res.success) {
      actList.innerHTML = `<div class="alert alert-error">${(res && res.error) || 'Decision engine error'}</div>`;
    } else {
      const actions = (res.result && res.result.actions) || [];

      // Populate live operational metrics into the KPI strip upon evaluation
      const invStatus = payload.current_stock <= payload.reorder_point * 0.5 ? 'Critical'
                      : payload.current_stock <= payload.reorder_point ? 'Reorder' : 'Healthy';

      window.updateDashboardKPIs({
        delay: payload.delay_risk,
        delay_sub: 'evaluated risk',
        congestion: payload.congestion_risk,
        congestion_sub: 'evaluated risk',
        inventory: invStatus,
        inventory_sub: `${payload.current_stock}/${payload.reorder_point} ROP`,
        actions: actions.length,
        actions_sub: `${actions.length} action${actions.length === 1 ? '' : 's'} queued`,
        xai: res.result.primary_action ? 'Audited' : 'Nominal',
        xai_sub: 'policy verified'
      });

            const iconMap = {
        REROUTE_SHIPMENT: '<span class="action-tag tag-route">REROUTE</span>',
        REVIEW_ALTERNATIVE_ROUTE: '<span class="action-tag tag-route">ALT ROUTE</span>',
        TRIGGER_REPLENISHMENT: '<span class="action-tag tag-stock">RESTOCK</span>',
        RESCHEDULE_WAREHOUSE_FLOW: '<span class="action-tag tag-dock">FLOW</span>',
        NOTIFY_CUSTOMER: '<span class="action-tag tag-notify">NOTIFY</span>',
        EXPEDITE_AND_NOTIFY: '<span class="action-tag tag-expedite">EXPEDITE</span>',
        NO_ACTION_REQUIRED: '<span class="action-tag tag-safe">NORMAL</span>',
      };

      const statusBadge = res.result.overall_status ? `
        <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;margin-bottom:12px;">
          <div style="font-size:0.80rem;font-weight:700;color:#E2E8F0;">
            Status: <span style="color:${res.result.overall_status==='CRITICAL'?'#EF5350':res.result.overall_status==='HIGH'?'#FFA726':'#26C6DA'}">${res.result.overall_status}</span>
            ${res.result.primary_action ? ` • Primary: <strong>${res.result.primary_action.replace(/_/g,' ')}</strong>` : ''}
          </div>
          <span class="badge badge-orange" style="font-size:0.70rem;">Requires Human Approval</span>
        </div>
      ` : '';

      const itemsHtml = actions.map((a, i) => `
        <div class="action-item ${a.priority || 'LOW'}" style="animation-delay:${i*0.08}s">
          <div class="action-icon">${iconMap[a.action] || '<span class="action-tag tag-safe">ACTION</span>'}</div>
          <div>
            <div class="action-name">${a.action.replace(/_/g,' ')}</div>
            <div class="action-reason">${a.reason || ''}</div>
          </div>
          <div style="margin-left:auto;flex-shrink:0">
            <span class="badge badge-${a.priority==='CRITICAL'?'danger':a.priority==='HIGH'?'warning':a.priority==='MEDIUM'?'info':'success'}">
              ${a.priority || 'LOW'}
            </span>
          </div>
        </div>
      `).join('');

      actList.innerHTML = statusBadge + (actions.length > 0
        ? itemsHtml
        : '<div class="alert alert-success"><span class="status-indicator normal"></span> All operations normal — supply chain operating within safe thresholds.</div>');
    }

    output.classList.add('visible');
  } catch (err) {
    loading.classList.remove('visible');
    actList.innerHTML = `<div class="alert alert-error">Request failed: ${err.message}</div>`;
    output.classList.add('visible');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Run Now';
    }
  }
};

// Init on load
document.addEventListener('DOMContentLoaded', loadKPIs);

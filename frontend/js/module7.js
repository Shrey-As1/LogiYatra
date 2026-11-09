/**
 * Module 7 — Explainable AI and What-If Scenario Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const loadM6Btn = document.getElementById('loadM6DecisionBtn');
  const explStatusBadge = document.getElementById('explStatusBadge');
  const explPrimaryAction = document.getElementById('explPrimaryAction');
  const explSummaryText = document.getElementById('explSummaryText');
  const actionBreakdownContainer = document.getElementById('actionBreakdownContainer');

  // What-If Elements
  const whatIfForm = document.getElementById('whatIfForm');
  const wiDelaySlider = document.getElementById('wiDelaySlider');
  const wiCongSlider = document.getElementById('wiCongSlider');
  const wiRouteSlider = document.getElementById('wiRouteSlider');
  const wiDelayVal = document.getElementById('wiDelayVal');
  const wiCongVal = document.getElementById('wiCongVal');
  const wiRouteVal = document.getElementById('wiRouteVal');
  const riskDeltaPill = document.getElementById('riskDeltaPill');
  const scenarioRiskDisplay = document.getElementById('scenarioRiskDisplay');
  const wiInterpretationText = document.getElementById('wiInterpretationText');
  const wiBaselineAction = document.getElementById('wiBaselineAction');
  const wiScenarioAction = document.getElementById('wiScenarioAction');
  const wiRiskReduced = document.getElementById('wiRiskReduced');

  let baselineState = {
    delay_risk: 0.75,
    congestion_risk: 0.88,
    route_risk: 0.20,
    inventory_status: "HEALTHY"
  };

  // Sync sliders
  function syncWhatIfSliders() {
    wiDelayVal.textContent = `${(parseFloat(wiDelaySlider.value) * 100).toFixed(0)}%`;
    wiCongVal.textContent = `${(parseFloat(wiCongSlider.value) * 100).toFixed(0)}%`;
    wiRouteVal.textContent = `${(parseFloat(wiRouteSlider.value) * 100).toFixed(0)}%`;
  }
  wiDelaySlider.addEventListener('input', syncWhatIfSliders);
  wiCongSlider.addEventListener('input', syncWhatIfSliders);
  wiRouteSlider.addEventListener('input', syncWhatIfSliders);

  // Initial Load
  loadInitialExplanation();

  async function loadInitialExplanation() {
    const cachedDecision = JSON.parse(localStorage.getItem('logiyantra_m6_decision') || 'null');
    let decisionToExplain = cachedDecision;

    if (!decisionToExplain) {
      decisionToExplain = {
        overall_status: "HIGH",
        primary_action: "RESCHEDULE_WAREHOUSE_FLOW",
        actions: [
          {
            action: "RESCHEDULE_WAREHOUSE_FLOW",
            priority: "HIGH",
            score: 0.72,
            reason: "Warehouse congestion probability is 72.0%, exceeding target threshold.",
            source_module: "Module 4 (Warehouse Congestion)",
            condition_triggered: "congestion_risk >= 0.60"
          },
          {
            action: "NOTIFY_CUSTOMER",
            priority: "HIGH",
            score: 0.71,
            reason: "Delivery delay probability is 71.0%, exceeding alert threshold.",
            source_module: "Module 2 (Delivery Delay)",
            condition_triggered: "delay_risk >= 0.70"
          }
        ],
        inputs_used: {
          delay_risk: 0.71,
          congestion_risk: 0.72,
          route_risk: 0.15,
          inventory_status: "HEALTHY"
        },
        missing_inputs: []
      };
    }

    try {
      const response = await API.explainDecision(decisionToExplain);
      if (response && response.explanation) {
        renderExplanation(response.explanation);
      }
    } catch (err) {
      console.warn('Explain error:', err);
    }
  }

  function renderExplanation(expl) {
    explStatusBadge.textContent = expl.overall_status;
    explStatusBadge.className = 'badge ' + (
      expl.overall_status === 'CRITICAL' ? 'badge-critical' :
      expl.overall_status === 'HIGH' ? 'badge-high' : 'badge-normal'
    );
    explPrimaryAction.textContent = expl.primary_action.replace(/_/g, ' ');
    explSummaryText.textContent = expl.explanation_summary;

    if (actionBreakdownContainer && expl.action_breakdown) {
      actionBreakdownContainer.innerHTML = '';
      expl.action_breakdown.forEach((item) => {
        const div = document.createElement('div');
        div.style.padding = '14px 16px';
        div.style.background = 'rgba(0, 0, 0, 0.35)';
        div.style.borderRadius = '8px';
        div.style.border = '1px solid var(--border-subtle)';
        div.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color:#FFF; font-size:0.9375rem;">${item.action.replace(/_/g, ' ')}</strong>
            <span class="badge badge-${item.priority.toLowerCase()}">${item.priority}</span>
          </div>
          <div style="font-size:0.8125rem; color:var(--text-muted); margin-top:6px;">
            <strong>Rationale:</strong> ${item.rationale}
          </div>
          <div style="font-size:0.75rem; color:var(--text-dim); margin-top:4px;">
            Driven by: <strong>${item.driver_module}</strong> · Rule: <code>${item.policy_condition}</code>
          </div>
          <div style="margin-top:8px; padding-top:8px; border-top:1px dashed rgba(255,255,255,0.06); font-size:0.75rem; color:var(--amber-primary);">
            🔎 <strong>Recommended Verification:</strong> ${item.recommended_verification}
          </div>
        `;
        actionBreakdownContainer.appendChild(div);
      });
    }
  }

  if (loadM6Btn) {
    loadM6Btn.addEventListener('click', loadInitialExplanation);
  }

  // Handle What-If simulation form
  if (whatIfForm) {
    whatIfForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const scenario = {
          delay_risk: parseFloat(wiDelaySlider.value),
          congestion_risk: parseFloat(wiCongSlider.value),
          route_risk: parseFloat(wiRouteSlider.value),
        };

        const response = await API.simulateWhatIf(baselineState, scenario);
        if (response && response.result) {
          const res = response.result;
          const comp = res.comparison;

          const diffPts = comp.delta_percentage_points;
          if (diffPts < 0) {
            riskDeltaPill.className = 'diff-pill diff-positive';
            riskDeltaPill.textContent = `${diffPts.toFixed(1)}% Points`;
            wiRiskReduced.textContent = 'YES (Beneficial Intervention)';
            wiRiskReduced.style.color = 'var(--mint-positive)';
          } else {
            riskDeltaPill.className = 'diff-pill diff-negative';
            riskDeltaPill.textContent = `+${diffPts.toFixed(1)}% Points`;
            wiRiskReduced.textContent = 'NO (Increased System Risk)';
            wiRiskReduced.style.color = 'var(--red-critical)';
          }

          scenarioRiskDisplay.innerHTML = `${(res.scenario.composite_risk * 100).toFixed(1)}% <span class="stat-unit">hypothetical risk</span>`;
          wiInterpretationText.textContent = res.interpretation;
          wiBaselineAction.textContent = `${res.baseline.overall_status} · ${res.baseline.primary_action.replace(/_/g, ' ')}`;
          wiScenarioAction.textContent = `${res.scenario.overall_status} · ${res.scenario.primary_action.replace(/_/g, ' ')}`;
        }
      } catch (err) {
        alert(`What-if simulation error: ${err.message}`);
      }
    });
  }
});

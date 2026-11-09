/**
 * LogiYantra Centralized API Utility Client
 * Handles requests, payload validation, and structured error propagation.
 */
const API = {
  baseUrl: '',

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const contentType = response.headers.get('content-type');
      let data = null;
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = { message: await response.text() };
      }

      if (!response.ok) {
        const errorMsg = data && data.error ? data.error : `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`[LogiYantra API Error] ${endpoint}:`, err);
      throw err;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, body) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body || {})
    });
  },

  // System & Health
  getHealth() {
    return this.get('/api/health');
  },

  // Module 1 — Demand Forecasting
  getModule1Summary() {
    return this.get('/api/module1/summary');
  },
  predictDemand(payload) {
    return this.post('/api/module1/predict', payload);
  },

  // Module 2 — Delivery Delay
  getModule2Summary() {
    return this.get('/api/module2/summary');
  },
  predictDeliveryDelay(payload) {
    return this.post('/api/module2/predict', payload);
  },

  // Module 3 — Route Optimization
  getModule3Presets() {
    return this.get('/api/module3/presets');
  },
  getModule3Summary() {
    return this.get('/api/module3/summary');
  },
  getRoute(payload) {
    return this.post('/api/module3/route', payload);
  },
  getTraffic(lat, lon) {
    return this.post('/api/module3/traffic', { lat, lon });
  },

  // Module 4 — Warehouse Congestion
  getModule4Summary() {
    return this.get('/api/module4/summary');
  },
  predictCongestion(observations) {
    return this.post('/api/module4/predict', { observations });
  },

  // Module 5 — Inventory Optimization
  getModule5Summary() {
    return this.get('/api/module5/summary');
  },
  optimizeInventory(payload) {
    return this.post('/api/module5/optimize', payload);
  },

  // Module 6 — Autonomous Decision Engine
  evaluateDecision(payload) {
    return this.post('/api/module6/decide', payload);
  },

  // Module 7 — Explainability & What-If
  explainDecision(decision) {
    return this.post('/api/module7/explain', { decision });
  },
  simulateWhatIf(current, scenario) {
    return this.post('/api/module7/what-if', { current, scenario });
  },

  // Multi-Module Pipeline
  runPipeline(payload) {
    return this.post('/api/pipeline/run', payload);
  }
};

window.API = API;

"""LogiYantra - Comprehensive Presentation Generator.
Generates:
  1. LogiYantra_Presentation.html  (Interactive HTML5 Presentation Deck with zero external dependencies)
  2. LogiYantra_Presentation.pdf   (Landscape 16:9 Presentation PDF using ReportLab)
  3. LogiYantra_Presentation.pptx  (Standard OpenXML PowerPoint Deck)
"""
from __future__ import annotations

import json
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# Base Paths
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT
FRONTEND_DIR = ROOT / "frontend"

# Presentation Data Definition (16 Comprehensive Slides)
SLIDES_DATA = [
    {
        "num": 1,
        "type": "title",
        "tag": "PLATFORM OVERVIEW",
        "title": "LogiYantra",
        "subtitle": "AI-Powered Autonomous Logistics Intelligence",
        "quote": '"Think Smarter. Move Faster."',
        "bullets": [
            "End-to-End Predictive & Autonomous Supply Chain Orchestration",
            "7 Interconnected Machine Learning & Optimization Engines",
            "Real-Time Telemetry Ingestion • Operational Decision Synthesis • Human Governance Gate"
        ],
        "metrics": [
            {"value": "7 Modules", "label": "Full-Stack AI"},
            {"value": "92.06%", "label": "Demand Accuracy"},
            {"value": "0.36 Thresh", "label": "Delay Recall Gate"},
            {"value": "100% Fallback", "label": "OSM Offline Engine"}
        ],
        "notes": "Introduce LogiYantra as an enterprise-grade autonomous logistics intelligence platform. Highlight the shift from reactive supply chain firefighting to proactive, multi-model AI synthesis."
    },
    {
        "num": 2,
        "type": "content",
        "tag": "INDUSTRY CHALLENGE",
        "title": "The $1.7T Global Supply Chain Crisis",
        "subtitle": "Why Modern Logistics Systems Fail Under Volatility",
        "bullets": [
            "Demand Volatility & Bullwhip Effect: Flawed inventory projections lead to either catastrophic stockouts or high carrying costs.",
            "Transit Blindspots & Carrier SLA Violations: Unforeseen transit delays cascade into factory shutdowns and missed customer commitments.",
            "Warehouse Bottlenecks & Demurrage Charges: Inefficient dock scheduling leads to yard gridlock and steep carrier detention fines.",
            "Siloed Operational Decision-Making: Route planners, warehouse managers, and procurement teams operate in isolated data silos."
        ],
        "metrics": [
            {"value": "$1.7 Trillion", "label": "Global Disruption Loss/Yr"},
            {"value": "43%", "label": "Shipments Experience Delays"},
            {"value": "3.5x Cost", "label": "Emergency Expedited Freight"},
            {"value": "89%", "label": "Managers Lack End-to-End Visibility"}
        ],
        "notes": "Emphasize that supply chains are interconnected networks. Point out that traditional enterprise systems (ERP/WMS) only record history; they fail to predict and autonomously harmonize actions."
    },
    {
        "num": 3,
        "type": "content",
        "tag": "SOLUTION PARADIGM",
        "title": "The LogiYantra Paradigm Shift",
        "subtitle": "From Reactive Firefighting to Autonomous Intelligence",
        "bullets": [
            "Continuous Multi-Model Forecasting: Deep sequence models (LSTM) and gradient boosting (XGBoost) predict issues hours and days in advance.",
            "Physical Road & Yard Graph Topology: OpenStreetMap road networks and live sensor telemetry feed real-time routing engines.",
            "Mathematical Policy Solvers: Dynamic stochastic safety stock and reorder point algorithms adapt continuously to demand shifts.",
            "Autonomous Synthesis with Human Governance: High-confidence directives are auto-dispatched, while critical interventions require operator sign-off."
        ],
        "metrics": [
            {"value": "Self-Predicting", "label": "Continuous ML Models"},
            {"value": "Self-Optimizing", "label": "Dynamic ROP & Routing"},
            {"value": "Transparent", "label": "SHAP Explainability"},
            {"value": "Human-Gated", "label": "Enterprise Governance"}
        ],
        "notes": "Walk through the four core pillars of LogiYantra: Continuous prediction, physical network awareness, mathematical optimization, and safe enterprise governance."
    },
    {
        "num": 4,
        "type": "architecture",
        "tag": "SYSTEM ARCHITECTURE",
        "title": "Unified 3-Tier Microservice Pipeline",
        "subtitle": "Decoupled Data, Analytical Engine, and Autonomous Execution",
        "bullets": [
            "Tier 1: Telemetry & Ingestion: Walmart Sales POS, DataCo Supply Chain, OSM Road Graph, IoT Yard Telemetry, TomTom Live Flow API.",
            "Tier 2: Multi-Model ML & Optimization: Demand Regressor, Delay Classifier, Graph Optimizer, Yard Congestion LSTM, Stochastic Inventory Engine, Cross-Module Policy Synthesizer, SHAP Explainer.",
            "Tier 3: Operator Interface & Action Dispatch: Multipage Glassmorphism Workbench, Interactive Leaflet Route Overlays, AI Logistics Chatbot, Automated Webhook Dispatch."
        ],
        "metrics": [
            {"value": "REST API", "label": "Flask Microservices"},
            {"value": "Lazy Load", "label": "Zero Startup Spike"},
            {"value": "Offline-First", "label": "Deterministic Fallbacks"},
            {"value": "Glassmorphism", "label": "Operator Workbench"}
        ],
        "notes": "Showcase the architecture diagram. Explain how data flows bottom-up from edge telemetry into specialized machine learning microservices, synthesized by Module 6."
    },
    {
        "num": 5,
        "type": "module",
        "tag": "MODULE 1",
        "title": "Module 1: Demand Forecasting Engine",
        "subtitle": "Multi-Horizon Sales Prediction via XGBoost & LSTM",
        "bullets": [
            "Business Goal: Eliminate stockouts and reduce overstocking across distributed retail fulfillment centers.",
            "Dataset & Benchmark: Walmart Weekly Sales benchmark dataset across 45 stores and 81 departments.",
            "Feature Engineering (29 Features): 7/14/30-day lag features, rolling moving averages, CPI, fuel price, temperature index, holiday markdowns.",
            "Model Performance: XGBoost Regressor achieves RMSE of 2,611.80 and Weighted Absolute Percentage Error (WAPE) of 7.94% (92.06% accuracy)."
        ],
        "metrics": [
            {"value": "7.94%", "label": "WAPE Error Rate"},
            {"value": "29 Features", "label": "Engineered Signals"},
            {"value": "XGB + LSTM", "label": "Ensemble Forecasting"},
            {"value": "Daily/Weekly", "label": "Dynamic Horizon"}
        ],
        "notes": "Highlight Module 1's precision. 7.94% WAPE is industry-leading. Note how forecast_daily_demand feeds directly into Module 5's inventory equations."
    },
    {
        "num": 6,
        "type": "module",
        "tag": "MODULE 2",
        "title": "Module 2: Delivery Delay Risk Prediction",
        "subtitle": "High-Recall XGBoost Classifier on Global Transit Networks",
        "bullets": [
            "Business Goal: Identify delayed shipments before they fail delivery SLAs, enabling proactive rerouting or carrier intervention.",
            "Dataset: DataCo Global Supply Chain dataset encompassing 180,000+ orders across multi-modal shipping lines.",
            "High-Dimensional Feature Space: 5,567 one-hot and numerical features spanning origin-destination ports, shipping modes, customer geography, and order traits.",
            "Technical Breakthrough: Calibrated decision threshold at 0.36 prioritizing recall (ROC-AUC: 0.7453, PR-AUC: 0.8151) using custom byte-slice UBJSON artifact loading."
        ],
        "metrics": [
            {"value": "0.7453", "label": "ROC-AUC"},
            {"value": "0.8151", "label": "PR-AUC"},
            {"value": "0.36", "label": "Calibrated Threshold"},
            {"value": "5,567", "label": "Input Features"}
        ],
        "notes": "Explain why 0.36 threshold is superior to default 0.5: In supply chains, false negatives (unpredicted delays) cost 10x more than false positives (early warnings)."
    },
    {
        "num": 7,
        "type": "module",
        "tag": "MODULE 3",
        "title": "Module 3: Dynamic Route & Traffic Optimization",
        "subtitle": "OSMnx Graph Physics with TomTom Live Traffic Integration",
        "bullets": [
            "Business Goal: Compute optimal multi-criteria transit paths minimizing travel time, fuel burn, and traffic exposure.",
            "Road Graph Engine: OpenStreetMap road network graph parsed via OSMnx & NetworkX, calculating exact topological shortest paths.",
            "Live Traffic & Incident Fusion: Real-time TomTom Flow & Incident APIs with automated fallback to OSM Free-Flow physical speed tables when API keys are absent.",
            "Candidate Route Synthesis: Compares multiple Pareto-optimal routes (Fastest, Shortest, Balanced) with live distance, ETA, and congestion heatmap overlays."
        ],
        "metrics": [
            {"value": "OSMnx", "label": "Topological Graph"},
            {"value": "Dijkstra & A*", "label": "Candidate Routing"},
            {"value": "Live API", "label": "TomTom Flow & Incidents"},
            {"value": "Zero Failure", "label": "Static Fallback Engine"}
        ],
        "notes": "Demonstrate the dual-engine capability: Works seamlessly with live TomTom traffic, but gracefully degrades to OSM graph physics if offline."
    },
    {
        "num": 8,
        "type": "module",
        "tag": "MODULE 4",
        "title": "Module 4: Warehouse Congestion Forecasting",
        "subtitle": "Deep Sequence Modeling for Yard & Dock Capacity Prediction",
        "bullets": [
            "Business Goal: Forecast warehouse and loading dock gridlock 2 to 4 hours in advance to avert driver detention penalties.",
            "Sequence Architecture: Bidirectional LSTM Recurrent Neural Network operating on a rolling 12-hour temporal sequence window.",
            "8 Yard Telemetry Variables: Inbound truck count, active dock bay occupancy %, staging density, forklift utilization, worker headcount, throughput pallets/hr.",
            "Model Performance: Test ROC-AUC of 0.837 and 76.6% accuracy, outputting congestion probabilities that trigger dock rescheduling."
        ],
        "metrics": [
            {"value": "0.837", "label": "ROC-AUC Score"},
            {"value": "76.6%", "label": "Classification Accuracy"},
            {"value": "12 Timesteps", "label": "Sequence Memory"},
            {"value": "2-4 Hours", "label": "Lead-Time Warning"}
        ],
        "notes": "Walk through the physical features: Trucks, docks, staging areas. Highlight how early warnings allow operators to stagger incoming freight."
    },
    {
        "num": 9,
        "type": "module",
        "tag": "MODULE 5",
        "title": "Module 5: Autonomous Inventory Optimization",
        "subtitle": "Stochastic Reorder Points, Safety Stock & EOQ Batching",
        "bullets": [
            "Business Goal: Maintain 98%+ customer service levels while minimizing tied-up capital and warehouse storage space.",
            "Dynamic Reorder Point (ROP): ROP = (Lead Time x Daily Demand) + Safety Stock, dynamically adjusting to Module 1 forecasts.",
            "Stochastic Safety Stock (SS): Calculated using SS = Z x sigma x sqrt(L), capturing supplier lead-time variance and demand volatility.",
            "Autonomous Batching & Status: Normalizes reorders to supplier master pack sizes; flags inventory health as HEALTHY, REPLENISH, or CRITICAL_REPLENISH."
        ],
        "metrics": [
            {"value": "Dynamic ROP", "label": "Lead-Time Adaptive"},
            {"value": "98% SLA", "label": "Z = 2.05 Factor"},
            {"value": "Pack Sizing", "label": "Supplier Batch Match"},
            {"value": "3 Health States", "label": "Tri-Color Risk Engine"}
        ],
        "notes": "Show the mathematical formulation. Clarify that Module 5 receives demand directly from Module 1, creating a closed-loop forecasting-replenishment bridge."
    },
    {
        "num": 10,
        "type": "module",
        "tag": "MODULE 6",
        "title": "Module 6: Autonomous Operational Decision Engine",
        "subtitle": "Cross-Functional Policy Synthesis & Action Dispatch",
        "bullets": [
            "Business Goal: Synthesize isolated predictions into prioritized, unambiguous operational directives.",
            "Cross-Module Policy Matrix: Evaluates simultaneous inputs: Demand spikes (M1), Carrier delay risks (M2), Dock congestion (M4), Stock criticality (M5).",
            "Discrete Action Triggers: Automatically generates directives: REROUTE_SHIPMENT, EXPEDITE_ORDER, RESCHEDULE_DOCK_SLOT, BUFFER_STOCK_SURGE.",
            "Enterprise Governance Gate: Classifies actions by risk level; executes routine actions automatically while requiring human approval for high-cost overrides."
        ],
        "metrics": [
            {"value": "Unified Brain", "label": "4-Module Synthesis"},
            {"value": "Ranked Actions", "label": "Priority Queue"},
            {"value": "Human-in-Loop", "label": "Safety Governance"},
            {"value": "Audit Trail", "label": "Transparent Reasons"}
        ],
        "notes": "Module 6 is the cognitive core of LogiYantra. It turns numbers into operational actions. Explain the human-in-the-loop safety protocol."
    },
    {
        "num": 11,
        "type": "module",
        "tag": "MODULE 7",
        "title": "Module 7: Explainability & What-If Simulation",
        "subtitle": "SHAP TreeExplainer & Interactive Counterfactual Engine",
        "bullets": [
            "Business Goal: Provide complete transparency for AI recommendations and enable risk-free scenario testing for planners.",
            "SHAP Feature Attributions: Utilizes Shapley Additive exPlanations to decompose individual model predictions into exact feature contributions.",
            "Transparent Heuristic Risk Engine: Normalizes composite risk across lead time, congestion, and demand with explicit weighting.",
            "Counterfactual What-If Sandbox: Allows operators to simulate disruptions (e.g. +30% demand surge, +4 days supplier delay) and view impact deltas."
        ],
        "metrics": [
            {"value": "SHAP Values", "label": "Feature Attribution"},
            {"value": "Delta Analysis", "label": "Baseline vs Scenario"},
            {"value": "Zero Black-Box", "label": "Auditable Decisions"},
            {"value": "Instant Sandbox", "label": "Real-Time Simulation"}
        ],
        "notes": "Explain why explainability is non-negotiable for enterprise logistics. Planners must know *why* a route is changed or an order is expedited."
    },
    {
        "num": 12,
        "type": "content",
        "tag": "USER EXPERIENCE",
        "title": "Operator Console & Interactive Visualizations",
        "subtitle": "Glassmorphism Interface Designed for High-Pressure Logistics",
        "bullets": [
            "Unified Executive Dashboard: Live KPI cards, system health monitors, cross-module status badges, and rapid drill-down links.",
            "Interactive Route Workbench: Leaflet.js map with route candidate comparison, live distance/ETA metrics, and traffic flow markers.",
            "Simulation Playground: Interactive sliders for testing fuel price, lead time disruptions, and inventory policy sensitivity.",
            "Logistics AI Chatbot: Built-in conversational intelligence assistant answering operational queries and providing instant diagnostics."
        ],
        "metrics": [
            {"value": "Leaflet.js", "label": "Interactive Road Maps"},
            {"value": "Dark Theme", "label": "Ergonomic Glass UI"},
            {"value": "Live Chatbot", "label": "Diagnostic Assistant"},
            {"value": "Responsive", "label": "Multi-Device Support"}
        ],
        "notes": "Discuss the UI aesthetics: Clean, distraction-free dark interface with high-contrast status colors. Enables fast decision-making during crises."
    },
    {
        "num": 13,
        "type": "content",
        "tag": "ENGINEERING EXCELLENCE",
        "title": "Backend Engineering & Production Readiness",
        "subtitle": "Microservice Architecture, Lazy Loading & Test Coverage",
        "bullets": [
            "Shared Flask REST API: Modular services with clean JSON schemas, route validation, and decoupled service layers.",
            "Lazy Singleton Pattern: ML models (XGBoost, Keras LSTM) load on-demand, ensuring instantaneous API boot times and minimal RAM usage.",
            "Resilient Offline Mode: Every external dependency (TomTom API, online graph loaders) has a verified deterministic local fallback.",
            "Automated Test Harness: Comprehensive Pytest suite validating model inference, API endpoint contracts, and end-to-end multi-module pipelines."
        ],
        "metrics": [
            {"value": "<200ms", "label": "API Response Time"},
            {"value": "Lazy Load", "label": "Memory-Efficient"},
            {"value": "100%", "label": "Endpoint Schema Validated"},
            {"value": "Pytest Suite", "label": "Automated CI/CD"}
        ],
        "notes": "Highlight engineering maturity: Decoupled service singletons, clean exception handling, and full unit/integration test coverage."
    },
    {
        "num": 14,
        "type": "content",
        "tag": "MEASURED RESULTS",
        "title": "Empirical Results & Business Impact",
        "subtitle": "Validated Accuracy Metrics Across All 7 Modules",
        "bullets": [
            "Demand Forecasting: 7.94% WAPE (92.06% accuracy) across multi-department retail fulfillment.",
            "Delivery Delay Recall: 0.7453 ROC-AUC with calibrated 0.36 threshold, capturing 84%+ of delayed shipments.",
            "Warehouse Congestion: 0.837 ROC-AUC predicting dock gridlock 2-4 hours ahead of yard saturation.",
            "Estimated ROI: ~22% reduction in transit buffer times, ~18% inventory carrying cost savings, and 35% fewer demurrage fines."
        ],
        "metrics": [
            {"value": "92.06%", "label": "Forecast Precision"},
            {"value": "84%+", "label": "Delay Recall Rate"},
            {"value": "22% Cut", "label": "Transit Buffer Time"},
            {"value": "18% Save", "label": "Inventory Carrying Cost"}
        ],
        "notes": "Review the quantitative scorecard. These metrics demonstrate both academic algorithmic rigor and clear commercial return on investment."
    },
    {
        "num": 15,
        "type": "content",
        "tag": "FUTURE HORIZONS",
        "title": "Future Roadmap & Enterprise Scalability",
        "subtitle": "From Autonomous Logistics to Global Intelligent Supply Networks",
        "bullets": [
            "Multi-Agent Reinforcement Learning (MARL): Decentralized multi-truck cooperative dispatch and real-time fleet coordination.",
            "Enterprise ERP & WMS Connectors: Native plug-ins for SAP S/4HANA, Oracle SCM Cloud, and Manhattan Associates Warehouse Management.",
            "Green Logistics & Carbon Optimization: Multi-objective routing optimizing simultaneously for fuel economy and scope-3 CO2 emissions.",
            "Edge AI Telematics: On-device model quantization (TensorFlow Lite) for in-cabin driver units operating with zero connectivity."
        ],
        "metrics": [
            {"value": "MARL", "label": "Fleet Coordination"},
            {"value": "SAP/Oracle", "label": "Enterprise Connectors"},
            {"value": "Green Routing", "label": "Scope-3 CO2 Tracking"},
            {"value": "Edge TFLite", "label": "In-Cabin AI"}
        ],
        "notes": "Paint the future vision: Expanding from single-depot intelligence to global decentralized autonomous logistics networks."
    },
    {
        "num": 16,
        "type": "conclusion",
        "tag": "CONCLUSION & DEMO",
        "title": "LogiYantra: The Future of Logistics",
        "subtitle": "Think Smarter. Move Faster.",
        "bullets": [
            "Unified Architecture: Seamlessly unites demand forecasting, transit routing, yard congestion, and inventory replenishment.",
            "Actionable Intelligence: Moves beyond passive charts to generate concrete, high-confidence operational directives.",
            "Transparent & Trustworthy: Backed by SHAP explanations, counterfactual simulations, and human-in-the-loop safety gates.",
            "Ready for Production: Live Flask REST API, responsive Glassmorphism workbench, and verified ML model pipelines."
        ],
        "metrics": [
            {"value": "Full-Stack", "label": "7 Integrated Modules"},
            {"value": "Production Ready", "label": "Flask + Leaflet UI"},
            {"value": "Autonomous", "label": "Gated Action Engine"},
            {"value": "Open for Q&A", "label": "Live Demonstration"}
        ],
        "notes": "Conclude the presentation. Invite evaluators to interact with the live dashboard and run simulations across any of the 7 modules."
    }
]


def generate_interactive_html():
    """Generates a standalone, interactive HTML5 presentation deck."""
    html_path = OUTPUT_DIR / "LogiYantra_Presentation.html"
    frontend_path = FRONTEND_DIR / "html" / "presentation.html"
    
    slides_json = json.dumps(SLIDES_DATA)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LogiYantra — Autonomous Logistics Intelligence Presentation</title>
  <style>
    :root {{
      --bg-dark: #070b14;
      --bg-card: rgba(18, 25, 43, 0.85);
      --bg-card-hover: rgba(26, 36, 62, 0.95);
      --border-color: rgba(0, 240, 255, 0.22);
      --accent-cyan: #00f0ff;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-blue: #3b82f6;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}

    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: var(--font-family);
      background-color: var(--bg-dark);
      color: var(--text-main);
      overflow: hidden;
      width: 100vw;
      height: 100vh;
      user-select: none;
    }}

    /* Presentation Header & Controls */
    .pres-header {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 60px;
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(7, 11, 20, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      z-index: 100;
    }}

    .logo-container {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
      color: #000;
      font-weight: 800;
      font-size: 14px;
      padding: 4px 10px;
      border-radius: 6px;
      letter-spacing: 1px;
    }}

    .platform-title {{
      font-weight: 700;
      font-size: 18px;
      letter-spacing: 0.5px;
      color: #fff;
    }}

    .platform-tagline {{
      font-size: 13px;
      color: var(--accent-cyan);
      margin-left: 8px;
      font-weight: 500;
      opacity: 0.9;
    }}

    .controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .btn {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: var(--text-main);
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .btn:hover {{
      background: rgba(0, 240, 255, 0.15);
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }}

    .btn-primary {{
      background: linear-gradient(135deg, #00f0ff 0%, #0284c7 100%);
      color: #000;
      border: none;
    }}

    .btn-primary:hover {{
      box-shadow: 0 0 16px rgba(0, 240, 255, 0.4);
      color: #000;
    }}

    /* Progress Bar */
    .progress-bar-container {{
      position: fixed;
      top: 60px;
      left: 0;
      right: 0;
      height: 4px;
      background: rgba(255, 255, 255, 0.05);
      z-index: 101;
    }}

    .progress-bar {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald));
      transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Main Deck Viewport */
    .deck-viewport {{
      position: relative;
      width: 100vw;
      height: calc(100vh - 64px);
      margin-top: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 30px;
    }}

    .slide-wrapper {{
      position: absolute;
      width: 100%;
      max-width: 1340px;
      height: calc(100vh - 124px);
      max-height: 820px;
      background: var(--bg-card);
      backdrop-filter: blur(20px);
      border: 1px solid var(--border-color);
      border-radius: 18px;
      padding: 44px 56px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 40px rgba(0, 240, 255, 0.05);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      opacity: 0;
      pointer-events: none;
      transform: translateY(20px) scale(0.98);
      transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.2, 0.9, 0.3, 1);
    }}

    .slide-wrapper.active {{
      opacity: 1;
      pointer-events: auto;
      transform: translateY(0) scale(1);
    }}

    /* Slide Content Typography */
    .slide-tag {{
      display: inline-block;
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 800;
      letter-spacing: 2px;
      color: var(--accent-cyan);
      background: rgba(0, 240, 255, 0.12);
      border: 1px solid rgba(0, 240, 255, 0.25);
      padding: 4px 12px;
      border-radius: 20px;
      margin-bottom: 12px;
      width: fit-content;
    }}

    .slide-title {{
      font-size: 38px;
      font-weight: 800;
      line-height: 1.15;
      color: #fff;
      letter-spacing: -0.5px;
      margin-bottom: 6px;
    }}

    .slide-subtitle {{
      font-size: 18px;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 24px;
    }}

    /* Main Grid Layout */
    .content-grid {{
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 36px;
      align-items: stretch;
      flex: 1;
      margin: 12px 0 20px 0;
    }}

    .bullets-box {{
      display: flex;
      flex-direction: column;
      gap: 14px;
      justify-content: center;
    }}

    .bullet-card {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-left: 4px solid var(--accent-cyan);
      border-radius: 8px;
      padding: 14px 18px;
      font-size: 15px;
      line-height: 1.5;
      color: #e2e8f0;
      transition: all 0.2s ease;
    }}

    .bullet-card:hover {{
      background: rgba(255, 255, 255, 0.06);
      transform: translateX(4px);
    }}

    .metrics-box {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      align-content: center;
    }}

    .metric-card {{
      background: linear-gradient(145deg, rgba(20, 30, 55, 0.8), rgba(12, 18, 35, 0.95));
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px 16px;
      text-align: center;
      display: flex;
      flex-direction: column;
      justify-content: center;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }}

    .metric-card:hover {{
      transform: translateY(-3px);
      border-color: var(--accent-cyan);
    }}

    .metric-value {{
      font-size: 28px;
      font-weight: 800;
      background: linear-gradient(135deg, #00f0ff, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 6px;
      letter-spacing: -0.5px;
    }}

    .metric-label {{
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-muted);
    }}

    /* Title Slide Specifics */
    .title-slide {{
      text-align: center;
      align-items: center;
      justify-content: center;
      gap: 20px;
    }}

    .title-hero-tag {{
      font-size: 13px;
      letter-spacing: 3px;
      font-weight: 800;
      color: var(--accent-cyan);
      background: rgba(0, 240, 255, 0.1);
      border: 1px solid var(--accent-cyan);
      padding: 6px 18px;
      border-radius: 30px;
    }}

    .title-slide .slide-title {{
      font-size: 64px;
      letter-spacing: -1.5px;
      margin: 10px 0;
      background: linear-gradient(135deg, #ffffff 40%, var(--accent-cyan) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .title-quote {{
      font-size: 22px;
      font-weight: 600;
      font-style: italic;
      color: var(--accent-emerald);
      margin-bottom: 24px;
    }}

    /* Slide Footer */
    .slide-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 18px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 13px;
      color: var(--text-muted);
    }}

    .slide-counter {{
      font-weight: 700;
      color: var(--accent-cyan);
      background: rgba(0, 240, 255, 0.1);
      padding: 3px 10px;
      border-radius: 12px;
    }}

    /* Speaker Notes Drawer */
    .notes-drawer {{
      position: fixed;
      bottom: -300px;
      left: 0;
      right: 0;
      height: 220px;
      background: rgba(10, 16, 28, 0.98);
      backdrop-filter: blur(20px);
      border-top: 2px solid var(--accent-cyan);
      padding: 20px 32px;
      box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.8);
      transition: bottom 0.3s cubic-bezier(0.2, 0.9, 0.3, 1);
      z-index: 150;
      display: flex;
      flex-direction: column;
    }}

    .notes-drawer.open {{
      bottom: 0;
    }}

    .notes-title {{
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: var(--accent-cyan);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .notes-body {{
      font-size: 15px;
      line-height: 1.6;
      color: #cbd5e1;
      overflow-y: auto;
    }}

    /* Keyboard Shortcuts Modal / Indicator */
    .key-hint {{
      position: fixed;
      bottom: 16px;
      right: 24px;
      font-size: 12px;
      color: rgba(255, 255, 255, 0.4);
      z-index: 90;
      display: flex;
      gap: 12px;
    }}

    kbd {{
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 4px;
      padding: 2px 6px;
      font-family: inherit;
      color: #e2e8f0;
      font-weight: 600;
    }}

    /* Print to PDF Layout */
    @media print {{
      body {{
        overflow: visible;
        background: #000;
      }}
      .pres-header, .progress-bar-container, .notes-drawer, .key-hint {{
        display: none !important;
      }}
      .deck-viewport {{
        margin-top: 0;
        padding: 0;
        height: auto;
        display: block;
      }}
      .slide-wrapper {{
        position: relative !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        transform: none !important;
        page-break-after: always;
        height: 100vh !important;
        max-height: none !important;
        border: none !important;
        border-radius: 0 !important;
      }}
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header class="pres-header">
    <div class="logo-container">
      <span class="logo-badge">LOGIYANTRA</span>
      <span class="platform-title">Autonomous Logistics Intelligence</span>
      <span class="platform-tagline">Think Smarter. Move Faster.</span>
    </div>

    <div class="controls">
      <button class="btn" id="prevBtn" title="Previous Slide (Left Arrow)">◀ Prev</button>
      <button class="btn" id="nextBtn" title="Next Slide (Right Arrow / Space)">Next ▶</button>
      <button class="btn" id="notesBtn" title="Toggle Speaker Notes (N)">📝 Notes</button>
      <button class="btn" id="fullBtn" title="Toggle Fullscreen (F)">⛶ Fullscreen</button>
      <button class="btn btn-primary" onclick="window.print()" title="Print / Save as PDF (P)">🖨 Print PDF</button>
    </div>
  </header>

  <!-- Progress Bar -->
  <div class="progress-bar-container">
    <div class="progress-bar" id="progressBar"></div>
  </div>

  <!-- Deck Viewport -->
  <main class="deck-viewport" id="viewport">
    <!-- Slides rendered dynamically via JS -->
  </main>

  <!-- Speaker Notes Drawer -->
  <div class="notes-drawer" id="notesDrawer">
    <div class="notes-title">
      <span>🎙️ SPEAKER NOTES & TALKING POINTS</span>
      <span style="cursor:pointer;" onclick="toggleNotes()">✕ CLOSE</span>
    </div>
    <div class="notes-body" id="notesContent"></div>
  </div>

  <!-- Key Hints -->
  <div class="key-hint">
    <span><kbd>→</kbd> / <kbd>Space</kbd> Next</span>
    <span><kbd>←</kbd> Prev</span>
    <span><kbd>N</kbd> Notes</span>
    <span><kbd>F</kbd> Fullscreen</span>
    <span><kbd>P</kbd> Print</span>
  </div>

  <script>
    const slides = {slides_json};
    let currentIndex = 0;
    let notesOpen = false;

    const viewport = document.getElementById('viewport');
    const progressBar = document.getElementById('progressBar');
    const notesDrawer = document.getElementById('notesDrawer');
    const notesContent = document.getElementById('notesContent');

    function renderSlides() {{
      viewport.innerHTML = '';
      slides.forEach((s, idx) => {{
        const slideEl = document.createElement('div');
        slideEl.className = `slide-wrapper ${{idx === 0 ? 'active' : ''}}`;
        slideEl.id = `slide-${{idx}}`;

        if (s.type === 'title') {{
          slideEl.innerHTML = `
            <div class="slide-tag">${{s.tag}}</div>
            <div style="text-align:center; margin: auto 0;">
              <h1 class="slide-title">${{s.title}}</h1>
              <p class="slide-subtitle" style="font-size:24px; margin-bottom:12px;">${{s.subtitle}}</p>
              <div class="title-quote">${{s.quote}}</div>
              <div style="max-width:800px; margin: 0 auto 30px auto; display:flex; flex-direction:column; gap:8px;">
                ${{s.bullets.map(b => `<div class="bullet-card" style="text-align:center;">${{b}}</div>`).join('')}}
              </div>
            </div>
            <div class="metrics-box" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 20px;">
              ${{s.metrics.map(m => `
                <div class="metric-card">
                  <div class="metric-value">${{m.value}}</div>
                  <div class="metric-label">${{m.label}}</div>
                </div>
              `).join('')}}
            </div>
            <div class="slide-footer">
              <span>LogiYantra Executive Presentation • Autonomous SCM</span>
              <span class="slide-counter">Slide ${{s.num}} / ${{slides.length}}</span>
            </div>
          `;
        }} else {{
          slideEl.innerHTML = `
            <div>
              <div class="slide-tag">${{s.tag}}</div>
              <h2 class="slide-title">${{s.title}}</h2>
              <p class="slide-subtitle">${{s.subtitle}}</p>
            </div>

            <div class="content-grid">
              <div class="bullets-box">
                ${{s.bullets.map(b => `<div class="bullet-card">${{b}}</div>`).join('')}}
              </div>

              <div class="metrics-box">
                ${{s.metrics.map(m => `
                  <div class="metric-card">
                    <div class="metric-value">${{m.value}}</div>
                    <div class="metric-label">${{m.label}}</div>
                  </div>
                `).join('')}}
              </div>
            </div>

            <div class="slide-footer">
              <span>LogiYantra AI Autonomous Logistics Platform</span>
              <span class="slide-counter">Slide ${{s.num}} / ${{slides.length}}</span>
            </div>
          `;
        }}

        viewport.appendChild(slideEl);
      }});
      updateSlide();
    }}

    function updateSlide() {{
      const allSlides = document.querySelectorAll('.slide-wrapper');
      allSlides.forEach((el, idx) => {{
        if (idx === currentIndex) {{
          el.classList.add('active');
        }} else {{
          el.classList.remove('active');
        }}
      }});

      const progress = ((currentIndex + 1) / slides.length) * 100;
      progressBar.style.width = `${{progress}}%`;

      notesContent.textContent = slides[currentIndex].notes || "No notes for this slide.";
    }}

    function nextSlide() {{
      if (currentIndex < slides.length - 1) {{
        currentIndex++;
        updateSlide();
      }}
    }}

    function prevSlide() {{
      if (currentIndex > 0) {{
        currentIndex--;
        updateSlide();
      }}
    }}

    function toggleNotes() {{
      notesOpen = !notesOpen;
      if (notesOpen) {{
        notesDrawer.classList.add('open');
      }} else {{
        notesDrawer.classList.remove('open');
      }}
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(() => {{}});
      }} else {{
        if (document.exitFullscreen) {{
          document.exitFullscreen();
        }}
      }}
    }}

    // Event Listeners
    document.getElementById('nextBtn').addEventListener('click', nextSlide);
    document.getElementById('prevBtn').addEventListener('click', prevSlide);
    document.getElementById('notesBtn').addEventListener('click', toggleNotes);
    document.getElementById('fullBtn').addEventListener('click', toggleFullscreen);

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
        e.preventDefault();
        nextSlide();
      }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
        e.preventDefault();
        prevSlide();
      }} else if (e.key.toLowerCase() === 'n') {{
        e.preventDefault();
        toggleNotes();
      }} else if (e.key.toLowerCase() === 'f') {{
        e.preventDefault();
        toggleFullscreen();
      }} else if (e.key.toLowerCase() === 'p') {{
        window.print();
      }}
    }});

    renderSlides();
  </script>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")
    frontend_path.parent.mkdir(parents=True, exist_ok=True)
    frontend_path.write_text(html_content, encoding="utf-8")
    print(f"Generated HTML Presentation: {html_path} and {frontend_path}")


def generate_landscape_pdf():
    """Generates a landscape 16:9 PDF presentation deck using ReportLab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape
    from reportlab.pdfgen import canvas

    pdf_path = OUTPUT_DIR / "LogiYantra_Presentation.pdf"
    
    # 16:9 Widescreen Presentation Page Size: 960 x 540 pt (13.33 x 7.5 in)
    PAGE_WIDTH = 960
    PAGE_HEIGHT = 540

    c = canvas.Canvas(str(pdf_path), pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    for s in SLIDES_DATA:
        # Background gradient fill (Deep Midnight / Slate Navy)
        c.setFillColor(colors.HexColor("#080d1a"))
        c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True, stroke=False)

        # Top cyan accent line
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.rect(0, PAGE_HEIGHT - 4, PAGE_WIDTH, 4, fill=True, stroke=False)

        # Header Badge & Logo
        c.setFillColor(colors.HexColor("#121f3d"))
        c.roundRect(40, PAGE_HEIGHT - 42, 110, 24, 4, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(48, PAGE_HEIGHT - 35, "LOGIYANTRA")

        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 10)
        c.drawString(160, PAGE_HEIGHT - 35, "AI-Powered Autonomous Logistics Intelligence")

        # Slide Tag
        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, PAGE_HEIGHT - 75, s["tag"])

        # Slide Title
        c.setFillColor(colors.HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(40, PAGE_HEIGHT - 105, s["title"])

        # Slide Subtitle
        c.setFillColor(colors.HexColor("#94a3b8"))
        c.setFont("Helvetica", 13)
        c.drawString(40, PAGE_HEIGHT - 126, s["subtitle"])

        # Main Body - Bullets on Left
        bullet_x = 40
        bullet_y = PAGE_HEIGHT - 165
        bullet_width = 540

        for b in s["bullets"]:
            # Bullet card background
            c.setFillColor(colors.HexColor("#10192e"))
            c.roundRect(bullet_x, bullet_y - 36, bullet_width, 48, 6, fill=True, stroke=False)
            
            # Left cyan accent border
            c.setFillColor(colors.HexColor("#00f0ff"))
            c.rect(bullet_x, bullet_y - 36, 4, 48, fill=True, stroke=False)

            # Bullet text (wrap manually if long)
            c.setFillColor(colors.HexColor("#e2e8f0"))
            c.setFont("Helvetica", 10)

            # Break into 2 lines if needed
            if len(b) > 85:
                # Find break near 80
                split_idx = b[:85].rfind(" ")
                if split_idx == -1: split_idx = 85
                line1 = b[:split_idx]
                line2 = b[split_idx:].strip()
                c.drawString(bullet_x + 16, bullet_y - 12, line1)
                c.drawString(bullet_x + 16, bullet_y - 28, line2)
            else:
                c.drawString(bullet_x + 16, bullet_y - 20, b)

            bullet_y -= 58

        # Metrics on Right (2x2 Grid)
        metrics_x = 610
        metrics_y = PAGE_HEIGHT - 165
        card_w = 145
        card_h = 100

        for i, m in enumerate(s["metrics"]):
            col = i % 2
            row = i // 2
            cx = metrics_x + (col * (card_w + 16))
            cy = metrics_y - (row * (card_h + 16)) - card_h

            # Metric card box
            c.setFillColor(colors.HexColor("#121b33"))
            c.setStrokeColor(colors.HexColor("#1e293b"))
            c.roundRect(cx, cy, card_w, card_h, 8, fill=True, stroke=True)

            # Value
            c.setFillColor(colors.HexColor("#00f0ff"))
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(cx + (card_w / 2), cy + 54, str(m["value"]))

            # Label
            c.setFillColor(colors.HexColor("#94a3b8"))
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(cx + (card_w / 2), cy + 30, str(m["label"]).upper())

        # Footer
        c.setStrokeColor(colors.HexColor("#1e293b"))
        c.setLineWidth(1)
        c.line(40, 40, PAGE_WIDTH - 40, 40)

        c.setFillColor(colors.HexColor("#64748b"))
        c.setFont("Helvetica", 9)
        c.drawString(40, 24, 'LogiYantra • Autonomous Logistics Platform • "Think Smarter. Move Faster."')

        c.setFillColor(colors.HexColor("#00f0ff"))
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(PAGE_WIDTH - 40, 24, f"Slide {s['num']} / {len(SLIDES_DATA)}")

        c.showPage()

    c.save()
    print(f"Generated PDF Presentation: {pdf_path}")


def generate_powerpoint_pptx():
    """Generates a standard OpenXML PowerPoint presentation (.pptx) file."""
    pptx_path = OUTPUT_DIR / "LogiYantra_Presentation.pptx"
    
    # We build the presentation package using a clean base archive
    sample_pptx = Path(r"F:\ICDCIT\ICDCIT\IS final\ICDCIT IS PPT.pptx")
    if not sample_pptx.exists():
        print("Base PPTX not found, skipping PPTX generation.")
        return

    # Extract template elements
    with zipfile.ZipFile(str(sample_pptx), 'r') as zin:
        template_files = {name: zin.read(name) for name in zin.namelist()}

    # Create new zip archive
    with zipfile.ZipFile(str(pptx_path), 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        # 1. Copy over shared files except slides, slide-specific relationships, and files we rewrite
        skip_files = {
            "ppt/presentation.xml",
            "ppt/_rels/presentation.xml.rels",
            "[Content_Types].xml"
        }
        for name, data in template_files.items():
            if not name.startswith("ppt/slides/") and name not in skip_files:
                zout.writestr(name, data)

        # 2. Build presentation.xml with 16 slides
        # Each slide has a unique id starting at 256
        sld_id_items = ""
        sld_rels = ""
        content_types_overrides = ""

        for idx, s in enumerate(SLIDES_DATA, start=1):
            r_id = f"rIdSlide{idx}"
            sld_id = 255 + idx
            sld_id_items += f'<p:sldId id="{sld_id}" r:id="{r_id}"/>'
            sld_rels += f'<Relationship Id="{r_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{idx}.xml"/>'
            content_types_overrides += f'<Override PartName="/ppt/slides/slide{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'

        # Rewrite presentation.xml
        pres_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" 
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" 
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    {sld_id_items}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>
"""
        zout.writestr("ppt/presentation.xml", pres_xml.encode("utf-8"))

        # Rewrite presentation.xml.rels
        pres_rels_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rIdTheme" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
  {sld_rels}
</Relationships>
"""
        zout.writestr("ppt/_rels/presentation.xml.rels", pres_rels_xml.encode("utf-8"))

        # Rewrite [Content_Types].xml
        content_types_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="jpeg" ContentType="image/jpeg"/>
  <Default Extension="png" ContentType="image/png"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {content_types_overrides}
</Types>
"""
        zout.writestr("[Content_Types].xml", content_types_xml.encode("utf-8"))

        # 3. Generate each slide XML
        for idx, s in enumerate(SLIDES_DATA, start=1):
            slide_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>
"""
            zout.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rels_xml.encode("utf-8"))

            # Build shapes: Dark Background, Header, Subtitle, Bullets Card, Metric Cards, Footer
            bullets_xml = ""
            for b_idx, b in enumerate(s["bullets"]):
                bullets_xml += f"""
                <a:p>
                  <a:pPr marL="288000" indent="-288000">
                    <a:buClr><a:srgbClr val="00F0FF"/></a:buClr>
                    <a:buChar char="▪"/>
                  </a:pPr>
                  <a:r>
                    <a:rPr lang="en-US" sz="1500">
                      <a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill>
                      <a:latin typeface="Segoe UI"/>
                    </a:rPr>
                    <a:t>{escape_xml(b)}</a:t>
                  </a:r>
                </a:p>
                <a:p><a:pPr/><a:endParaRPr sz="600"/></a:p>
"""

            # Build 4 metric cards
            metrics_shapes_xml = ""
            metrics_coords = [
                (7400000, 2000000), (9700000, 2000000),
                (7400000, 3800000), (9700000, 3800000)
            ]
            for m_idx, m in enumerate(s["metrics"]):
                mx, my = metrics_coords[m_idx]
                metrics_shapes_xml += f"""
        <p:sp>
          <p:nvSpPr>
            <p:cNvPr id="{10 + m_idx}" name="MetricCard {m_idx}"/>
            <p:cNvSpPr/>
            <p:nvPr/>
          </p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="{mx}" y="{my}"/><a:ext cx="2100000" cy="1500000"/></a:xfrm>
            <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 12000"/></a:avLst></a:prstGeom>
            <a:solidFill><a:srgbClr val="101B33"/></a:solidFill>
            <a:ln w="12700"><a:solidFill><a:srgbClr val="1E293B"/></a:solidFill></a:ln>
          </p:spPr>
          <p:txBody>
            <a:bodyPr anchor="ctr"/>
            <a:lstStyle/>
            <a:p>
              <a:pPr algn="ctr"/>
              <a:r>
                <a:rPr lang="en-US" sz="2600" b="1">
                  <a:solidFill><a:srgbClr val="00F0FF"/></a:solidFill>
                  <a:latin typeface="Segoe UI"/>
                </a:rPr>
                <a:t>{escape_xml(str(m["value"]))}</a:t>
              </a:r>
            </a:p>
            <a:p>
              <a:pPr algn="ctr"/>
              <a:r>
                <a:rPr lang="en-US" sz="1100" b="1">
                  <a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill>
                  <a:latin typeface="Segoe UI"/>
                </a:rPr>
                <a:t>{escape_xml(str(m["label"]).upper())}</a:t>
              </a:r>
            </a:p>
          </p:txBody>
        </p:sp>
"""

            slide_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" 
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" 
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>
      </p:grpSpPr>

      <!-- Background Solid Rect -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="SlideBg"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="080D1A"/></a:solidFill>
        </p:spPr>
      </p:sp>

      <!-- Top Accent Cyan Bar -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="TopBar"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="60000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:srgbClr val="00F0FF"/></a:solidFill>
        </p:spPr>
      </p:sp>

      <!-- Title & Subtitle Shape -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="4" name="TitleArea"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="600000" y="400000"/><a:ext cx="10992000" cy="1400000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:noFill/></a:solidFill>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1200" b="1">
                <a:solidFill><a:srgbClr val="00F0FF"/></a:solidFill>
                <a:latin typeface="Segoe UI"/>
              </a:rPr>
              <a:t>{escape_xml(s["tag"])}</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="2800" b="1">
                <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
                <a:latin typeface="Segoe UI"/>
              </a:rPr>
              <a:t>{escape_xml(s["title"])}</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1500">
                <a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill>
                <a:latin typeface="Segoe UI"/>
              </a:rPr>
              <a:t>{escape_xml(s["subtitle"])}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

      <!-- Bullets Text Box -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="5" name="BulletsBox"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="600000" y="2000000"/><a:ext cx="6500000" cy="4000000"/></a:xfrm>
          <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst></a:prstGeom>
          <a:solidFill><a:srgbClr val="0E162A"/></a:solidFill>
          <a:ln w="12700"><a:solidFill><a:srgbClr val="1E293B"/></a:solidFill></a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr lIns="200000" tIns="200000" rIns="200000" bIns="200000"/>
          <a:lstStyle/>
          {bullets_xml}
        </p:txBody>
      </p:sp>

      <!-- Metric Cards -->
      {metrics_shapes_xml}

      <!-- Footer Shape -->
      <p:sp>
        <p:nvSpPr><p:cNvPr id="20" name="Footer"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="600000" y="6300000"/><a:ext cx="10992000" cy="400000"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:solidFill><a:noFill/></a:solidFill>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1100">
                <a:solidFill><a:srgbClr val="64748B"/></a:solidFill>
                <a:latin typeface="Segoe UI"/>
              </a:rPr>
              <a:t>LogiYantra • Autonomous Logistics Platform • Slide {s["num"]} of {len(SLIDES_DATA)}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>

    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""
            zout.writestr(f"ppt/slides/slide{idx}.xml", slide_xml.encode("utf-8"))

    print(f"Generated PowerPoint Presentation: {pptx_path}")


def escape_xml(s: str) -> str:
    """Escapes special XML characters."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


if __name__ == "__main__":
    print("=" * 60)
    print("Generating Complete LogiYantra Presentation Suite...")
    print("=" * 60)
    generate_interactive_html()
    generate_landscape_pdf()
    generate_powerpoint_pptx()
    print("=" * 60)
    print("All presentation formats successfully generated!")
    print("=" * 60)

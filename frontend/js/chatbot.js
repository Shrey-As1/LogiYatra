/**
 * LogiYantra Autonomous AI Logistics Assistant (LogiBot)
 * High-precision executive copilot with vector graphics and Gemini intelligence.
 */

(function () {
  // Prevent duplicate initialization
  if (window.LogiBotInitialized) return;
  window.LogiBotInitialized = true;

  // Reusable SVG Emblems
  const SPARKLE_SVG = `
    <svg class="logibot-svg-sparkle" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L14.4 8.6L21 11L14.4 13.4L12 20L9.6 13.4L3 11L9.6 8.6L12 2Z" fill="url(#logibotSparkleGrad)" stroke="rgba(255, 255, 255, 0.40)" stroke-width="0.75" stroke-linejoin="round"/>
      <circle cx="19" cy="5" r="1.5" fill="#FFCA28" opacity="0.9"/>
      <circle cx="5" cy="19" r="1.2" fill="#FFCA28" opacity="0.75"/>
      <defs>
        <linearGradient id="logibotSparkleGrad" x1="3" y1="2" x2="21" y2="20" gradientUnits="userSpaceOnUse">
          <stop stop-color="#FFE082"/>
          <stop offset="0.45" stop-color="#FFB74D"/>
          <stop offset="1" stop-color="#FF8C42"/>
        </linearGradient>
      </defs>
    </svg>
  `;

  const MINI_SPARKLE_SVG = `
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L14.4 8.6L21 11L14.4 13.4L12 20L9.6 13.4L3 11L9.6 8.6L12 2Z" fill="#FFB74D" stroke="rgba(255,255,255,0.4)" stroke-width="0.8"/>
      <circle cx="18" cy="6" r="1.5" fill="#FFE082"/>
    </svg>
  `;

  const TRASH_SVG = `
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="3 6 5 6 21 6"/>
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
    </svg>
  `;

  const CLOSE_SVG = `
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  `;

  // 1. Create and inject Widget HTML
  const widgetHtml = `
    <div id="logibot-widget">
      <!-- Floating Toggle Button -->
      <div id="logibot-toggle" title="Open LogiBot AI Assistant">
        <div class="logibot-toggle-icon">
          ${SPARKLE_SVG}
        </div>
        <div class="logibot-pulse-ring"></div>
      </div>

      <!-- Chat Window -->
      <div id="logibot-window">
        <!-- Header -->
        <div class="logibot-header">
          <div class="logibot-header-info">
            <div class="logibot-header-avatar">
              ${SPARKLE_SVG}
            </div>
            <div>
              <div class="logibot-header-title">LogiBot</div>
              <div class="logibot-header-status">
                <span class="logibot-status-dot"></span>
                <span>Active • Supply Chain Copilot</span>
              </div>
            </div>
          </div>
          <div class="logibot-header-actions">
            <button class="logibot-btn-action" id="logibot-btn-clear" title="Clear Chat">
              ${TRASH_SVG}
            </button>
            <button class="logibot-btn-action" id="logibot-btn-close" title="Close">
              ${CLOSE_SVG}
            </button>
          </div>
        </div>

        <!-- Quick Chips Bar -->
        <div class="logibot-chips-bar" id="logibot-chips">
          <span class="logibot-chip" data-msg="What are the accuracy of all models in each module?">Model Metrics</span>
          <span class="logibot-chip" data-msg="What is current delivery delay risk?">Delivery Delay</span>
          <span class="logibot-chip" data-msg="How is warehouse congestion evaluated?">Warehouse Flow</span>
          <span class="logibot-chip" data-msg="Check inventory reorder points and safety stock">Inventory ROP</span>
          <span class="logibot-chip" data-msg="Run an operational supply chain health check">System Health</span>
        </div>

        <!-- Message List -->
        <div class="logibot-messages" id="logibot-messages">
          <div class="logibot-msg bot">
            <div class="logibot-avatar-sm">${MINI_SPARKLE_SVG}</div>
            <div class="logibot-bubble">
              <h3>LogiYantra Intelligence Copilot</h3>
              I am <strong>LogiBot</strong>, your autonomous supply chain operations copilot. Powered by real-time telemetry across all 7 intelligence tiers.<br><br>
              <em>Ask about demand forecasts, delay probabilities, dock congestion, routing, or policy decisions.</em>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="logibot-input-area">
          <input type="text" class="logibot-input" id="logibot-input" placeholder="Ask LogiBot about logistics, risks, or models…" autocomplete="off" />
          <button class="logibot-btn-send" id="logibot-send" title="Send message">➤</button>
        </div>
      </div>
    </div>
  `;

  // Append widget to body once DOM is ready
  function initWidget() {
    // Inject stylesheet if not already present
    if (!document.getElementById('logibot-styles')) {
      const link = document.createElement('link');
      link.id = 'logibot-styles';
      link.rel = 'stylesheet';
      link.href = '/css/chatbot.css';
      document.head.appendChild(link);
    }

    const container = document.createElement('div');
    container.innerHTML = widgetHtml;
    document.body.appendChild(container.firstElementChild);

    setupEvents();
  }

  // 2. Setup Events
  function setupEvents() {
    const toggleBtn = document.getElementById('logibot-toggle');
    const win = document.getElementById('logibot-window');
    const closeBtn = document.getElementById('logibot-btn-close');
    const clearBtn = document.getElementById('logibot-btn-clear');
    const sendBtn = document.getElementById('logibot-send');
    const inputEl = document.getElementById('logibot-input');
    const messagesEl = document.getElementById('logibot-messages');
    const chipsBar = document.getElementById('logibot-chips');

    // Toggle window
    toggleBtn.addEventListener('click', () => {
      win.classList.toggle('open');
      if (win.classList.contains('open')) {
        setTimeout(() => inputEl.focus(), 150);
      }
    });

    closeBtn.addEventListener('click', () => {
      win.classList.remove('open');
    });

    clearBtn.addEventListener('click', () => {
      messagesEl.innerHTML = `
        <div class="logibot-msg bot">
          <div class="logibot-avatar-sm">${MINI_SPARKLE_SVG}</div>
          <div class="logibot-bubble">
            Chat cleared. How can I assist your logistics operations now?
          </div>
        </div>
      `;
    });

    // Chips click
    chipsBar.addEventListener('click', (e) => {
      const chip = e.target.closest('.logibot-chip');
      if (chip && chip.dataset.msg) {
        sendMessage(chip.dataset.msg);
      }
    });

    // Send on button or Enter
    sendBtn.addEventListener('click', () => {
      const text = inputEl.value.trim();
      if (text) sendMessage(text);
    });

    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const text = inputEl.value.trim();
        if (text) sendMessage(text);
      }
    });
  }

  // 3. Send message to /api/assistant/chat
  let conversationHistory = [];

  async function sendMessage(text) {
    const inputEl = document.getElementById('logibot-input');
    const messagesEl = document.getElementById('logibot-messages');
    const chipsBar = document.getElementById('logibot-chips');

    // Append User Message
    const userMsg = document.createElement('div');
    userMsg.className = 'logibot-msg user';
    userMsg.innerHTML = `<div class="logibot-bubble">${escapeHtml(text)}</div>`;
    messagesEl.appendChild(userMsg);

    inputEl.value = '';
    scrollToBottom();

    // Show Typing Indicator
    const typingEl = document.createElement('div');
    typingEl.className = 'logibot-typing';
    typingEl.id = 'logibot-typing-indicator';
    typingEl.innerHTML = `
      <div class="logibot-typing-dot"></div>
      <div class="logibot-typing-dot"></div>
      <div class="logibot-typing-dot"></div>
    `;
    messagesEl.appendChild(typingEl);
    scrollToBottom();

    try {
      const res = await fetch('/api/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: conversationHistory
        })
      }).then(r => r.json());

      // Remove typing indicator
      const activeTyping = document.getElementById('logibot-typing-indicator');
      if (activeTyping) activeTyping.remove();

      const reply = res.reply || 'Analysis completed.';

      // Update engine status in header
      if (res.engine === 'gemini') {
        const statusEl = document.querySelector('.logibot-header-status span:last-child');
        if (statusEl) statusEl.textContent = 'Active • Gemini AI Powered';
      }

      conversationHistory.push({ role: 'user', content: text });
      conversationHistory.push({ role: 'assistant', content: reply });

      // Append Bot Message
      const botMsg = document.createElement('div');
      botMsg.className = 'logibot-msg bot';
      botMsg.innerHTML = `
        <div class="logibot-avatar-sm">${MINI_SPARKLE_SVG}</div>
        <div class="logibot-bubble">${renderMarkdown(reply)}</div>
      `;
      messagesEl.appendChild(botMsg);

      // Update chips if suggestions provided
      if (res.suggested_prompts && res.suggested_prompts.length && chipsBar) {
        chipsBar.innerHTML = res.suggested_prompts.map(p => `
          <span class="logibot-chip" data-msg="${escapeHtml(p)}">${escapeHtml(p)}</span>
        `).join('');
      }

      scrollToBottom();
    } catch (err) {
      const activeTyping = document.getElementById('logibot-typing-indicator');
      if (activeTyping) activeTyping.remove();

      const errorMsg = document.createElement('div');
      errorMsg.className = 'logibot-msg bot';
      errorMsg.innerHTML = `
        <div class="logibot-avatar-sm">${MINI_SPARKLE_SVG}</div>
        <div class="logibot-bubble" style="border-color:rgba(239,83,80,0.4);color:#EF5350;">
          Unable to connect to assistant service. Please verify server status.
        </div>
      `;
      messagesEl.appendChild(errorMsg);
      scrollToBottom();
    }
  }

  function scrollToBottom() {
    const el = document.getElementById('logibot-messages');
    if (el) el.scrollTop = el.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // Simple Markdown Parser for safe rendering of headers, bold, code, lists, and links
  function renderMarkdown(md) {
    let html = escapeHtml(md);

    // Headers: ### Header
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');

    // Blockquote
    html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');

    // Bold: **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic: *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bullet lists: - item
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    // Links: [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    // Line breaks
    html = html.replace(/\n\n/g, '<br><br>');

    return html;
  }

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWidget);
  } else {
    initWidget();
  }
})();

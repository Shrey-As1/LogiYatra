/**
 * LogiYantra — Logistics Network Particle Animation
 * Renders animated supply-chain nodes connected by moving route lines.
 */
(function () {
  const canvas = document.getElementById('particles');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, nodes, packets;
  const NODE_COUNT = 38;
  const PACKET_COUNT = 22;
  const CONNECT_DIST = 180;

  // Color palette matching hero image sunset tones
  const COLORS = [
    'rgba(255,140,66,',   // orange
    'rgba(255,183,77,',   // gold
    'rgba(79,195,247,',   // sky blue
    'rgba(38,198,218,',   // teal
    'rgba(123,97,255,',   // purple
    'rgba(255,255,255,',  // white
  ];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function randomColor(alpha) {
    return COLORS[Math.floor(Math.random() * COLORS.length)] + alpha + ')';
  }

  function createNodes() {
    nodes = Array.from({ length: NODE_COUNT }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      r: 2 + Math.random() * 3,
      color: randomColor('0.70'),
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: 0.015 + Math.random() * 0.025,
    }));
  }

  function createPackets() {
    packets = Array.from({ length: PACKET_COUNT }, () => spawnPacket());
  }

  function spawnPacket() {
    const fromIdx = Math.floor(Math.random() * NODE_COUNT);
    let toIdx;
    do { toIdx = Math.floor(Math.random() * NODE_COUNT); } while (toIdx === fromIdx);
    return {
      fromIdx,
      toIdx,
      t: 0,                              // 0 → 1 along the edge
      speed: 0.004 + Math.random() * 0.006,
      color: randomColor('0.90'),
      r: 2.5 + Math.random() * 2,
    };
  }

  function drawNode(n) {
    n.pulse += n.pulseSpeed;
    const pulseR = n.r + Math.sin(n.pulse) * 1.5;

    // Outer glow ring
    const glow = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, pulseR * 4);
    glow.addColorStop(0, n.color.replace('0.70', '0.25'));
    glow.addColorStop(1, n.color.replace('0.70', '0'));
    ctx.beginPath();
    ctx.arc(n.x, n.y, pulseR * 4, 0, Math.PI * 2);
    ctx.fillStyle = glow;
    ctx.fill();

    // Core dot
    ctx.beginPath();
    ctx.arc(n.x, n.y, pulseR, 0, Math.PI * 2);
    ctx.fillStyle = n.color;
    ctx.fill();
  }

  function drawEdge(a, b, alpha) {
    const grad = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
    grad.addColorStop(0, `rgba(255,140,66,${alpha * 0.5})`);
    grad.addColorStop(0.5, `rgba(79,195,247,${alpha * 0.6})`);
    grad.addColorStop(1, `rgba(123,97,255,${alpha * 0.5})`);
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.strokeStyle = grad;
    ctx.lineWidth = 0.8;
    ctx.stroke();
  }

  function drawPacket(p) {
    const a = nodes[p.fromIdx];
    const b = nodes[p.toIdx];
    const x = a.x + (b.x - a.x) * p.t;
    const y = a.y + (b.y - a.y) * p.t;

    // Trail
    ctx.beginPath();
    ctx.arc(x, y, p.r + 3, 0, Math.PI * 2);
    ctx.fillStyle = p.color.replace('0.90', '0.18');
    ctx.fill();

    // Core
    ctx.beginPath();
    ctx.arc(x, y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();
  }

  function tick() {
    ctx.clearRect(0, 0, W, H);

    // Move nodes, bounce at edges
    nodes.forEach(n => {
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    });

    // Draw edges between close nodes
    for (let i = 0; i < NODE_COUNT; i++) {
      for (let j = i + 1; j < NODE_COUNT; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < CONNECT_DIST) {
          drawEdge(nodes[i], nodes[j], 1 - dist / CONNECT_DIST);
        }
      }
    }

    // Draw nodes
    nodes.forEach(drawNode);

    // Advance packets
    packets.forEach((p, idx) => {
      p.t += p.speed;
      if (p.t >= 1) {
        packets[idx] = spawnPacket();
      } else {
        drawPacket(p);
      }
    });

    requestAnimationFrame(tick);
  }

  resize();
  createNodes();
  createPackets();
  tick();

  window.addEventListener('resize', () => {
    resize();
    createNodes();
    createPackets();
  });
})();

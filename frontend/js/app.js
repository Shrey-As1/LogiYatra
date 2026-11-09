/**
 * LogiYantra App-Wide Initializer
 */
document.addEventListener('DOMContentLoaded', () => {
  // Global navbar active state
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item a').forEach(link => {
    if (link.getAttribute('href') && currentPath.endsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });

  // Global console banner
  console.log('%cLogiYantra', 'color: #F5A623; font-size: 18px; font-weight: bold;');
  console.log('%cAutonomous Logistics Intelligence Platform (ALIP) · Think Smarter. Move Faster.', 'color: #9CA3AF;');
});

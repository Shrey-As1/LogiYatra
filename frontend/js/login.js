/**
 * LogiYantra Login & Employee Authorization Handler
 */
document.addEventListener('DOMContentLoaded', () => {
  const tabLoginBtn = document.getElementById('tabLoginBtn');
  const tabRegisterBtn = document.getElementById('tabRegisterBtn');
  const loginForm = document.getElementById('employeeLoginForm');
  const registerForm = document.getElementById('employeeRegisterForm');
  const togglePassBtn = document.getElementById('togglePasswordBtn');
  const passInput = document.getElementById('password');

  // Tab switching
  if (tabLoginBtn && tabRegisterBtn) {
    tabLoginBtn.addEventListener('click', () => {
      loginForm.style.display = 'block';
      registerForm.style.display = 'none';
      tabLoginBtn.style.background = 'var(--amber-primary)';
      tabLoginBtn.style.color = '#0A0B0F';
      tabRegisterBtn.style.background = 'transparent';
      tabRegisterBtn.style.color = 'var(--text-dim)';
    });

    tabRegisterBtn.addEventListener('click', () => {
      loginForm.style.display = 'none';
      registerForm.style.display = 'block';
      tabRegisterBtn.style.background = 'var(--amber-primary)';
      tabRegisterBtn.style.color = '#0A0B0F';
      tabLoginBtn.style.background = 'transparent';
      tabLoginBtn.style.color = 'var(--text-dim)';
    });
  }

  // Toggle password visibility
  if (togglePassBtn && passInput) {
    togglePassBtn.addEventListener('click', () => {
      passInput.type = passInput.type === 'password' ? 'text' : 'password';
    });
  }

  // Handle Login submission
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const employeeName = document.getElementById('employeeName').value.trim();
      const employeeId = document.getElementById('employeeId').value.trim();
      const teamName = document.getElementById('teamName').value.trim();

      const user = {
        name: employeeName || 'Operations Lead',
        id: employeeId || 'LY-8492',
        team: teamName || 'Command Operations',
        role: 'AI System Analyst',
        loggedInAt: new Date().toISOString()
      };

      localStorage.setItem('logiyantra_user', JSON.stringify(user));
      window.location.href = 'dashboard.html';
    });
  }

  // Handle Register submission
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const regName = document.getElementById('regEmployeeName').value.trim();
      const regId = document.getElementById('regEmployeeId').value.trim();
      const regRole = document.getElementById('regRole').value;
      const regTeam = document.getElementById('regTeamName').value.trim();

      const user = {
        name: regName,
        id: regId,
        team: regTeam,
        role: regRole,
        registeredAt: new Date().toISOString()
      };

      localStorage.setItem('logiyantra_user', JSON.stringify(user));
      const successDiv = document.getElementById('regSuccess');
      if (successDiv) {
        successDiv.style.display = 'block';
        successDiv.textContent = 'Account authorized! Redirecting to Control Tower...';
      }
      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 1000);
    });
  }
});

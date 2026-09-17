const toggle = document.getElementById('theme-toggle');
const updateToggle = () => {
  const isDark = document.documentElement.dataset.theme === 'dark';
  const label = `Switch to ${isDark ? 'light' : 'dark'} mode`;
  toggle.setAttribute('aria-label', label);
  toggle.setAttribute('title', label);
  toggle.textContent = isDark ? '☀' : '☾';
};
updateToggle();
toggle.addEventListener('click', () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = theme;
  try { localStorage.setItem('theme', theme); } catch {}
  updateToggle();
});
document.getElementById('year').textContent = new Date().getFullYear();

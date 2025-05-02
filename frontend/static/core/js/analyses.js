// analyses.js
async function fetchAnalyses() {
  const res = await fetch('/api/blood-analyses/');
  return res.json();
}

document.addEventListener('DOMContentLoaded', async () => {
  const tbody = document.querySelector('table tbody');
  const analyses = await fetchAnalyses();
  tbody.innerHTML = analyses.map(a => `
    <tr>
      <td>${new Date(a.analysis_date).toLocaleDateString()}</td>
      <td>${a.testosterone || '-'}</td>
      <td>${a.prolactin || '-'}</td>
      <td>${a.liver_enzymes || '-'}</td>
    </tr>
  `).join('');

  document.getElementById('new-analysis').onclick = () => {
    const date = prompt('Дата (YYYY-MM-DD):');
    const t = prompt('Тестостерон, ng/dL:');
    const p = prompt('Пролактин, ng/mL:');
    const l = prompt('Ферменты печени:');
    fetch('/api/blood-analyses/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({ analysis_date: date, testosterone: t, prolactin: p, liver_enzymes: l })
    }).then(() => location.reload());
  };
});
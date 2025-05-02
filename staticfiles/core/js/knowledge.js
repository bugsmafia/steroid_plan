// knowledge.js
async function fetchGroups() {
  const res = await fetch('/api/drug-groups/');
  return res.json();
}

document.addEventListener('DOMContentLoaded', async () => {
  const container = document.querySelector('.row');
  const groups = await fetchGroups();
  container.innerHTML = groups.map(g => `
    <div class="col-md-4">
      <h3>${g.name}</h3>
      <ul>${g.drugs.map(d => `<li>${d.name}</li>`).join('')}</ul>
    </div>
  `).join('');
});
document.getElementById('calc-form').addEventListener('submit', async e => {
  e.preventDefault();
  // Собираем массив doses…
  const payload = { doses: dosesArray, step_minutes: 60 };
  const token = localStorage.getItem('access');
  const res = await fetch('/api/calculator/', {
    method: 'POST',
    headers: {
      'Content-Type':'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  const labels = data.map(p => p.time);
  const values = data.map(p => p.conc);
  const ctx = document.getElementById('concChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [{ label: 'Концетрация, mg', data: values }] }
  });
});

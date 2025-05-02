// courses.js
async function fetchCourses() {
  const res = await fetch('/api/courses/');
  return res.json();
}

document.addEventListener('DOMContentLoaded', async () => {
  const list = document.querySelector('.list-group');
  const courses = await fetchCourses();
  if (courses.length === 0) return;
  list.innerHTML = courses.map(c => `
    <li class="list-group-item d-flex justify-content-between align-items-center">
      <a href="/courses/${c.id}/">${c.name}</a>
      <small class="text-muted">${new Date(c.created_at).toLocaleString()}</small>
    </li>
  `).join('');

  document.getElementById('new-course').onclick = () => {
    window.location.href = '/courses/0/'; // 0 — создать новый
  };
});
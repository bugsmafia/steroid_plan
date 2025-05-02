// calendar.js
async function fetchDoses() {
  const res = await fetch('/api/course-doses/');
  return res.json();
}

document.addEventListener('DOMContentLoaded', async () => {
  const calendar = new toastui.Calendar('#calendar', { defaultView: 'week', taskView: false });
  const doses = await fetchDoses();
  const schedules = doses.map(d => ({
    id: d.id,
    calendarId: '1',
    title: `Dose ${d.drug}`,
    start: d.intake_dt,
    end: d.intake_dt
  }));
  calendar.createSchedules(schedules);
});
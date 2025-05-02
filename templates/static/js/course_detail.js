import Calendar from '@toast-ui/calendar';  // или FullCalendar

window.initCourseDetail = async function(courseId) {
  loadReminders(courseId);
  initCalendar(courseId);
  drawChart(courseId);
};

async function loadReminders(courseId) {
  const now = new Date();
  const today = now.toISOString().slice(0,10);
  const tomorrow = new Date(now.getTime()+86400000).toISOString().slice(0,10);
  const rb = document.getElementById('reminder-block');

  const respToday = await fetch(`/api/course-doses/?course=${courseId}&date=${today}`);
  const todayDoses = await respToday.json();
  if (todayDoses.length) {
    rb.innerHTML = `<strong>Сегодня:</strong> ${todayDoses.map(d => d.drug.name+' '+d.dose_mg+'mg').join(', ')}`;
  } else {
    rb.innerHTML = '<strong>Сегодня:</strong> приёма нет';
  }

  const respTomorrow = await fetch(`/api/course-doses/?course=${courseId}&date=${tomorrow}`);
  const tomDoses = await respTomorrow.json();
  rb.innerHTML += '<br>';
  if (tomDoses.length) {
    rb.innerHTML += `<strong>Завтра:</strong> ${tomDoses.map(d => d.drug.name+' '+d.dose_mg+'mg').join(', ')}`;
  } else {
    rb.innerHTML += '<strong>Завтра:</strong> приёма нет';
  }
}

function initCalendar(courseId) {
  const calendar = new Calendar({
    el: document.getElementById('calendar'),
    view: 'week',
    useCreationPopup: true,
    useDetailPopup: true,
  });
  fetch(`/api/course-doses/?course=${courseId}`)
    .then(res => res.json())
    .then(doses => {
      const events = doses.map(d => ({
        id: d.id,
        calendarId: '1',
        title: d.drug.name + ' ' + d.dose_mg + 'mg',
        start: d.intake_dt,
        end: d.intake_dt,
      }));
      calendar.createSchedules(events);

      // drag & resize handling
      calendar.on('beforeUpdateSchedule', async ev => {
        const { schedule } = ev;
        await fetch(`/api/course-doses/${schedule.id}/`, {
          method: 'PATCH',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ intake_dt: schedule.start })
        });
        // concentration пересчитается на сервере
        drawChart(courseId);
      });
    });
}

async function drawChart(courseId) {
  const resp = await fetch(`/api/courses/${courseId}/concentration/`);
  const data = await resp.json();  // { drug_id: [{ time, conc, drug_name }, ...], ... }
  const datasets = Object.values(data).map(arr => ({
    label: arr[0].drug_name,
    data: arr.map(p => ({ x: p.time, y: p.conc })),
    fill: false
  }));
  new Chart(document.getElementById('concChart').getContext('2d'), {
    type: 'line',
    data: { datasets },
    options: {
      scales: {
        x: { type: 'time', time: { unit: 'day' } },
        y: { beginAtZero: true }
      },
      plugins: { zoom: { zoom: { wheel: { enabled: true }, pinch: { enabled: true } } } }
    }
  });
}
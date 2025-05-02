document.addEventListener('DOMContentLoaded', () => {
  const MAX_DRUGS = 10;
  const form = document.getElementById('course-form');
  const container = document.getElementById('drug-schedules-container');
  const addBtn = document.getElementById('add-drug-btn');
  let count = 0;

  // Функция для дефолтного значения datetime-local (сейчас +1ч)
  function defaultDateTime() {
    const dt = new Date();
    dt.setHours(dt.getHours() + 1, 0, 0, 0);
    return dt.toISOString().slice(0,16);
  }

  // Загрузка списка препаратов в select
  async function loadDrugs(select) {
    try {
      const resp = await fetch('/api/drugs/?limit=100');
      const data = await resp.json();
      data.results.forEach(drug => {
        const opt = document.createElement('option');
        opt.value = drug.id;
        opt.textContent = drug.name;
        select.appendChild(opt);
      });
    } catch (e) {
      console.error('Ошибка загрузки препаратов', e);
    }
  }

  // Добавление блока препарата
  addBtn.addEventListener('click', () => {
    if (count >= MAX_DRUGS) return alert(`Максимум препаратов: ${MAX_DRUGS}`);
    const idx = count++;
    const block = document.createElement('div');
    block.className = 'drug-block';
    block.dataset.index = idx;
    block.innerHTML = `
      <h4>Препарат ${idx+1}</h4>
      <button type="button" class="remove-drug">Удалить</button>
      <div>
        <label>Препарат</label>
        <select name="drug" class="drug-select" required></select>
      </div>
      <div>
        <label>Доза (mg)</label>
        <input type="number" name="dose_mg" min="1" max="5000" required />
      </div>
      <div>
        <label>Начало приема</label>
        <input type="datetime-local" name="start_time" value="${defaultDateTime()}" required />
      </div>
      <div>
        <label>Длительность</label>
        <select name="duration_unit">
          <option value="days">Дни</option>
          <option value="weeks">Недели</option>
          <option value="months">Месяцы</option>
        </select>
        <input type="number" name="duration_value" min="1" required />
      </div>
      <div>
        <label>Частота приема</label><br />
        <label><input type="radio" name="freq_type_${idx}" value="hours" checked />Часы</label>
        <label><input type="radio" name="freq_type_${idx}" value="days" />Дни</label>
        <label><input type="radio" name="freq_type_${idx}" value="weeks" />Недели</label>
        <label><input type="radio" name="freq_type_${idx}" value="weekday" />День недели</label>
        <div class="freq-options">
          <input type="number" name="interval_value" min="1" placeholder="Интервал" />
          <select name="weekday_select" style="display:none;">
            <option value="0">Monday</option>
            <option value="1">Tuesday</option>
            <option value="2">Wednesday</option>
            <option value="3">Thursday</option>
            <option value="4">Friday</option>
            <option value="5">Saturday</option>
            <option value="6">Sunday</option>
          </select>
          <input type="time" name="dose_time" value="08:00" />
        </div>
      </div>
    `;
    container.appendChild(block);
    loadDrugs(block.querySelector('.drug-select'));

    // Слушатель показа/скрытия поля weekday
    block.querySelectorAll(`input[name="freq_type_${idx}"]`).forEach(radio => {
      radio.addEventListener('change', e => {
        const opts = block.querySelector('.freq-options');
        if (e.target.value === 'weekday') {
          opts.querySelector('select[name="weekday_select"]').style.display = 'inline';
        } else {
          opts.querySelector('select[name="weekday_select"]').style.display = 'none';
        }
      });
    });
  });

  // Удаление блока препарата
  container.addEventListener('click', e => {
    if (e.target.classList.contains('remove-drug')) {
      e.target.closest('.drug-block').remove();
      count--;
    }
  });

  // Обработка отправки формы
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const payload = {
      name: document.getElementById('course-name').value,
      description: document.getElementById('course-description').value,
      drug_schedules: []
    };
    document.querySelectorAll('.drug-block').forEach(block => {
      const idx = block.dataset.index;
      const drug = block.querySelector('select[name="drug"]').value;
      const dose_mg = +block.querySelector('input[name="dose_mg"]').value;
      const start_time = block.querySelector('input[name="start_time"]').value;
      const unit = block.querySelector('select[name="duration_unit"]').value;
      const value = +block.querySelector('input[name="duration_value"]').value;
      let total_hours;
      switch(unit) {
        case 'days': total_hours = value * 24; break;
        case 'weeks': total_hours = value * 7 * 24; break;
        case 'months': total_hours = value * 30 * 24; break;
      }
      const freqType = block.querySelector(`input[name="freq_type_${idx}"]:checked`).value;
      const intervalValue = +block.querySelector('input[name="interval_value"]').value;
      let interval_h = null, weekday = null;
      if (freqType === 'hours') interval_h = intervalValue;
      else if (freqType === 'days') interval_h = intervalValue * 24;
      else if (freqType === 'weeks') interval_h = intervalValue * 7 * 24;
      else if (freqType === 'weekday') weekday = +block.querySelector('select[name="weekday_select"]').value;
      const dose_time = block.querySelector('input[name="dose_time"]').value;

      payload.drug_schedules.push({
        drug,
        dose_mg,
        start_time,
        total_hours,
        interval_h,
        weekday,
        dose_clock: dose_time
      });
    });
    // Отправка
    try {
      const resp = await fetch('/api/courses/', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
      if (!resp.ok) throw new Error('Ошибка при создании');
      const data = await resp.json();
      window.location.href = `/courses/${data.id}/`;  
    } catch (err) {
      alert(err.message);
    }
  });
});
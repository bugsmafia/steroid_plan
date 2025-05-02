// frontend/static/core/js/calculator.js?v=1.0.4
document.addEventListener('DOMContentLoaded', () => {
	if (window.Chart && window['chartjsPluginZoom']) {
	  Chart.register(chartjsPluginZoom);
	}
  // 1) Элементы формы
  const drugSelect     = document.getElementById('drugSelect');
  const dosageInfo     = document.getElementById('dosageInfo');
  const doseStart      = document.getElementById('dose-start');
  const doseAmount     = document.getElementById('dose-amount');
  const freqInput      = document.getElementById('dose-frequency');
  const unitSelect     = document.getElementById('dose-unit');
  const doseForm       = document.getElementById('dose-form');
  const chartCanvas    = document.getElementById('concChart');
  const tableContainer = document.getElementById('table-container');

  if (![drugSelect, dosageInfo, doseStart, doseAmount,
        freqInput, unitSelect, doseForm,
        chartCanvas, tableContainer].every(el => el)) {
    console.error('Ошибка: не найдены все необходимые элементы.');
    return;
  }

  let currentDosageRec = null;
  let concChart = null;

  // Загрузка списка препаратов
  fetch('/api/drugs/')
    .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
    .then(list => {
      list.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.id;
        opt.textContent = d.name;
        drugSelect.append(opt);
      });
    })
    .catch(err => {
      console.error('drugs fetch:', err);
      alert('Не удалось загрузить список препаратов.');
    });

  // При выборе препарата — рекомендации
  drugSelect.addEventListener('change', () => {
    const id = drugSelect.value;
    dosageInfo.textContent = '';
    currentDosageRec = null;
    if (!id) return;

    fetch(`/api/drugs/${id}/dosage/`)
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(info => {
        if (info.rec != null) {
          currentDosageRec = info.rec;
          dosageInfo.textContent =
            `Курс: min ${info.min} дн., usually ${info.rec} дн., max ${info.max} дн.`;
        } else {
          dosageInfo.textContent = 'Рекомендации отсутствуют.';
        }
      })
      .catch(err => {
        console.error('dosage fetch:', err);
        dosageInfo.textContent = 'Ошибка загрузки рекомендаций.';
      });
  });

  // При сабмите — строим график и таблицу
  doseForm.addEventListener('submit', e => {
    e.preventDefault();

    const drugId   = +drugSelect.value;
    const startStr = doseStart.value;
    const amount   = parseFloat(doseAmount.value);
    const freq     = parseInt(freqInput.value, 10);
    const unit     = unitSelect.value;

    if (!drugId || !startStr || isNaN(amount) || isNaN(freq)) {
      return alert('Пожалуйста, заполните все поля.');
    }
    if (!currentDosageRec) {
      return alert('Дождитесь загрузки рекомендаций.');
    }

    // Подгружаем формулу распада
    fetch(`/api/decay-formulas/?drug=${drugId}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
      .then(arr => {
		  console.log(arr.length);
        if (!arr.length) throw 'формула не найдена';
        const formula = arr[0].formula; // e.g. "C(t)=C0​∗e−0.231t"
		console.log(formula);

        // Более надёжно извлечём k:
        const idxE = formula.lastIndexOf('e');
        const idxT = formula.lastIndexOf('t');
		console.log("Проверяем формат формулы");
        if (idxE < 0 || idxT < 0 || idxT <= idxE) throw 'формат формулы некорректен';
		console.log("Формула проверена");
        // убираем всё, кроме цифр и точки:
        const kStr = formula.slice(idxE + 1, idxT).replace(/[^\d.]/g, '');
        const k = parseFloat(kStr);
		console.log(k);
		console.log("не удалось распарсить k");
        if (isNaN(k)) throw 'не удалось распарсить k';
		
		console.log("Парсер удался");
		console.log("buildAndRender");
        buildAndRender(
          new Date(startStr).getTime(),
          amount, freq, unit,
          currentDosageRec, k
        );
      })
      .catch(err => {
        console.error('decay-formula fetch:', err);
        alert('Не удалось загрузить формулу распада.');
      });
  });

  // Генерация дат инъекций, точек выборки и рендер
  function buildAndRender(startMs, doseMg, freq, unit, durationDays, k) {
    const unitMs = { hours:3600e3, days:86400e3, weeks:7*86400e3 };
    const intervalMs = freq * (unitMs[unit] || unitMs.days);

    // инъекции
    const injections = [];
    for (let t = startMs; t <= startMs + durationDays * 86400e3; t += intervalMs) {
      injections.push(t);
    }

    // выборки по дням
    const samples = Array.from({length: durationDays+1}, (_, i) =>
      startMs + i * 86400e3
    );

    // расчёт концентраций
    const concentrations = samples.map(ts =>
      injections.reduce((sum, inj) => {
        const dt = (ts - inj) / 3600e3;
        return dt >= 0 ? sum + doseMg * Math.exp(-k * dt) : sum;
      }, 0)
    );

    // метки по датам
    const labels = samples.map(ts =>
      new Date(ts).toLocaleDateString('ru-RU', {day:'2-digit',month:'2-digit'})
    );

    // Chart.js
    if (concChart) concChart.destroy();
    concChart = new Chart(chartCanvas.getContext('2d'), {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: drugSelect.selectedOptions[0].text,
          data: concentrations,
          borderColor: '#007bff',
          fill: false,
          pointRadius: 3,
        }]
      },
      options: {
        scales: {
          x: { display: true, title: { display: true, text: 'Дата' } },
          y: { display: true, title: { display: true, text: 'Конц. (mg)' } }
        },
        plugins: {
          zoom: {                  // <-- здесь конфиг плагина
            zoom: {
              wheel: { enabled: true },
              pinch: { enabled: true },
              mode: 'x',
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false,
        }
      }
    });

    renderTable(labels, concentrations);
  }

  // Рендер HTML-таблицы
  function renderTable(labels, data) {
    tableContainer.innerHTML = '';
    const tbl = document.createElement('table');
    tbl.className = 'table table-striped mt-3';
    const rows = labels.map((d,i) =>
      `<tr><td>${d}</td><td>${data[i].toFixed(2)}</td></tr>`
    ).join('');
    tbl.innerHTML = `
      <thead><tr><th>Дата</th><th>Конц., mg</th></tr></thead>
      <tbody>${rows}</tbody>`;
    tableContainer.append(tbl);
  }
});

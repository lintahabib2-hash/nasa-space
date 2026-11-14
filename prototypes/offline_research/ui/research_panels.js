/* Crew Vitals read-only, offline NASA research panels. No external requests. */
'use strict';
(function () {
  const $ = id => document.getElementById(id);
  const api = async path => {
    const response = await fetch(path, {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok) throw Error(data.error || `HTTP ${response.status}`);
    return data;
  };
  const say = (id, message) => { $(id).textContent = message; };
  const options = (id, values) => {
    $(id).replaceChildren(...values.map(value => {
      const el = document.createElement('option');
      el.value = value;
      el.textContent = value;
      return el;
    }));
  };
  const fmt = x => Number.isFinite(x) ? Number(x).toFixed(2) : 'Unavailable';
  function paint(canvasId, records, measured, baseline) {
    const rows = records.map(row => ({
      ...row,
      observed_on: row.label || '',
    }));
    linePlot($(canvasId), rows, measured, baseline);
  }

  async function loadCft70() {
    try {
      const meta = await api('/api/research/cft70');
      options('cftSubject', meta.subjects);
      say('cftSource', 'NASA CFT70 bed-rest analog · real dietary records · kcal/day · ' + meta.source_url);
      await drawCft70();
    } catch (error) {
      say('cftStatus', 'Unavailable: ' + error.message);
    }
  }
  async function drawCft70() {
    try {
      const subject = $('cftSubject').value;
      const data = await api('/api/research/cft70?subject_id=' + encodeURIComponent(subject));
      const p = data.participant;
      say('cftStatus', subject + ' · Group ' + p.group + ' · ' + p.pre_reference_n +
          ' pre-test reference days · pre-test median ' + fmt(p.pre_reference_median_kcal_day) +
          ' kcal/day · ' + p.observations.length + ' recorded days');
      let lastPhase = null;
      const rows = [];
      for (const r of p.observations) {
        if (lastPhase !== null && lastPhase !== r.study_phase) {
          rows.push({label: '', kcal: null, reference: null});
        }
        rows.push({label: r.study_phase.replace('_TEST', '') + ':' + r.study_day_label,
                   kcal: r.energy_kcal_per_day, reference: p.pre_reference_median_kcal_day});
        lastPhase = r.study_phase;
      }
      paint('cftChart', rows, 'kcal', 'reference');
      say('cftNote', 'Within-participant pre-test median (dashed); phase boundaries shown as gaps. ' +
          'Diet was protocol-controlled; this is not a health deterioration score. X1/X2 excluded from reference.');
    } catch(error) {say('cftStatus', 'Unable to show CFT70: ' + error.message);}
  }

  async function loadInspiration() {
    try {
      const study = $('i4Study').value;
      const meta = await api('/api/research/inspiration4?study=' + study);
      options('i4Subject', meta.subjects);
      options('i4Metric', meta.measurements);
      say('i4Source', 'NASA ' + meta.study_id + ' · historical Inspiration4 laboratory data · ' + meta.source_url);
      await drawInspiration();
    } catch(error) {say('i4Status', 'Unavailable: ' + error.message);}
  }
  async function drawInspiration() {
    try {
      const study = $('i4Study').value;
      const subject = $('i4Subject').value;
      const metric = $('i4Metric').value;
      const data = await api('/api/research/inspiration4?study=' + study +
          '&subject_id=' + encodeURIComponent(subject) + '&measurement=' + encodeURIComponent(metric));
      const values = data.records;
      const unavailable = values.filter(x => x.observed_value === null).length;
      const flagged = values.filter(x => (x.source_range_flags || []).length).length;
      const units = values[0].units || ({glucose:'mg/dL', sodium:'mmol/L', potassium:'mmol/L', albumin:'g/dL', creatinine:'mg/dL'})[metric] || 'see source metadata';
      say('i4Status', subject + ' · ' + metric + ' · preflight reference ' +
          fmt(values[0].preflight_reference_median) + ' ' + units + ' · missing ' + unavailable +
          ' · source-range review flags on ' + flagged + ' records');
      paint('i4Chart', values.map(x => ({label:x.timepoint,
          value:x.observed_value, reference:x.preflight_reference_median})), 'value', 'reference');
      say('i4Note', 'Solid = actual postflight observation; dashed = median of L−92/L−44/L−3. ' +
          'Three widely spaced preflight samples are a provisional descriptive reference, NOT a clinical normal range. ' +
          'Quality flags remain visible in the status line.');
    } catch(error) {say('i4Status', 'Unable to show biomarker: ' + error.message);}
  }

  async function loadRadlab() {
    try {
      const meta=await api('/api/research/radlab');
      options('radInstrument', meta.instrument_ids);
      say('radSource', 'NASA RadLab ISS historical instrument measurements · µGy/hour · ' + meta.source_url);
      await drawRadlab();
    } catch(error) {say('radStatus', 'Unavailable: '+error.message);}
  }
  async function drawRadlab() {
    try {
      const instrument=$('radInstrument').value;
      const data=await api('/api/research/radlab?instrument_id='+encodeURIComponent(instrument));
      const values=data.observations.map(x=>x.absorbed_dose_rate);
      const sorted=[...values].sort((a,b)=>a-b);
      const mid=sorted.length ? (sorted[Math.floor((sorted.length-1)/2)] + sorted[Math.floor(sorted.length/2)])/2 : NaN;
      say('radStatus', instrument+' · '+values.length+' observations · median '+fmt(mid)+
          ' µGy/hour · equivalent dose unavailable');
      paint('radChart', data.observations.map(x=>({label:x.timestamp_as_provided.slice(0,10),
          rate:x.absorbed_dose_rate})), 'rate', null);
      say('radNote','Source timestamp timezone not verified. Instrument dose-rate values are not a person’s exposure or a health risk estimate.');
    } catch(error) {say('radStatus', 'Unable to show radiation: '+error.message);}
  }
  $('cftSubject').addEventListener('change',drawCft70);
  $('i4Study').addEventListener('change',loadInspiration);
  $('i4Subject').addEventListener('change',drawInspiration);
  $('i4Metric').addEventListener('change',drawInspiration);
  $('radInstrument').addEventListener('change',drawRadlab);
  Promise.allSettled([loadCft70(),loadInspiration(),loadRadlab()]);
})();

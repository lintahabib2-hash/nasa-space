"""Read-only, provenance-checked offline research views.

No live requests, no subject cross-study joins, no medical predictions.
Generated NASA research reports are supplied explicitly from outside Git.
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
from collections import Counter

MAX_JSON_BYTES = 8_000_000
MAX_RADLAB_BYTES = 1_000_000


def _load(path, limit=MAX_JSON_BYTES):
    path = Path(path)
    if path.stat().st_size > limit:
        raise ValueError('Research export exceeds configured size limit')
    with path.open(encoding='utf-8') as f:
        result = json.load(f)
    if not isinstance(result, dict):
        raise ValueError('Expected a research JSON object')
    return result


def _positive_metric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def cft70_view(path, subject_id=None):
    d = _load(path)
    n = d.get('nutrition')
    if not isinstance(n, dict) or n.get('source_id') != 'NASA_NLSP_MR016G_CFT70' or n.get('provenance_kind') != 'analog_measured':
        raise ValueError('CFT70 research provenance mismatch')
    people = n.get('participants')
    if not isinstance(people, list) or not people:
        raise ValueError('CFT70 participant records missing')
    ids = [p.get('subject_id') for p in people]
    if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError('Invalid or duplicate CFT70 subject')
    meta = dict(source_id=n['source_id'], source_url=n.get('source_url'), provenance_kind='analog_measured',
                measurement='daily_energy_intake', units='kcal/day', time_precision='study_phase_day_label_only',
                subjects=ids, total_records=n.get('records'), clinical_validation=False,
                warning=n.get('interpretation_warning'), no_cross_study_merging=True)
    if subject_id is None:
        return meta
    p = next((p for p in people if p['subject_id'] == subject_id), None)
    if p is None:
        raise ValueError('Unknown CFT70 subject')
    obs = p.get('observations')
    if not isinstance(obs, list):
        raise ValueError('CFT70 observations missing')
    for row in obs:
        if row.get('study_phase') not in ('PRE_TEST','IN_TEST','POST_TEST') or not _positive_metric(row.get('energy_kcal_per_day')):
            raise ValueError('Invalid CFT70 observation')
    return {**meta, 'participant': p}


STUDIES = {'cmp': ('OSD-575', 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-575'),
           'cbc': ('OSD-569', 'https://osdr.nasa.gov/bio/repo/data/studies/OSD-569')}


def inspiration_view(path, study, subject_id=None, measurement=None):
    if study not in STUDIES:
        raise ValueError('Unknown Inspiration4 study')
    d = _load(path)
    study_id, source_url = STUDIES[study]
    if d.get('study_id') != study_id or d.get('clinical_validation') is not False:
        raise ValueError('Inspiration4 study/provenance mismatch')
    records = d.get('records')
    if not isinstance(records, list) or not records:
        raise ValueError('No Inspiration4 comparisons')
    if len(records)>5000:
        raise ValueError('Unexpected Inspiration4 record count')
    for r in records:
        if r.get('source_id') != 'NASA_OSDR_'+study_id or r.get('provenance_kind') != 'nasa_measured' or r.get('not_medical_diagnosis') is not True:
            raise ValueError('Inspiration4 record provenance mismatch')
        if r.get('timepoint') not in ('R+1','R+45','R+82','R+194'):
            raise ValueError('Unrecognized Inspiration4 timepoint')
        for k in ('observed_value','preflight_reference_median'):
            v=r.get(k)
            if v is not None and not _positive_metric(v):
                raise ValueError('Non-finite Inspiration4 measurement')
    subjects = sorted(set(r['subject_id'] for r in records))
    metrics = sorted(set(r['measurement'] for r in records))
    meta = dict(source_id='NASA_OSDR_'+study_id, source_url=source_url,
                provenance_kind='nasa_measured', study_id=study_id,
                time_precision='mission_relative_day', subjects=subjects,
                measurements=metrics, comparison_records=len(records),
                clinical_validation=False, limitations=d.get('limitations', []), no_cross_study_merging=True)
    if subject_id is None and measurement is None:
        return meta
    if subject_id not in subjects or measurement not in metrics:
        raise ValueError('Unknown subject or measurement')
    subset=[r for r in records if r['subject_id']==subject_id and r['measurement']==measurement]
    if not subset:
        raise ValueError('No matching biomarker records')
    order={'R+1':0,'R+45':1,'R+82':2,'R+194':3}
    subset.sort(key=lambda r: order[r['timepoint']])
    if len(set(r['timepoint'] for r in subset)) != len(subset):
        raise ValueError('Duplicate Inspiration4 comparison timepoint')
    return {**meta, 'subject_id':subject_id, 'measurement':measurement, 'records':subset}


def radlab_view(path, instrument_id=None):
    path=Path(path)
    if path.stat().st_size > MAX_RADLAB_BYTES:
        raise ValueError('RadLab CSV exceeds configured size limit')
    rows=[]
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not {'timestamp','instrument_id','absorbed_dose_rate'}.issubset(reader.fieldnames or []):
            raise ValueError('Missing RadLab measurement columns')
        seen=set()
        for row in reader:
            inst=row['instrument_id']
            timestamp=row['timestamp']
            if not inst or not timestamp or (inst,timestamp) in seen:
                raise ValueError('Missing/duplicate RadLab instrument timestamp')
            seen.add((inst,timestamp))
            try:
                rate=float(row['absorbed_dose_rate'])
            except (TypeError,ValueError) as exc:
                raise ValueError('RadLab absorbed dose rate is missing or invalid') from exc
            if not math.isfinite(rate) or rate < 0:
                raise ValueError('Nonfinite or negative RadLab absorbed dose rate')
            rows.append({'instrument_id':inst,'timestamp_as_provided':timestamp,'absorbed_dose_rate':rate})
            if len(rows)>5000:
                raise ValueError('Unexpectedly large RadLab sample')
    if not rows:
        raise ValueError('Empty RadLab sample')
    ids=sorted(set(x['instrument_id'] for x in rows))
    meta=dict(source_id='NASA_OSDR_RADLAB_ISS_DOSTEL_SAMPLE',
              source_url='https://visualization.osdr.nasa.gov/radlab/gui/data-api/',
              provenance_kind='historical_spacecraft_instrument_measurements',
              time_precision='source_timestamp_timezone_unverified',
              instrument_ids=ids, record_count=len(rows),
              measurement='absorbed_dose_rate',units='microgray/hour',
              dose_equivalent_rate_status='unavailable_in_acquired_sample',
              clinical_validation=False,
              warning='DosTel instrument readings, not astronaut personal exposure or health risk.')
    if instrument_id is None:
        return meta
    if instrument_id not in ids:
        raise ValueError('Unknown RadLab instrument')
    return {**meta, 'instrument_id':instrument_id,
            'observations':[x for x in rows if x['instrument_id']==instrument_id]}

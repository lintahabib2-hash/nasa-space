"""Deterministic offline-only scientific panel tests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from offline_research import cft70_view, inspiration_view, radlab_view

class ResearchViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def write(self, name, value):
        p=self.root/name
        p.write_text(json.dumps(value),encoding='utf-8')
        return p

    def test_cft70_provenance_rejected(self):
        p=self.write('cft.json',{'nutrition':{'source_id':'fake','participants':[{'subject_id':'1'}]}})
        with self.assertRaises(ValueError):cft70_view(p)

    def test_cft70_selected_subject_only(self):
        a={'subject_id':'5210','group':'Control','pre_reference_n':6,
           'pre_reference_median_kcal_day':2000,
           'observations':[{'study_phase':'PRE_TEST','study_day_label':'6','energy_kcal_per_day':2000}]}
        b={'subject_id':'5211','group':'Exercise','pre_reference_n':6,'observations':[]}
        p=self.write('cft.json',{'nutrition':{'source_id':'NASA_NLSP_MR016G_CFT70',
            'provenance_kind':'analog_measured','participants':[a,b]}})
        self.assertEqual(cft70_view(p)['subjects'],['5210','5211'])
        self.assertEqual(cft70_view(p,'5210')['participant']['subject_id'],'5210')
        with self.assertRaises(ValueError):cft70_view(p,'unknown')

    def test_inspiration4_subject_and_analyte_separation(self):
        r=lambda sid,measurement: {'subject_id':sid,'measurement':measurement,'timepoint':'R+1',
                'source_id':'NASA_OSDR_OSD-569','provenance_kind':'nasa_measured',
                'not_medical_diagnosis':True,'observed_value':1.0,'preflight_reference_median':2.0}
        p=self.write('cbc.json',{'study_id':'OSD-569','clinical_validation':False,
                                'records':[r('C001','hemoglobin'),r('C002','platelet_count')]})
        out=inspiration_view(p,'cbc','C001','hemoglobin')
        self.assertEqual(len(out['records']),1)
        self.assertEqual(out['records'][0]['subject_id'],'C001')
        with self.assertRaises(ValueError):inspiration_view(p,'cbc','C002','hemoglobin')

    def test_inspiration4_invalid_provenance_rejected(self):
        p=self.write('cbc.json',{'study_id':'OSD-569','clinical_validation':False,'records':[{
            'source_id':'NASA_OSDR_OSD-569','provenance_kind':'crew_self_report',
            'not_medical_diagnosis':True,'timepoint':'R+1'}]})
        with self.assertRaises(ValueError):inspiration_view(p,'cbc')

    def test_radlab_keeps_instruments_separate_and_no_equivalent_conversion(self):
        p=self.root/'rad.csv'
        p.write_text('timestamp,instrument_id,absorbed_dose_rate,dose_equivalent_rate\n'
             '2022-04-01T23:00:00,DosTel1,2.0,\n'
             '2022-04-01T23:00:00,DosTel2,3.0,\n')
        self.assertEqual(radlab_view(p)['record_count'],2)
        view=radlab_view(p,'DosTel1')
        self.assertEqual(len(view['observations']),1)
        self.assertEqual(view['observations'][0]['absorbed_dose_rate'],2.0)
        self.assertEqual(view['dose_equivalent_rate_status'],'unavailable_in_acquired_sample')

    def test_radlab_negative_and_duplicate_rejected(self):
        p=self.root/'rad.csv'
        p.write_text('timestamp,instrument_id,absorbed_dose_rate\nT1,DosTel1,-1\n')
        with self.assertRaises(ValueError):radlab_view(p)
        p.write_text('timestamp,instrument_id,absorbed_dose_rate\nT1,DosTel1,1\nT1,DosTel1,2\n')
        with self.assertRaises(ValueError):radlab_view(p)

if __name__=='__main__':unittest.main()

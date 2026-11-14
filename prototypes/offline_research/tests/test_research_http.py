"""Real localhost routes with temporary offline research files only."""
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from offline_api import create_server

class HTTPResearchPanelTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        cft=self.root/'cft.json'
        cft.write_text(json.dumps({'nutrition':{
            'source_id':'NASA_NLSP_MR016G_CFT70','provenance_kind':'analog_measured',
            'participants':[{'subject_id':'5210','group':'Control','pre_reference_n':5,
                'pre_reference_median_kcal_day':2100,'observations':[
                    {'study_phase':'PRE_TEST','study_day_label':'10','energy_kcal_per_day':2100.0}]}]}}))
        self.server=create_server(db_path=self.root/'checkins.sqlite', cft70_json=cft, port=0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url=f'http://127.0.0.1:{self.server.server_port}'
    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
    def get(self, route):
        with urlopen(self.url+route,timeout=3) as response:
            return response.read()
    def test_research_endpoint_is_subject_scoped(self):
        meta=json.loads(self.get('/api/research/cft70'))
        self.assertEqual(meta['subjects'],['5210'])
        detail=json.loads(self.get('/api/research/cft70?subject_id=5210'))
        self.assertEqual(detail['participant']['pre_reference_median_kcal_day'],2100)
    def test_research_static_js_served_locally(self):
        self.assertIn(b'loadCft70',self.get('/research-panels.js'))
        health=json.loads(self.get('/api/health'))
        self.assertTrue(health['research']['cft70_available'])
        self.assertFalse(health['research']['radlab_available'])

if __name__=='__main__':unittest.main()

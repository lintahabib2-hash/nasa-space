"""Local HTTP smoke tests: no cloud network and no research files required."""
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from offline_api import create_server


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.server=create_server(db_path=Path(self.tmp.name)/'local.sqlite',port=0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.cleanup_server)
        self.base=f'http://127.0.0.1:{self.server.server_port}'

    def cleanup_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def get(self,route):
        with urllib.request.urlopen(self.base+route,timeout=3) as r:
            return r.status,json.loads(r.read())

    def test_local_health(self):
        status,payload=self.get('/api/health')
        self.assertEqual(status,200)
        self.assertEqual(payload['mode'],'local_offline')
        self.assertFalse(payload['research']['bedrest_available'])

    def test_submission_and_insufficient_history(self):
        payload={'subject_id':'crew_01','study_id':'local_demo','source_id':'local_checkin',
                 'provenance_kind':'crew_self_report','measurement':'sleep_duration',
                 'value':7.2,'units':'hours','timestamp_utc':'2020-01-01T05:00:00Z'}
        request=urllib.request.Request(self.base+'/api/checkins',data=json.dumps(payload).encode(),
                                     headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(request,timeout=3) as r:
            self.assertEqual(r.status,201)
        status,result=self.get('/api/analytics/latest?subject_id=crew_01')
        self.assertEqual(status,200)
        self.assertEqual(result['status'],'insufficient_history')
        self.assertTrue(result['not_medical_diagnosis'])

    def test_research_unavailable_without_local_files(self):
        with self.assertRaises(urllib.error.HTTPError) as e:
            self.get('/api/research/bedrest')
        self.assertEqual(e.exception.code,404)

if __name__=='__main__':unittest.main()

"""Offline deterministic intake tests; no requests to NASA in CI."""
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from extra_sources import audit_radlab, osdr_file_candidates, radlab_query

BASE = ("timestamp,instrument_id,absorbed_dose_rate,dose_equivalent_rate\n"
        "2022-04-01T23:00:00,ISS-DosTel-1,2.5,4.0\n"
        "2022-04-01T23:05:00,ISS-DosTel-1,2.7,NA\n").encode()

class ExtraSourcesTests(unittest.TestCase):
    def test_radlab_query_is_bounded_and_explicit(self):
        params = parse_qs(urlsplit(radlab_query()).query)
        self.assertEqual(params["format"], ["csv"])
        self.assertEqual(
            params["fields"],
            ["absorbed_dose_rate,dose_equivalent_rate"]
        )
        expression = params["query"][0]
        self.assertIn("(spacecraft=ISS)", expression)
        self.assertIn("(instrument=DosTel)", expression)
        self.assertIn(
            "(timestamp>=2022-04-01T23:00)", expression
        )
        self.assertIn(
            "(timestamp<2022-04-02T01:05)", expression
        )
        self.assertNotIn("absorbed_dose_rate>", expression)

    def test_radlab_audit_preserves_missing_and_units(self):
        r = audit_radlab(BASE)
        self.assertEqual(r['rows'], 2)
        self.assertEqual(r['measurements']['absorbed_dose_rate']['units'], 'microgray/hour')
        self.assertEqual(r['measurements']['dose_equivalent_rate']['missing_rows'], 1)
        self.assertEqual(r['timestamp_timezone_assumption'], 'none; consult RadLab instrument documentation')
    def test_rejects_invalid_instrument_or_schema(self):
        with self.assertRaises(ValueError):
            audit_radlab(b'timestamp,absorbed_dose_rate\n2022-01-01,1.0\n')
    def test_rejects_negative_dose(self):
        with self.assertRaises(ValueError):
            audit_radlab(BASE.replace(b'2.5', b'-2.5'))
    def test_rejects_nonfinite_dose(self):
        with self.assertRaises(ValueError):
            audit_radlab(BASE.replace(b'2.5', b'inf'))
    def test_rejects_empty_data(self):
        with self.assertRaises(ValueError):
            audit_radlab(b'timestamp,instrument_id,absorbed_dose_rate\n')
    def test_duplicates_reported_not_silently_dropped(self):
        r = audit_radlab(BASE + BASE.split(b'\n')[1] + b'\n')
        self.assertEqual(r['duplicate_instrument_timestamp_pairs'], 1)
    def test_osd575_inventory_never_claims_public(self):
        payload = {'study_files': [{'file_name':'LSDS-8_TRANSFORMED.csv', 'remote_url':'/file.csv', 'public':False},
                                   {'remote_url':'/restricted.zip','status':'restricted'},
                                   {'remote_url':'/file.csv'}]}
        f = osdr_file_candidates(payload)
        self.assertEqual(len(f), 2)
        self.assertEqual(f[0]['access'], 'NOT_VERIFIED_FILE_LEVEL')
        self.assertTrue(f[0]['candidate_data'])

if __name__ == '__main__': unittest.main()

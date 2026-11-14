"""No external data or network services required for storage/API unit tests."""
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from offline_api import OfflineStore, normalize_checkin


def checkin(value=7.5, subject="crew_01", at="2020-01-01T05:00:00Z"):
    return {"subject_id": subject, "study_id": "local_demo", "source_id": "local_checkin",
            "provenance_kind": "crew_self_report", "measurement": "sleep_duration",
            "value": value, "units": "hours", "timestamp_utc": at}


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = OfflineStore(Path(self.tmp.name)/"nested"/"crew.sqlite3")

    def test_store_and_reopen(self):
        a = self.store.put(checkin())
        reopened = OfflineStore(self.store.path)
        self.assertEqual(len(reopened.list_subject("crew_01")), 1)
        self.assertEqual(reopened.list_subject("crew_01")[0]["id"], a["id"])

    def test_duplicate_rejected(self):
        self.store.put(checkin())
        with self.assertRaises(ValueError): self.store.put(checkin())
        self.assertEqual(len(self.store.list_subject("crew_01")), 1)

    def test_subject_separation(self):
        self.store.put(checkin(subject="crew_01"))
        self.store.put(checkin(subject="crew_02"))
        self.assertEqual(len(self.store.list_subject("crew_01")), 1)

    def test_no_history_not_diagnosed(self):
        result = self.store.latest_analysis("crew_01")
        self.assertEqual(result["status"], "no_observations")
        self.assertTrue(result["not_medical_diagnosis"])
        self.store.put(checkin())
        result = self.store.latest_analysis("crew_01")
        self.assertEqual(result["status"], "insufficient_history")

    def test_rejects_fake_nasa_provenance(self):
        record = checkin()
        record["provenance_kind"] = "analog_measured"
        with self.assertRaises(ValueError): self.store.put(record)

    def test_rejects_non_sleep_and_future(self):
        record = checkin()
        record["measurement"] = "heart_rate"
        with self.assertRaises(ValueError): normalize_checkin(record)
        future = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        with self.assertRaises(ValueError): self.store.put(checkin(at=future))

    def test_invalid_number_not_persisted(self):
        with self.assertRaises(ValueError): self.store.put(checkin(value=float('nan')))
        self.assertEqual(self.store.list_subject("crew_01"), [])

if __name__ == "__main__": unittest.main()

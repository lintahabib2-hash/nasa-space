import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eda_adapter import FIELDS, load_eda_preview


class EdaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/"RR1.csv"

    def write(self, rows):
        with self.path.open('w',newline='',encoding='utf8') as f:
            writer = csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()
            for row in rows: writer.writerow(row)

    def example(self, at="2014-09-20 03:59", co2="2641"):
        return dict(zip(FIELDS,(at,"24.1","24.1","37","39","484",co2)))

    def test_valid_preview_and_units(self):
        self.write([self.example(),self.example("2014-09-20 04:04","2652")])
        a = load_eda_preview(self.path)
        self.assertEqual(a["row_count"],2)
        self.assertEqual(a["units"]["CO2_ppm_ISS"],"ppm")
        self.assertEqual(a["observations"][0]["observed_at_utc"],"2014-09-20T03:59:00Z")
        self.assertEqual(a["provenance_kind"],"environment_measured")

    def test_reject_duplicate_timestamp(self):
        self.write([self.example(),self.example()])
        with self.assertRaises(ValueError): load_eda_preview(self.path)

    def test_reject_nan(self):
        self.write([self.example(co2="NaN")])
        with self.assertRaises(ValueError): load_eda_preview(self.path)

    def test_reject_out_of_range_humidity(self):
        row=self.example();row["RH_percent_ISS"]="101"
        self.write([row])
        with self.assertRaises(ValueError): load_eda_preview(self.path)

if __name__ == "__main__": unittest.main()

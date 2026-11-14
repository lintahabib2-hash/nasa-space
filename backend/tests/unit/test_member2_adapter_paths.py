import unittest

from backend.app.adapters import (
    nlsp_actigraphy,
    nlsp_preview,
    nlsp_trends,
    osd575_serum,
    osd569_cbc,
    cft70_nutrition,
)

from member2 import (
    bedrest_adapter,
    bedrest_preview_export,
    retrospective_trends,
    inspiration4_reference,
    inspiration4_cbc,
    cft70_research,
)


class AdapterMigrationTests(unittest.TestCase):

    def test_actigraphy_shared(self):
        self.assertIs(
            nlsp_actigraphy.load_and_audit,
            bedrest_adapter.load_and_audit,
        )

    def test_bedrest_preview_shared(self):
        self.assertIs(
            nlsp_preview.create_preview,
            bedrest_preview_export.create_preview,
        )

    def test_bedrest_trends_shared(self):
        self.assertIs(
            nlsp_trends.add_trends,
            retrospective_trends.add_trends,
        )

    def test_serum_shared(self):
        self.assertIs(
            osd575_serum.analyze,
            inspiration4_reference.analyze,
        )

    def test_cbc_shared(self):
        self.assertIs(
            osd569_cbc.analyze_cbc,
            inspiration4_cbc.analyze_cbc,
        )

    def test_cft70_shared(self):
        self.assertIs(
            cft70_nutrition.analyze_intake,
            cft70_research.analyze_intake,
        )


if __name__ == "__main__":
    unittest.main()

import unittest
import datetime
from NS_Common_Keywords.keywords import NS_Common_Keywords

class TestNS_Common_Keywords(unittest.TestCase):
    def setUp(self):
        self.keywords = NS_Common_Keywords()

    def test_pas_format_aan_van_datum(self):
        self.assertEqual(
            self.keywords.pas_format_aan_van_datum('03-07-2025'),
            '2025-07-03'
        )
        self.assertEqual(
            self.keywords.pas_format_aan_van_datum('03/07/2025', '%d/%m/%Y', '%d-%m-%Y'),
            '03-07-2025'
        )

    def test_bepaal_huidige_datum(self):
        today = datetime.datetime.now().strftime('%d-%m-%Y')
        self.assertEqual(self.keywords.bepaal_huidige_datum(), today)

    def test_bepaal_datum_plus_extra_dagen(self):
        self.assertEqual(
            self.keywords.bepaal_datum_plus_extra_dagen(1, '03-07-2025', '%d-%m-%Y'),
            '04-07-2025'
        )

    def test_formatteer_bedrag(self):
        self.assertEqual(self.keywords.formatteer_bedrag(1000), '1.000,00')
        self.assertEqual(self.keywords.formatteer_bedrag(12345), '12.345,00')
        self.assertEqual(self.keywords.formatteer_bedrag(12345.67), '12.345,67')

    def test_creeer_willekeurige_zin(self):
        zin = self.keywords.creeer_willekeurige_zin()
        self.assertIsInstance(zin, str)
        self.assertGreater(len(zin.split()), 3)

    def test_creeer_willekeurig_woord(self):
        woord = self.keywords.creeer_willekeurig_woord()
        self.assertIsInstance(woord, str)
        self.assertGreater(len(woord), 0)

if __name__ == '__main__':
    unittest.main()

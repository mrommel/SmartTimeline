import unittest
from google_play_scraper import app as GoogleApp


class MyTestCase(unittest.TestCase):
	def test_something(self):
		result_myf_android = GoogleApp('de.avm.android.myfritz2', lang='de', country='de')
		self.assertEqual(4.220142, result_myf_android["score"])


if __name__ == '__main__':
	unittest.main()

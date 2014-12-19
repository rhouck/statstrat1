# python -m unittest discover <test_directory>
# python -m unittest discover -s <directory> -p 'test1.py'
# nosetests test1.py
# "nosetests /path/to/tests" - to execute a suite of tests in a folder

import unittest
from p1 import * 

class TestRecordsCollection(unittest.TestCase):
	
	def setUp(self):
		pass
	
	def test_mongo_connection(self):
		db = Mongo()

if __name__ == "__main__":
	 unittest.main()
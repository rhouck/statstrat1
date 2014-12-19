from django.core.management.base import BaseCommand, CommandError
from model.p1 import *

class Command(BaseCommand):
	help = "Updates historical stock price and index db."

	def handle(self, *args, **options):
	
		self.stdout.write("Checking index data")
		index_tix = ['^GSPC', '^IXIC']
		try:
			get_collection_as_pandas_df(index_tix, 'index_test')
		except Exception as err:
			raise CommandError("Could not update index prices - %s" % (err))
		
		self.stdout.write("Checking stocks data")
		tix = get_import_io_s_and_p_tickers()
		get_collection_as_pandas_df(tix, 'stocks_test')

		self.stdout.write("Done")
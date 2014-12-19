from django.core.management.base import BaseCommand, CommandError
from model.p2 import *

class Command(BaseCommand):
	
	help = "Updates historical stock price and index db."

	def handle(self, *args, **options):
		

		count_args = len([a for a in args])
		if count_args != 2:
			raise CommandError("Must provide two date arguments - start_date and end_date")
		
		
		dates = []
		try:
			for i in args:
				a = i.split('-')
				a = [int(n) for n in a]
				dates.append(datetime.datetime(a[0],a[1],a[2],0,0))
		except Exception as err:
			raise CommandError("Dates must be formatted as 'YYYY-MM-DD' - %s" % (err))	
		
		if dates[1] < dates[0]:
			raise CommandError("First date (start_date) must be less than second date (end_date)")
		
		tix = get_import_io_s_and_p_tickers('model/')
		df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
		w = Window(df, start_date=dates[0], end_date=dates[1], return_period_days=1)
		w.pull_cointegrated_partners(date_strict=True)

		self.stdout.write("Done")
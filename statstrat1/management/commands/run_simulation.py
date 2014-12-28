from django.core.management.base import BaseCommand, CommandError
from model.p4 import *

class Command(BaseCommand):
	help = "Runs simulation."

	def handle(self, *args, **options):

		count_args = len([a for a in args])
		if count_args != 4:
			raise CommandError("Must provide start date, number of periods to simulate, simulation_interval_days, and return_period_days")
			
		try:
			a = args[0].split('-')
			a = [int(n) for n in a]
			start_date = (datetime.datetime(a[0],a[1],a[2],0,0))
		except Exception as err:
			raise CommandError("Arg 1 must be date. Dates must be formatted as 'YYYY-MM-DD' - %s" % (err))

		try: 
			sim_periods = int(args[1])
		except:
			raise CommandError("Arg 2, number of periods to sumulate, must be int.")
		
		try: 
			simulation_interval_days = int(args[2])
		except:
			raise CommandError("Arg 3, simulation_interval_days, must be int.")

		try: 
			return_period_days = int(args[3])
		except:
			raise CommandError("Arg 4, return_period_days, must be int.")

		tix = get_import_io_s_and_p_tickers('model/')
		df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
		performance = back_test_model(df, start_date, sim_periods, simulation_interval_days, return_period_days, 'model/')

		self.stdout.write("Done")
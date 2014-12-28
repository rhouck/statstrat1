from django.core.management.base import BaseCommand, CommandError
from model.p4 import *

class Command(BaseCommand):
	help = "Updates input data to splash page."

	def handle(self, *args, **options):

		return_period_days = 5
		return_period_days_fwd = 5

		count_args = len([a for a in args])
		if count_args > 2:
			raise CommandError("Limit to two (int) argument: return_period_days and return_period_days_fwd")
			
		if count_args > 0:
			try: 
				return_period_days = int(args[0])
			except:
				raise CommandError("return_period_days arg must be int.")

		if count_args > 1:
			try: 
				return_period_days_fwd = int(args[1])
			except:
				raise CommandError("return_period_days_fwd arg must be int.")

		update_splash_page_inputs('model/', return_period_days, return_period_days_fwd)
		
		self.stdout.write("Done")
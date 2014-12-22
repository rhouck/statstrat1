from django.core.management.base import BaseCommand, CommandError
from model.p4 import *

class Command(BaseCommand):
	help = "Updates input data to splash page."

	def handle(self, *args, **options):

		return_period_days = 7

		count_args = len([a for a in args])
		if count_args > 1:
			raise CommandError("Limit to one (int) argument: return_period_days")
			
		if count_args:
			try: 
				return_period_days = int(args[0])
			except:
				raise CommandError("return_period_days arg must be int.")

		update_splash_page_inputs('model/', return_period_days)
		
		self.stdout.write("Done")
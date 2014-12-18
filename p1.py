import datetime

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#import statsmodels.formula.api as sm_f
#import statsmodels.api as sm
import pandas.io.data as web
from pymongo import MongoClient, DESCENDING, ASCENDING
import pymongo
import pytz

from tickers import get_import_io_nasdaq_tickers, get_import_io_s_and_p_tickers

class Mongo():
	
	def __init__(self, db_name=None):
		
		if (db_name and not isinstance(db_name, str)):
			raise ValueError('db_name must be a string.')

		self.client = MongoClient()
		db_name = db_name if db_name else 'strat1'
		self.db = self.client[db_name]


def get_last_market_close():

	# finds date of most recent market close (ignoring weekdends and holidays)
	utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
	eastern = pytz.timezone('US/Eastern')
	ny_dt = utc_now.astimezone(eastern)
	
	# return current day if market already closed
	if ny_dt.hour > 16:
		return datetime.datetime(ny_dt.year, ny_dt.month, ny_dt.day,0,0)
	else: 
		return datetime.datetime(ny_dt.year, ny_dt.month, ny_dt.day-1,0,0)

def check_px_collection_date_range(collection,):
	
	if not isinstance(collection, pymongo.collection.Collection):
		raise ValueError('collection must by a pymongo Collection type')

	earliest_date = collection.find().sort([("date", ASCENDING)]).limit(1)[0]['date']
	latest_date = collection.find().sort([("date", DESCENDING)]).limit(1)[0]['date']
	return (earliest_date, latest_date)

def add_rows(collection, pandas_df):
	
	if not isinstance(collection, pymongo.collection.Collection):
		raise ValueError('collection must by a pymongo Collection type')

	if not isinstance(pandas_df, pd.core.frame.DataFrame):
		raise ValueError('pandas_df must by a pandas DataFrame type')

	# add new pricing rows to mongo db
	for i in range(pandas_df.shape[0]):
	    row = {'date': pandas_df.index[i]}
	    row.update(pandas_df.ix[i].to_dict())
	    collection.insert(row)
	

def pull_prices_from_pandas_data_reader(start_date, end_date, tickers,):
	
	if not tickers or not isinstance(tickers, (list, tuple)):
		raise ValueError('tickers must be a tuple or list and not empty.')		
	
	if not isinstance(start_date, (datetime.date, datetime.datetime)) or not isinstance(end_date, (datetime.date, datetime.datetime)):
		raise ValueError("start_ and end_ date must be date or datetime format.")	
	
	df = web.DataReader(tickers, 'yahoo', start_date, end_date)
	return df

def update_collection_if_needed(tickers, pandas_price_type, collection_name):

	if not tickers or not isinstance(tickers, (list, tuple)):
		raise ValueError('tickers must be a tuple or list and not empty.')

	if not isinstance(pandas_price_type, str) or not isinstance(collection_name, str):
		raise ValueError('pandas_price_type and collection_name must be strings.')

	def cleanup(message=None):
		if message:
			print message
		db.client.close()
		return True

	earliest_relevant_date = datetime.datetime(2000,1,1,0,0)
	last_market_close = get_last_market_close()

	# get collection
	db = Mongo()
	collection = db.db[collection_name]
	
	# check if tickers have changed
	rec = collection.find_one()
	if not rec:
		# rebuild from full set if no records in collection
		print "No records in collection, need to rebuild"
		df = pull_prices_from_pandas_data_reader(earliest_relevant_date, last_market_close, tickers,)
		new_rows = df[pandas_price_type].shape[0]
		
		print "Pulled price data from pandas"
		collection.create_index("date")
		current_collection_size = collection.count()
		add_rows(collection, df[pandas_price_type])
		
		return cleanup("Finished - beg count: %s, new rows: %s, end count: %s" % (current_collection_size, new_rows, collection.count()))

	# find current tickers in collection
	current_tickers = [str(t) for t in rec.keys()]
	for i in ('_id', 'date'):
		current_tickers.remove(i)
	# compare current tickers in db to tickers passed in script
	if not (set(current_tickers) == set(tickers)):
		# drop collection and rebuild
		print "Tickers don't match what is in current database, drop collections and rebuild"
		collection.drop()
		df = pull_prices_from_pandas_data_reader(earliest_relevant_date, last_market_close, tickers,)
		new_rows = df[pandas_price_type].shape[0]
		
		print "Pulled price data from pandas"
		collection.create_index("date")
		current_collection_size = collection.count()
		add_rows(collection, df[pandas_price_type])
		
		return cleanup("Finished - beg count: %s, new rows: %s, end count: %s" % (current_collection_size, new_rows, collection.count()))

	
	# check latest db date
	db_date_range =  check_px_collection_date_range(collection)
	if last_market_close.date() > db_date_range[1].date():
		search_start = db_date_range[1] + datetime.timedelta(days=1)
		
		print "Need to update db to current date"
		df = pull_prices_from_pandas_data_reader(search_start, last_market_close, tickers,)
		if pandas_price_type not in df:
			return cleanup("No new data available yet")
		print "Pulled price data from pandas"
		new_rows = df[pandas_price_type].shape[0]
		current_collection_size = collection.count()
		add_rows(collection, df[pandas_price_type])
		
		return cleanup("Finished - beg count: %s, new rows: %s, end count: %s" % (current_collection_size, new_rows, collection.count()))

	return cleanup()

def get_collection_as_pandas_df(tickers, collection_name, earliest_search_date=None, update=True):
	
	collection_name_to_pandas_price_type = {
											'test': 'Close',
											'open': 'Open',
											'high': 'High',
											'low': 'Low',
											'close': 'Close',
											'vol': 'Volume',
											'adj_close': 'Adj Close',
											}
	if collection_name not in collection_name_to_pandas_price_type:
		raise KeyError('collection_name not recognized')

	pandas_price_type = collection_name_to_pandas_price_type[collection_name]
	
	if update:
		update_collection_if_needed(tickers, pandas_price_type, collection_name)

	db = Mongo()
	collection = db.db[collection_name]
	
	desired_columns = {'date': 1, '_id': 0}
	for i in tickers:
		desired_columns[str(i)] = 1
	
	d = earliest_search_date if earliest_search_date else datetime.datetime(2000,1,1,0,0)
	records = list(collection.find({"date": {"$gte": d}},desired_columns).sort([("date", ASCENDING)]))
	df = pd.DataFrame.from_records(records).set_index('date')
	db.client.close()
	return df

if __name__ == "__main__":

	"""
	db = Mongo()
	collection = db.db['test']
	#collection.drop()
	# delete recent data for testing
	recent = collection.find().sort([("date", DESCENDING)]).limit(5)
	for r in recent:
		collection.remove(r)
	"""

	#tix = ['AA', 'AAPL', 'GE', 'IBM', 'JNJ', 'MSFT', 'PEP', 'XOM', 'SPX']
	tix = get_import_io_s_and_p_tickers()
	df = get_collection_as_pandas_df(tix, 'test')
	print df
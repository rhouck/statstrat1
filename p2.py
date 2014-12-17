from pprint import pprint
from p1 import *

class Window():

	def __init__(self, pandas_df, start_date=None, end_date=None):

		# takes a data frame as input and truncates according to start and end dates
		# calculates daily returns and daily cummulative returns

		if (start_date and not isinstance(start_date, (datetime.datetime))) or (end_date and not isinstance(end_date, (datetime.datetime))):
			raise ValueError("start_ and end_ date must be datetime format if given")

		if not isinstance(pandas_df, pd.core.frame.DataFrame):
			raise ValueError('pandas_df must by a pandas DataFrame type')

		if start_date:	
			pandas_df = pandas_df[pandas_df.index >= start_date]
		if end_date:	
			pandas_df = pandas_df[pandas_df.index <= end_date]

		self.start_date = pandas_df.index[0]
		self.end_date = pandas_df.index[-1]
		
		self.df = pandas_df
		
		# convert prices to daily cumulative returns
		# this is helpful when looking into correlations and calculating betas
		returns = self.df / self.df.shift(1) - 1
		self.returns = (1 + returns).dropna(how='any')	
		self.daily_index = self.returns.cumprod().dropna(how='any')	


	def get_ticker_highest_corr(self, beta_period=7, max_pairs=3, min_corr=None):
		
		# returns a dictionary item for each ticker in list with a list of its top N most highly correlated tickers
		period_returns = (self.daily_index / self.daily_index.shift(beta_period)).dropna(how='any')
		corr_matrix = period_returns.corr()
		cols = corr_matrix.columns
		
		self.highest_corr = {}
		for c in cols:
			pair_wise_corr = corr_matrix[c].copy()
			pair_wise_corr = pair_wise_corr.drop(c)
			pair_wise_corr.sort(ascending=False)
			if min_corr:
				pair_wise_corr = pair_wise_corr[pair_wise_corr >= min_corr]
			
			self.highest_corr[c] = list(pair_wise_corr.index[:max_pairs])


if __name__ == "__main__":

	tix = ['AA', 'AAPL', 'GE', 'IBM', 'JNJ', 'MSFT', 'PEP', 'XOM', 'SPX']
	df = get_collection_as_pandas_df(tix, 'test')

	w = Window(df) #, start_date=datetime.datetime(2010,1,1,0,0), end_date=datetime.datetime(2010,1,5,0,0))
	"""
	print w.start_date
	print w.end_date
	print w.returns.head()
	print w.daily_index.head()
	print w.df.head()
	"""
	w.get_ticker_highest_corr()
	pprint(w.highest_corr)
		

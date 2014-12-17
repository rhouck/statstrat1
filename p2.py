from pprint import pprint
from p1 import *

class Window():

	def __init__(self, pandas_df, start_date=None, end_date=None, return_period_days=7):

		# takes a data frame as input and truncates according to start and end dates
		# calculates daily returns and daily cummulative returns

		# this determins the number of days' gap between return calcualtions - for finding correlation matches and betas
		if not isinstance(return_period_days, int):
			raise ValueError("return_period_days must be integer")
		self.return_period_days = return_period_days

		if (start_date and not isinstance(start_date, (datetime.datetime))) or (end_date and not isinstance(end_date, (datetime.datetime))):
			raise ValueError("start_ and end_ date must be datetime format if given")

		if not isinstance(pandas_df, pd.core.frame.DataFrame):
			raise ValueError('pandas_df must by a pandas DataFrame type')


		if start_date:	
			# if start_date is provided, first extend range by return_period_days to not exlcude first values
			pandas_df = pandas_df[pandas_df.index >= (start_date - datetime.timedelta(days=(self.return_period_days+7)))]
		if end_date:	
			pandas_df = pandas_df[pandas_df.index <= end_date]

		# convert prices to daily cumulative returns
		# this is helpful when looking into correlations and calculating betas
		returns = pandas_df / pandas_df.shift(1) - 1
		self.returns = (1 + returns).dropna(how='any')	
		self.daily_index = self.returns.cumprod().dropna(how='any')	
		# returns a dictionary item for each ticker in list with a list of its top N most highly correlated tickers
		self.period_returns = (self.daily_index / self.daily_index.shift(self.return_period_days)).dropna(how='any')

		# if start_date was provided, removed extended date range
		if start_date:	
			pandas_df = pandas_df[pandas_df.index >= start_date]
			self.returns = self.returns[self.returns.index >= start_date]
			self.daily_index = self.daily_index[self.daily_index.index >= start_date]
			self.period_returns = self.period_returns[self.period_returns.index >= start_date]

		self.df = pandas_df
		self.start_date = self.df.index[0]
		self.end_date = self.df.index[-1]
		self.tickers = list(self.df.columns)

	def get_ticker_highest_corr(self, max_pairs=3): #, min_corr=None):
		
		corr_matrix = self.period_returns.corr()
		cols = corr_matrix.columns
		
		self.highest_corr_pairs_tickers = {}
		self.highest_corr_pairs_values = {}
		for c in cols:
			pair_wise_corr = corr_matrix[c].copy()
			pair_wise_corr = pair_wise_corr.drop(c)
			pair_wise_corr.sort(ascending=False)
			
			#if min_corr:
			#	pair_wise_corr = pair_wise_corr[pair_wise_corr >= min_corr]
			
			self.highest_corr_pairs_tickers[c] = list(pair_wise_corr.index[:max_pairs])
			self.highest_corr_pairs_values[c] = list(pair_wise_corr[:max_pairs])

	def find_partner_betas(self):
		
		try:
			self.highest_corr_pairs_tickers
		except:
			raise Exception('Must first run get_ticker_highest_corr to find closest matches.')

		self.betas = {}
		for ticker in self.tickers:
			self.betas[ticker] = []
			p1 = w.period_returns[ticker]
			for i in range(len(w.highest_corr_pairs_tickers[ticker])):
				p2 = w.period_returns[w.highest_corr_pairs_tickers[ticker][i]]
			
				covmat = np.cov(p1, p2)
				beta = covmat[0,1]/covmat[1,1]
				self.betas[ticker].append(beta)
			



if __name__ == "__main__":

	tix = ['AA', 'AAPL', 'GE', 'IBM', 'JNJ', 'MSFT', 'PEP', 'XOM', 'SPX']
	df = get_collection_as_pandas_df(tix, 'test')

	w = Window(df, start_date=datetime.datetime(2010,1,1,0,0), end_date=datetime.datetime(2010,4,5,0,0))
	"""
	print w.start_date
	print w.end_date
	print w.returns.head()
	print w.daily_index.head()
	print w.period_returns.head()
	print w.df.head()
	"""

	w.get_ticker_highest_corr()
	w.find_partner_betas()
	pprint(w.highest_corr_pairs_values)
	pprint(w.betas)
	
	
	
	
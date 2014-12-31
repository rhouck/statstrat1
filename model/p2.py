from pprint import pprint
from sets import Set
import random
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2, f_regression
from sklearn.svm import LinearSVC
from sklearn import linear_model
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
			pandas_df = pandas_df[pandas_df.index >= (start_date - datetime.timedelta(days=(self.return_period_days+20)))]
		if end_date:	
			pandas_df = pandas_df[pandas_df.index < end_date]

		# drop columns/tickers with any missing pricing data
		pandas_df = pandas_df.dropna(axis=1,)

		# convert prices to daily cumulative returns
		# this is helpful when looking into correlations and calculating betas
		returns = pandas_df / pandas_df.shift(1) - 1
		
		# smoooth over extreme return values due to stock splits
		f = lambda x: 0 if x > 1 or x < -0.5 else x
		returns = returns.applymap(f)

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
		
	def get_index_period_returns(self, index_ticker, collection_name='index_test'):
		
		# pull index ticker returns based on same date ranges given for window
		index_tickers = ['^GSPC', '^IXIC']
		pandas_df = get_collection_as_pandas_df(index_tickers, collection_name, update=False)
		pandas_df = pandas_df[[index_ticker,]]

		# if start_date is provided, first extend range by return_period_days to not exlcude first values
		pandas_df = pandas_df[pandas_df.index >= (self.start_date - datetime.timedelta(days=(self.return_period_days+20)))]
		pandas_df = pandas_df[pandas_df.index <= self.end_date]
		
		# drop columns/tickers with any missing pricing data
		pandas_df = pandas_df.dropna(axis=1,)

		# convert prices to daily cumulative returns
		# this is helpful when looking into correlations and calculating betas
		returns = pandas_df / pandas_df.shift(1) - 1
		returns = (1 + returns).dropna(how='any')	
		daily_index = returns.cumprod().dropna(how='any')	
		# returns a dictionary item for each ticker in list with a list of its top N most highly correlated tickers
		period_returns = (daily_index / daily_index.shift(self.return_period_days)).dropna(how='any')

		pandas_df = pandas_df[pandas_df.index >= self.start_date]
		returns = returns[returns.index >= self.start_date]
		daily_index = daily_index[daily_index.index >= self.start_date]
		period_returns = period_returns[period_returns.index >= self.start_date]

		# get period returns as series
		period_returns = period_returns[period_returns.columns[0]]
		return period_returns


	def cointegration_test(self, y, x, criteria='5%'):
	    # criteria - 1-cirteria sets detmines how confident we are we've identified all cointegrated pairs
	    # a lower criteria will tend to result in more matches
	    ols_result = sm.OLS(y, x).fit() 
	    adf = ts.adfuller(ols_result.resid)
	    if (adf[0] < adf[4][criteria]):
	        boolean = False
	    else:
	        boolean = True
	    return boolean

	
	def find_cointegration_partners(self):
		# cycles through available tickers to find cointegrated pairs
		# sets self.pairs as a collection of pair Sets
		
		print "Recalculating cointegrated pairs"
		# first drop mongodb records of pairs
		db = Mongo()
		collection = db.db['cointegrated_pairs']
		# remove old record
		collection.remove({'start_date': self.start_date, 'end_date': self.end_date})
		entry = {'start_date': self.start_date, 'end_date': self.end_date, 'pairs': []}

		# add check for failed matched pairs
		past_tickers_seen = []
		for ind, t1 in enumerate(self.tickers):
			
			print "Checking matches for %s" % (t1)
			p1 = self.period_returns[t1]
			
			for c, t2 in enumerate(self.tickers):

				if c % 150 == 0 and c != 0:
					print "t1: %s - total matches: %s -- %s" % (t1, len(entry['pairs']), datetime.datetime.now())
				if t2 != t1 and t2 not in past_tickers_seen:
					p2 = self.period_returns[t2]			
					match =	self.cointegration_test(p1, p2)
					if match:		
						entry['pairs'].append({t1: 1, t2: 1})	
			
			past_tickers_seen.append(t1)			
					
		collection.insert(entry)
		db.client.close()

	def pull_cointegrated_partners(self, date_strict=False):

		db = Mongo()
		collection = db.db['cointegrated_pairs']

		if date_strict:
			mongo_pairs = collection.find({'start_date': self.start_date, 'end_date': self.end_date}).limit(1)
		else:
			mongo_pairs = collection.find({'end_date': {"$lte": self.end_date}}).sort([('end_date', DESCENDING),('start_date', DESCENDING)]).limit(1)
		res = list(mongo_pairs)
		
		if not res:
			self.find_cointegration_partners()
			mongo_pairs = collection.find({'start_date': self.start_date, 'end_date': self.end_date}).limit(1)
			res = list(mongo_pairs)
		
		db.client.close()

		pairs = []
		for i in res[0]['pairs']:
			pairs.append(Set([k for k in i.iterkeys()]))
		
		return list(Set(pairs))

		

	def calculate_pair_betas(self, x, y):
	
		if x.shape != y.shape:
			raise ValueError("Both series must have same shape")

		covmat = np.cov(x, y)
		beta = covmat[0,1]/covmat[1,1]
		return beta

	def get_index_betas_for_all_stocks(self, index_ticker):
		
		# iterates through ticker list to calculate market betas for each
		index_period_returns = self.get_index_period_returns(index_ticker)
		betas = {}

		for i in range(len(self.tickers)):
			try:
				beta = self.calculate_pair_betas(self.period_returns[self.tickers[i]], index_period_returns)	
				betas[self.tickers[i]] = beta
			except Exception as err:
				print "Can't find beta for ticker: %s - %s" % (i, err)
		return betas

	def get_cointegrated_beta_list(self, ticker, pairs, beta_list):
		# for a given ticker, return beta list containing only cointegrated stocks
		pairs_beta_list = {}
		for i in pairs:
			if ticker in i:
				pair = [t for t in i if t != ticker][0]
				#if pair in self.period_returns.columns:
				if pair in beta_list:
					pairs_beta_list[pair] = beta_list[pair]
		return pairs_beta_list

	def find_beta_X_portfolio(self, desired_beta, beta_list):

		keys = [k for k in beta_list.iterkeys()]
		betas = [beta_list[k] for k in keys]	
		portfolio_weights = {'long': {}, 'short': {}}

		
		# ensure coeffs sum to one
		last_beta = betas.pop()
		target = desired_beta - ((1.) * last_beta)
		aug_betas = [b-last_beta for b in betas]

		clf = linear_model.Ridge(alpha = 0.0, fit_intercept = False,)
		clf.fit([aug_betas,], [target,])

		coefs = list(clf.coef_)
		# add back coefficeint for popped beta
		coefs.append((1-sum([c for c in coefs])))

		for i in range(len(keys)):
			portfolio_weights['long'][keys[i]] = coefs[i]

		"""
		target = desired_beta
		clf = linear_model.Ridge(alpha = 0.001, fit_intercept = False)
		clf.fit([betas,], [target,])

		coefs = list(clf.coef_)
		abs_sum = sum([abs(c) for c in coefs])
		
		for i in range(len(keys)):
			weight = abs(coefs[i]) / abs_sum
			position = 'long' if coefs[i] > 0 else 'short'
			portfolio_weights[position][keys[i]] = weight
		"""
		return portfolio_weights


	def build_market_neutral_portfolio(self, long_tickers, short_tickers, beta_list):

		# given a list of short and long picks, return weights for a market neutral portfolio
		
		avg_beta_long = sum([beta_list[t] for t in long_tickers]) / len(long_tickers)
		
		avg_beta_short = sum([beta_list[t] for t in short_tickers]) / len(short_tickers)
		
		agg_long_weight = 1. - (avg_beta_long / (avg_beta_long + avg_beta_short))
		agg_short_weight = 1. - (avg_beta_short / (avg_beta_long + avg_beta_short))	
		
		portfolio_weights = {'long': {}, 'short': {}}
		for i in long_tickers:
			portfolio_weights['long'][i] = agg_long_weight / len(long_tickers)
		for i in short_tickers:
			portfolio_weights['short'][i] = agg_short_weight / len(short_tickers)
		"""
		
		portfolio_weights = {'long': {}, 'short': {}}

		long_betas = {}
		for i in long_tickers:
			long_betas[i] = beta_list[i]

		short_betas = {}
		for i in short_tickers:
			short_betas[i] = beta_list[i]

		portfolio_weights['long'] = self.find_beta_X_portfolio(1, long_betas)['long']
		portfolio_weights['short'] = self.find_beta_X_portfolio(1, short_betas)['long']
		
		for i in ('long', 'short'):
			for k, v in portfolio_weights[i].iteritems():
				portfolio_weights[i][k] = v / 2
		"""
		return portfolio_weights

	def calculate_portfolio_return(self, portfolio_weights, return_period_days):
		
		if not isinstance(portfolio_weights, dict):
			raise ValueError("Portfolio_weights must be dictionary")
		if ('long' or 'short') not in portfolio_weights:
			raise KeyError("Portfolio_weights must contain long and short portfolio weight dicts (can be empty)")
		if return_period_days and not isinstance(return_period_days, int):
			raise ValueError("return_period_days must be integer")
		
		if not return_period_days:
			return_period_days = self.return_period_days

		cols = []
		weights = []
		for k, v in portfolio_weights['long'].iteritems():
			cols.append(k)
			weights.append(v)
		short_cols = []
		for k, v in portfolio_weights['short'].iteritems():
			short_cols.append(k)
			cols.append(k)
			weights.append(v)


		df = self.returns[cols] - 1
		if short_cols:
			df[short_cols] = df[short_cols] * -1.
		
		weights = pd.DataFrame(pd.Series(weights, index=cols, name=0))
		portfolio_returns = (df * weights[0]).sum(1)
		portfolio_returns = portfolio_returns + 1.0
		portfolio_daily_index = portfolio_returns.cumprod().dropna(how='any')	
		portfolio_period_returns = (portfolio_daily_index / portfolio_daily_index.shift(return_period_days)).dropna(how='any')
		return portfolio_period_returns

	def get_set_of_beta_matching_portfolios(self, pairs, beta_list, index_period_returns,):

		# return set of portfolios for each stock with cointegrated pairs, matched to the respective stocks beta

		beta_matching_portfolios = {}

		for ticker in self.tickers:
			cointigrated_beta_list = self.get_cointegrated_beta_list(ticker, pairs, beta_list)
			if len([k for k in cointigrated_beta_list.iterkeys()]) > 2:
				portfolio_weights = self.find_beta_X_portfolio(beta_list[ticker], cointigrated_beta_list)
				beta_matching_portfolios[ticker] = portfolio_weights
		return beta_matching_portfolios

	def get_set_of_peer_portfolios(self, pairs, beta_list,):

		# return set of portfolios for each stock, each portfolio made up of cointegrated peers, equally weighted

		portfolios = {}

		for ticker in self.tickers:

			cointigrated_beta_list = self.get_cointegrated_beta_list(ticker, pairs, beta_list)
			peers = [k for k in cointigrated_beta_list.iterkeys()]
			count = len(peers)

			if count > 2:
				portfolio_weights = {'long': {}, 'short': {}}
				for i in peers:
					portfolio_weights['long'][i] = 1.0 / count
				portfolios[ticker] = portfolio_weights
		
		return portfolios

	def compare_stock_performance_to_peer_portfolio(self, ticker, portfolio_weights, return_period_days):
		
		portfolio_returns = self.calculate_portfolio_return(portfolio_weights, return_period_days=return_period_days).dropna(how='any')
		
		period_returns = (self.daily_index[ticker] / self.daily_index[ticker].shift(return_period_days)).dropna(how='any')

		last_ticker_date = period_returns.index[-1]
		ticker_excess_return = (period_returns.ix[last_ticker_date] - portfolio_returns.ix[last_ticker_date]) / period_returns.std()
		return ticker_excess_return

	def simple_score(self, ticker, portfolio_weights, return_period_days):
		
		#portfolio_returns = self.calculate_portfolio_return(portfolio_weights, return_period_days=return_period_days).dropna(how='any')
		
		period_returns = (self.daily_index[ticker] / self.daily_index[ticker].shift(return_period_days)).dropna(how='any')

		last_ticker_date = period_returns.index[-1]
		ticker_return = (period_returns.ix[last_ticker_date]) / period_returns.std()
		"""
		ticker_return = random.random() / 10.0
		sign_flip = random.randint(0,1)
		if sign_flip:
			ticker_return = -1.0 * ticker_return
		"""
		return ticker_return

	def relative_performnace_to_peer_by_beta(self, ticker, portfolio_weights, return_period_days):
		
		portfolio_returns = self.calculate_portfolio_return(portfolio_weights, return_period_days=return_period_days).dropna(how='any')
		
		period_returns = (self.daily_index[ticker] / self.daily_index[ticker].shift(return_period_days)).dropna(how='any')

		beta = self.calculate_pair_betas(period_returns, portfolio_returns)
		
		if beta >= 0.5:
			last_ticker_date = period_returns.index[-1]
			ticker_return = (period_returns.ix[last_ticker_date]) - 1.0 # / 1.0 # period_returns.std()
			portfolio_return = (portfolio_returns.ix[last_ticker_date])
			expected_ticker_return = (portfolio_return - 1.0) * beta
			excess_return = ticker_return - expected_ticker_return
			#return excess_return
			scaled_excess_return = excess_return / period_returns.std()
			return scaled_excess_return
		else: 
			return 0

	def get_list_of_recent_relative_performance(self, portfolios, return_period_days):

		# runs compare_stock_performance_to_peer_portfolio on all tickers, recording results into 2d array
		performance_chart = []
		for ticker in self.tickers:
			try:
				performance = self.simple_score(ticker, portfolios[ticker], return_period_days)
				performance_chart.append([ticker, performance])
			except Exception as err:
				pass
				#print "Could not calcualte recent performance - %s" % (err)
		performance_chart = pd.DataFrame(data=performance_chart, index=None, columns=['tickers', 'over_performance'])
		performance_chart = performance_chart.sort(columns=['over_performance'])

		return performance_chart

	def get_portfolio_weights_for_target_tickers(self, performance_chart, beta_list, test=None):
		
		# filter out excessively high / low performing stocks
		# pick top and bottom X performing stocks
		
		if test == 'beta-1':
			# build random portfolio that mostly tracks market performance
			count = 300
			selected = random.sample(performance_chart.index, count)
			tickers = performance_chart.ix[selected]['tickers'].values
			portfolio_weights = {'long': {}, 'short': {}}
			for i in tickers:
				portfolio_weights['long'][i] = 1.0 / count 
			return portfolio_weights
		elif test == 'beta-0':
			# build random portoflio that is beta neutral
			selected = random.sample(performance_chart.index, 200)
			long_tickers = performance_chart.ix[selected[:100]]['tickers'].values
			short_tickers = performance_chart.ix[selected[100:]]['tickers'].values
			return self.build_market_neutral_portfolio(long_tickers, short_tickers, beta_list)
		else:

			#performance_chart = performance_chart[performance_chart['over_performance'] > -.1]
			#performance_chart = performance_chart[performance_chart['over_performance'] < .1]
		
			long_tickers = performance_chart['tickers'].head(25).values
			short_tickers = performance_chart['tickers'].tail(25).values
			return self.build_market_neutral_portfolio(long_tickers, short_tickers, beta_list)

	def get_stat_arb_portfolio(self, return_period_days, test=None):

		pairs = self.pull_cointegrated_partners(date_strict=False)

		beta_list = self.get_index_betas_for_all_stocks(index_ticker='^GSPC')

		index_period_returns = self.get_index_period_returns('^GSPC')

		# for each stock, find a portfolio of peers that has same beta
		#portfolios = self.get_set_of_beta_matching_portfolios(pairs, beta_list, index_period_returns,)
		portfolios = self.get_set_of_peer_portfolios(pairs, beta_list)

		# compare return of a stock to its peer portfolio
		# log excess returns for each stock, keep track of best and worst
		performance_chart = self.get_list_of_recent_relative_performance(portfolios, return_period_days)
		#print performance_chart
		# check returns of market neutral portfolio over a period of time
		portfolio_weights = self.get_portfolio_weights_for_target_tickers(performance_chart, beta_list, test)
		"""
		sum_weight = 0
		for i in ('long', 'short'):
			for k, v in portfolio_weights[i].iteritems():
				sum_weight += v
		print sum_weight
		"""
		#print portfolio_weights 
		# combine best and worst to build market neutral portfolio
		portfolio_returns = self.calculate_portfolio_return(portfolio_weights, self.return_period_days)

		print "portfolio beta: %s" % (self.calculate_pair_betas(portfolio_returns, index_period_returns.ix[portfolio_returns.index]))

		return {'portfolio_weights': portfolio_weights, 'beta_list': beta_list, 'performance_chart': performance_chart, 'pairs': pairs}


if __name__ == "__main__":

	tix = get_import_io_s_and_p_tickers()
	df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
	w = Window(df, start_date=datetime.datetime(2010,7,1,0,0), end_date=datetime.datetime(2014,10,1,0,0), return_period_days=1)
	w.get_stat_arb_portfolio(return_period_days=7)
	
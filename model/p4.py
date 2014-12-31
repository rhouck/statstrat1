import csv
import math

from p3 import *

def update_splash_page_inputs(location="", return_period_days=5, return_period_days_fwd=5):
	
	portfolio_returns = pd.io.parsers.read_csv('%smodel_output/test_results.csv' % (location), index_col=0, parse_dates=True)
 	
 	if portfolio_returns.shape[0] == 0:
 		raise Exception("Must first run model simulation to generate test_results.csv.")
 	#if (portfolio_returns.index[-1] - portfolio_returns.index[0]) < datetime.timedelta(days=365):
 	#	raise Exception("Simulation must be run for period of at least one year.")

	# build short / long picks csv
	tix = get_import_io_s_and_p_tickers(location)
	df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
	

	test_date = df.index[-1] + datetime.timedelta(days=1)
	w = Window(df, start_date=(test_date-datetime.timedelta(days=150)), end_date=test_date, return_period_days=return_period_days)
	portfolio = w.get_stat_arb_portfolio(return_period_days=return_period_days)
	period_returns = (w.daily_index / w.daily_index.shift(return_period_days)).tail(1) - 1
	
	rows = {}
	for i in ('long', 'short'):
	    rows[i] = []
	    for k, v in portfolio['portfolio_weights'][i].iteritems():

	        temp = {}
	        try:
		        temp['ticker'] = k
		        temp['weight'] = v
		        temp['score'] = -1. * portfolio['performance_chart'][portfolio['performance_chart']['tickers'] == k]['over_performance'].values[0]
		        temp['returns'] = period_returns[k].values[0]
		        temp['pairs'] = [p for p in w.get_cointegrated_beta_list(k, portfolio['pairs'], portfolio['beta_list']).iterkeys()] 
	        except:
	        	pass
	        rows[i].append(temp)
	
	cols = [k for k in rows['long'][0].iterkeys()]
	for i in ('long', 'short'):
		df = pd.DataFrame.from_records(rows[i], columns=cols)
		ascending = False if i == 'long' else True
		df = df.sort(columns=['score'], ascending=ascending)
		df.to_csv('%smodel_output/%s_picks.csv' % (location, i))

 	# build ttm returns, beta and sharpe ratio
 	start_date = portfolio_returns.index[-1] - datetime.timedelta(days=365)
 	date_range = portfolio_returns.index[portfolio_returns.index > start_date]
 	portfolio_returns_prod = portfolio_returns.ix[date_range].cumprod()
 	ttm_return = (portfolio_returns_prod.ix[date_range[-1]] / portfolio_returns_prod.ix[date_range[0]])['%s' % (return_period_days_fwd)] - 1

 	rfr = .02
 	selected = portfolio_returns.ix[date_range]['%s' % (return_period_days_fwd)] - 1# -rfr
 	periods = 365.0 / ((selected.index[5] - selected.index[0]).days / 5.0)
 	sharpe = (selected.mean() / selected.std()) * math.sqrt(periods)
 	
 	
 	# store index returns
	date_range = portfolio_returns.index
	
	index_tix = ['^GSPC', '^IXIC']
	index = get_collection_as_pandas_df(index_tix, 'index_test')
	index = index.ix[date_range]['^GSPC']

	index_returns = (index.shift(-1) / index)
	index_returns.to_csv('%smodel_output/index_returns.csv' % (location))

 	ttm_beta = w.calculate_pair_betas(portfolio_returns.ix[date_range[:-1]]['%s' % (return_period_days_fwd)], index_returns[:-1]) 	

 	summary = {'ttm_return': ttm_return, 
 				'ttm_sharpe': sharpe, 
 				'ttm_beta': ttm_beta,
 				'latest_date': date_range[-1], 
 				'return_period_days': return_period_days, 
 				'return_period_days_fwd': return_period_days_fwd,
 				'updated_date': datetime.datetime.now()}

 	with open('%smodel_output/summary_stats.csv' % (location), 'w') as csvfile:
	    fieldnames = [k for k in summary.iterkeys()]
	    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	    row = {}
	    for f in fieldnames:
	    	row[f] = summary[f]
	    writer.writeheader()
	    writer.writerow(row)


if __name__ == "__main__":

	update_splash_page_inputs()
	"""
	client = MongoClient()
	db = client['strat1']
	collection = db['cointegrated_pairs']
	mongo_pairs = collection.find({},{'end_date': 1, 'start_date': 1, '_id': 0}).sort([('end_date', DESCENDING),('start_date', DESCENDING)])
 	print mongo_pairs.count()
 	for i in list(mongo_pairs):
 		print i
 		print ""
 	"""

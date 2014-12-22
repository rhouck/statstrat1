import csv
import math

from p3 import *

def update_splash_page_inputs(location="", return_period_days=7, return_period_days_fwd=7):
	
	portfolio_returns = pd.io.parsers.read_csv('%smodel_output/test_results.csv' % (location), index_col=0, parse_dates=True)
 	
 	if portfolio_returns.shape[0] == 0:
 		raise Exception("Must first run model simulation to generate test_results.csv.")
 	if (portfolio_returns.index[-1] - portfolio_returns.index[0]) < datetime.timedelta(days=365):
 		raise Exception("Simulation must be run for period of at least one year.")

	# build short / long picks csv
	tix = get_import_io_s_and_p_tickers(location)
	df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
	w = Window(df, start_date=datetime.datetime(2014,7,1,0,0), end_date=datetime.datetime(2014,10,1,0,0), return_period_days=1)
	portfolio = w.get_stat_arb_portfolio(return_period_days=return_period_days)
	
	period_returns = (w.daily_index / w.daily_index.shift(return_period_days)).tail(1) - 1

	rows = {}
	for i in ('long', 'short'):
	    rows[i] = []
	    for k, v in portfolio['portfolio_weights'][i].iteritems():

	        temp = {}
	        temp['ticker'] = k
	        temp['weight'] = v
	        temp['score'] = -1. * portfolio['performance_chart'][portfolio['performance_chart']['tickers'] == k]['over_performance'].values[0]
	        temp['returns'] = period_returns[k].values[0]
	        temp['pairs'] = [p for p in w.get_cointegrated_beta_list(k, portfolio['pairs'], portfolio['beta_list']).iterkeys()] 
	        rows[i].append(temp)
	
	for i in ('long', 'short'):
		df = pd.DataFrame.from_records(rows[i], columns=[k for k in rows[i][0].iterkeys()])
		ascending = False if i == 'long' else True
		df = df.sort(columns=['score'], ascending=ascending)
		df.to_csv('%smodel_output/%s_picks.csv' % (location, i))
 	

 	# build ttm returns and sharpe ratio
 	start_date = portfolio_returns.index[-1] - datetime.timedelta(days=370)
 	date_range = portfolio_returns.index[portfolio_returns.index > start_date]
 	portfolio_returns_prod = portfolio_returns.ix[date_range].cumprod()
 	ttm_return = (portfolio_returns_prod.ix[date_range[-1]] / portfolio_returns_prod.ix[date_range[0]])['%s' % (return_period_days_fwd)] - 1

 	rfr = .02
 	selected = portfolio_returns.ix[date_range]['%s' % (return_period_days_fwd)] - 1# -rfr
 	sharpe = (selected.mean() / selected.std()) * math.sqrt(52.)
 	#sharpe = (portfolio_returns.ix[date_range].mean() / portfolio_returns.ix[date_range].std()) * 52^0.5
 	#std = portfolio_returns.ix[date_range]['%s' % (return_period_days_fwd)].std()
 	#sharpe = (ttm_return - rfr ) / portfolio_returns.ix[date_range]['%s' % (return_period_days_fwd)].std()
 	
 	summary = {'ttm_return': ttm_return, 
 				'ttm_sharpe': sharpe, 
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


	# store index returns
	date_range = portfolio_returns.index
	
	index_tix = ['^GSPC', '^IXIC']
	index = get_collection_as_pandas_df(index_tix, 'index_test')
	index = index.ix[date_range]['^GSPC']

	returns = (index.shift(-1) / index)
	returns.to_csv('%smodel_output/index_returns.csv' % (location))
	"""
	data = {}
	columns = [int(c) for c in portfolio_returns.columns]
	for i in columns:
		data[i] = (index.shift(i) / index).ix[date_range]
	df = pd.DataFrame(data=data, columns=columns)
	df.to_csv('%smodel_output/index_returns.csv' % (location))
	"""

if __name__ == "__main__":
	"""
	portfolio_returns = pd.io.parsers.read_csv('model_output/test_results.csv', index_col=0, parse_dates=True)

	index_tix = ['^GSPC', '^IXIC']
	index = get_collection_as_pandas_df(index_tix, 'index_test')
	index = index['^GSPC',]
	index_weekly_returns = (index.shift(7) / index)
	index_weekly_returns = index_weekly_returns.ix[portfolio_returns.index]['^GSPC']
	portfolio_returns['index'] = index_weekly_returns

	portfolio_returns_prod = portfolio_returns.cumprod().dropna(how='any')
	"""

	"""
	tix = get_import_io_s_and_p_tickers()	
	end_date = datetime.datetime(2008,10,1,0,0)
	for i in range(5):
		end_date = end_date - datetime.timedelta(days=91*i)
		start_date = end_date - datetime.timedelta(days=91)
		#print end_date
		#print start_date
		
		df = get_collection_as_pandas_df(tix, 'stocks_test', update=False)
		w = Window(df, start_date=start_date, end_date=end_date, return_period_days=1)
		w.pull_cointegrated_partners(date_strict=True)
	"""
	update_splash_page_inputs()
	
	    
 	


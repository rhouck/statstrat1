from p3 import *

if __name__ == "__main__":

	portfolio_returns = pd.io.parsers.read_csv('test_results.csv', index_col=0, parse_dates=True)

	index_tix = ['^GSPC',]
	index = get_collection_as_pandas_df(index_tix, 'index_test')
	
	index_weekly_returns = (index.shift(7) / index)
	index_weekly_returns = index_weekly_returns.ix[portfolio_returns.index]['^GSPC']
	portfolio_returns['index'] = index_weekly_returns

	print portfolio_returns.cumprod().dropna(how='any')
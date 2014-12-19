import numpy as np
import csv
from sets import Set

def get_import_io_nasdaq_tickers():
	# csv built with import io at this url: http://www.advfn.com/nasdaq/nasdaq.asp?companies=A
	reader=csv.reader(open("tickers_source/nasdaq_tickers_1.csv","rb"),delimiter=',')
	x=list(reader)
	result=np.array(x)
	tickers = result[1:,6]

	tickers = np.unique(tickers)

	tickers_set = Set([])
	for i in tickers:
		if i.strip() not in tickers_set:
			tickers_set.add(i.strip())
	tickers = list(tickers_set)
	return tickers

def get_import_io_s_and_p_tickers():
	# csv built with import io at this url: http://en.wikipedia.org/wiki/List_of_S%26P_500_companies
	reader=csv.reader(open("tickers_source/s_and_p_tickers.csv","rb"),delimiter=',')
	x=list(reader)
	result=np.array(x)
	tickers = result[1:,1]

	tickers = np.unique(tickers)

	tickers_set = Set([])
	for i in tickers:
		i = i.strip()
		if i not in tickers_set and "." not in i:
			tickers_set.add(i)
	tickers = list(tickers_set)
	return tickers
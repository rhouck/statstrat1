from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.views import logout
from django.contrib.auth.views import login
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.forms.util import ErrorList

import datetime
import json
import time

import csv
import ast
from dateutil import parser

from settings import BASE_DIR

def splash(request):
	
	data = {}	
	
	# load summary stats
	with open("%s/model/model_output/summary_stats.csv" % (BASE_DIR), 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for index, row in enumerate(reader):
			if index == 0:
				columns = row
			else:
				values = row
	for i in range(len(columns)):
		data[columns[i]] = values[i] 
	data['ttm_return'] = float(data['ttm_return']) * 100
	data['latest_date'] = parser.parse(data['latest_date'])
	data['updated_date'] = parser.parse(data['updated_date'])


	# load stock pics data
	for i in ('short', 'long'):
		picks = []
		with open("%s/model/model_output/%s_picks.csv" % (BASE_DIR, i), 'rb') as csvfile:
		     reader = csv.reader(csvfile, delimiter=',')
		     for index, row in enumerate(reader):
		         if index > 0:
		            
		            # change returns to percentage
		            row[1] = float(row[1]) * 100
		            row[5] = float(row[5]) * 100

		            # interpret pairs as list
		            row[4] = ast.literal_eval(row[4])
		            picks.append(row[1:])
		data["%s_picks" %(i)] = picks
	
	# load test results
	values = []
	with open("%s/model/model_output/test_results.csv" % (BASE_DIR), 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for index, row in enumerate(reader):
			if index == 0:
				columns = row
			else:
				values.append([row[0], float(row[columns.index(str(data['return_period_days_fwd']))])])
	
	# load index returns
	index_returns = {}
	with open("%s/model/model_output/index_returns.csv" % (BASE_DIR), 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for index, row in enumerate(reader):
			try:
				index_returns[row[0]] = float(row[1]) # float(row[columns.index(str(data['return_period_days']))]) 
			except:
				pass
	
	# merge returns and convert date format
	for i in values:
		if i[0] in index_returns:
			i.append(index_returns[i[0]])
		i[0] = time.mktime(parser.parse(i[0]).timetuple()) * 1000
	
	# shift returns to future period
	shifted_values = []
	for t, i in enumerate(values):
		if t == 0:
			start_date = i[0]
		if t > 0:
			shifted_values.append([values[t][0], values[t-1][1], values[t-1][2]])
	values = shifted_values

	data['returns'] = {}
	data['returns']['strategy'] = []
	data['returns']['index'] = []
	for t, i in enumerate(values):
		data['returns']['index'].append([i[0], (i[2]-1)*100])
		data['returns']['strategy'].append([i[0], (i[1]-1)*100])

	data['returns_prod'] = {}
	data['returns_prod']['strategy'] = [[start_date, 0.]]
	data['returns_prod']['index'] = [[start_date, 0.]]
	for t, i in enumerate(values):
		data['returns_prod']['index'].append([i[0], (data['returns_prod']['index'][-1][1]+1) * i[2] -1])
		data['returns_prod']['strategy'].append([i[0], (data['returns_prod']['strategy'][-1][1]+1)*i[1]-1])
	
	for i in ('strategy', 'index'):
		for k in range(len(data['returns_prod'][i])):
			data['returns_prod'][i][k][1] = data['returns_prod'][i][k][1] * 100.
		

	#return HttpResponse(data['returns_prod']['index'])
	
	return render_to_response('splash.html', data, context_instance=RequestContext(request))
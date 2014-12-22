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
	
	
	
	return render_to_response('splash.html', data, context_instance=RequestContext(request))
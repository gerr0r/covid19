# Module for creating graphics with matplotlib

from matplotlib import pyplot as plt
#from matplotlib import dates as mpld
from datetime import datetime
from collections import Counter
from pprint import pprint

def create(graph_type,graph_period,graph_data):
	test_dict = {}
	for row in graph_data:
		print(dict(row))
		test_dict[row['short_name']] = {}
		for key in row.keys():
			if key != 'short_name': test_dict[row['short_name']][key] = []
	for row in graph_data:
		for key,value in dict(row).items():
			if key != 'short_name': test_dict[row['short_name']][key].append(value)
	print(test_dict.keys())
	pprint(test_dict)
	if graph_type == 'plot':
		if not graph_data:
			print(f'Input not found...')
		else:
			fig,ax = plt.subplots(nrows=1,ncols=1)
			print(fig)
			print(ax)
			print(type(graph_data))
			print(len(graph_data))
			print(type(graph_data[0]))
			print(len(graph_data[0]))
			print(graph_data[0].keys())
			num_countries = set(e['short_name'] for e in graph_data)
			print(num_countries)
			print(len(num_countries))
			num_apps = Counter(e['short_name'] for e in graph_data)
			print(num_apps)

			#return
			#x=0
			#plt.style.use('seaborn')
			for country in test_dict.keys():
				xaxis = set(test_dict[country].keys()).intersection(['date','week','month']).pop()
				for case,values in test_dict[country].items():
					if case not in ('confirmed','deaths','recovered','active'): continue
					else:
						plt.plot(xaxis,case,data=test_dict[country],label=f'{country} - {case}')
						#plt.set_xticklabels(test_dict[country][xaxis],rotation = 90)
						#plt.xticks(test_dict[country][xaxis],rotation = 90)
						plt.legend()
				#x += 1
			plt.xlabel(xaxis.upper())
			plt.ylabel('Total cases')
			plt.margins(x=0)
			if xaxis == 'date': 
				plt.gcf().autofmt_xdate(rotation=90)
				for label in plt.gca().xaxis.get_ticklabels()[::2]:
				    label.set_visible(False)
			#plt.xticks(xaxis,rotation = 90)
			#plt.title(f'COVID-19 {req.upper()} CASES')
			#plt.legend()
			plt.grid()
			plt.show()

	if graph_type == 'bar':
		# Create countries set to remove duplicates and count them
		countries = set(row['short_name'] for row in graph_data)
		countries_count = len(countries)
		print(f"Countries [{countries_count}]: {', '.join(countries)}")

		valid_cases = ['confirmed','recovered','deaths']
		case_color = {'confirmed':'blue','recovered':'green','deaths':'red'}
		cases = set(graph_data[0].keys()).intersection(valid_cases)
		cases_count = len(cases)
		print(f"Cases [{cases_count}]: {', '.join(cases)}")

		interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()
		interval_dict = {'date':'daily','week':'weekly','month':'monthly'}
		print(graph_period)

		if interval == 'week':
			if graph_period[1] == graph_period[2]:
				title_period = f"week: {graph_period[1]}"
			else:
				title_period = f"period: week{graph_period[1]}-week{graph_period[2]}"
		elif interval == 'month':
			if graph_period[1] == graph_period[2]:
				title_period = f"month: {datetime.strptime(str(graph_period[1]),'%m').strftime('%B')}"
			else:
				title_period = f"period: {datetime.strptime(str(graph_period[1]),'%m').strftime('%B')}-{datetime.strptime(str(graph_period[2]),'%m').strftime('%B')}"
		else:
			if graph_period[1] == graph_period[2]:
				title_period = f"date: {datetime.strptime(graph_period[1],'%Y-%m-%d').strftime('%B %d')}"
			else:
				title_period = f"period: {datetime.strptime(graph_period[1],'%Y-%m-%d').strftime('%B %d')}-{datetime.strptime(graph_period[2],'%Y-%m-%d').strftime('%B %d')}"

		if countries_count > 1:
			# Create list (new) with country names (because set is random
			if cases_count == 1:
				case = cases.pop()
				case_data = [row[case] for row in graph_data]
				countries = [row['short_name'] for row in graph_data]

				plt.figure(figsize=(8,6))
				plt.bar(countries,case_data)
				plt.title(f'{case} cases\n{title_period}'.upper())
				plt.ylabel('CASES FOR PERIOD')
				plt.tight_layout()
				plt.grid(axis='y')
				plt.show()


			else: #more cases more bars
				countries = sorted(countries)
				# Create dictionary with case:values from query
				cases_data = {case:[] for case in cases}
				for row in graph_data:
					for case in cases:
						cases_data[case].append(row[case])
				print(cases_data)

				import numpy as np
				plt.figure(figsize=(8,6))
				index = np.arange(countries_count)
				width = 0.4 if cases_count == 2 else 0.27 # if cases_count == 3
				offset = width/2 if cases_count == 2 else width # if cases_count == 3
				print(index)

				tmp = 0
				for case in valid_cases:
					if case in cases_data.keys():
						#plt.bar(index+tmp,cases_data[case],width,label=case,color=case_color[case])
						plt.bar([x+tmp for x in list(range(0,countries_count))],cases_data[case],width,label=case,color=case_color[case])
						tmp += width

				#plt.xticks(ticks=index+offset,labels=countries)
				plt.xticks(ticks=[x+offset for x in list(range(0,countries_count))],labels=countries)
				plt.title(f"{', '.join(cases)} cases\n{title_period}".upper())
				plt.ylabel('CASES FOR PERIOD')
				plt.tight_layout()
				plt.grid(axis='y')
				plt.legend()
				plt.show()

		else: # 1 country
			# Get country name
			country = countries.pop()

			# Get dates/weeks/months from query and create list
			interval_data = [row[interval] for row in graph_data]

			# Create list with formated dates/weeks/months for X axis
			if interval == 'week':
				interval_data = [f'W{week}' for week in interval_data]
			elif interval == 'month':
				interval_data = [datetime.strptime(str(month),'%m').strftime('%b') for month in interval_data]
			else:
				interval_data = [datetime.strptime(date,'%Y-%m-%d').strftime('%b %d') for date in interval_data]
			print(interval_data)

			if cases_count == 1:
				# Get case and create list with values from query
				case = cases.pop()
				case_data = [row[case] for row in graph_data]
				print(case_data)

				#fig, ax = plt.subplots()
				plt.figure(figsize=(8,6))
				plt.bar(interval_data,case_data)
				if interval == 'date':
					plt.xticks(rotation=90)
					import math
					jump = math.ceil(len(interval_data)/30)
					for index, label in enumerate(plt.gca().xaxis.get_ticklabels()):
					    if index % jump != 0: label.set_visible(False)
					del math
				plt.title(f'{country}\n{case} cases\n{interval_dict[interval]} statistics'.upper())
				plt.xlabel(interval.upper())
				plt.ylabel(f'{interval_dict[interval]} cases'.upper())
				plt.tight_layout()
				plt.grid(axis='y')
				plt.savefig('test2.png')
				#plt.savefig(f'pngfiles/{datetime.datetime.now().timestamp()}.png',dpi=300)
				plt.show()

			else: # more cases more bars
				# Create dictionary with case:values from query
				cases_data = {case:[] for case in cases}
				for row in graph_data:
					for case in cases:
						cases_data[case].append(row[case])
				print(cases_data)

				import numpy as np
				plt.figure(figsize=(8,6))
				index = np.arange(len(interval_data))
				width = 0.4 if cases_count == 2 else 0.27 # if cases_count == 3
				offset = width/2 if cases_count == 2 else width # if cases_count == 3
				print(index)

				tmp = 0
				for case in valid_cases:
					if case in cases_data.keys():
						plt.bar(index+tmp,cases_data[case],width,label=case,color=case_color[case])
						tmp += width

				plt.xticks(ticks=index+offset,labels=interval_data)
				if interval == 'date':
					plt.xticks(rotation=90)
					import math
					jump = math.ceil(len(interval_data)/30)
					for index, label in enumerate(plt.gca().xaxis.get_ticklabels()):
					    if index % jump != 0: label.set_visible(False)
					del math

				plt.title(f"{country}\n{', '.join(cases)} cases\n{interval_dict[interval]} statistics".upper())
				plt.xlabel(interval.upper())
				plt.ylabel(f'{interval_dict[interval]} cases'.upper())
				plt.tight_layout()
				plt.grid(axis='y')
				plt.legend()
				plt.show()

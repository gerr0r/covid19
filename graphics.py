# Module for creating graphics with matplotlib

from matplotlib import pyplot as plt
#from matplotlib import dates as mpld
from datetime import datetime
from collections import Counter
from pprint import pprint

def create(graph_type,graph_period,graph_country,graph_data):
	for row in graph_data:
		print(dict(row))

	if graph_type == 'plot':
		if not graph_data:
			print(f'Input not found...')
		else:
			data_dict = {}
			for row in graph_data:
				data_dict[row['short_name']] = {}
				for key in row.keys():
					if key != 'short_name': data_dict[row['short_name']][key] = []
			for row in graph_data:
				for key,value in dict(row).items():
					if key != 'short_name': data_dict[row['short_name']][key].append(value)
			#print(data_dict.keys())
			#pprint(data_dict)
			interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()
			#fig,ax = plt.subplots(nrows=1,ncols=1)
			plt.figure(figsize=(8,6))
			num_countries = set(e['short_name'] for e in graph_data)
			print(num_countries)
			print(len(num_countries))
			num_apps = Counter(e['short_name'] for e in graph_data)
			print(num_apps)

			#return
			#x=0
			#plt.style.use('seaborn')
			for country in data_dict.keys():
				xaxis = set(data_dict[country].keys()).intersection(['date','week','month']).pop()
				for case,values in data_dict[country].items():
					if case not in ('confirmed','deaths','recovered','active'): continue
					else:
						plt.plot(xaxis,case,data=data_dict[country],label=f'{country} - {case}')
						#plt.set_xticklabels(data_dict[country][xaxis],rotation = 90)
						#plt.xticks(data_dict[country][xaxis],rotation = 90)
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


	if graph_type == 'pie':
		if not graph_data:
			raise ValueError('No data found')
		if len(graph_data) == 1 and len(graph_country) > 1:
			raise ValueError('No data found for specified countries')
		elif len(graph_data) == 1:
			country = graph_data[0]['short_name']

			if 'week' in graph_data[0].keys():
				date_format = f" {datetime.strptime(graph_data[0]['date'],'%Y-%m-%d').strftime('week %W (%a, %d %b)')}"
			elif 'month' in graph_data[0].keys():
				date_format = f"{datetime.strptime(graph_data[0]['date'],'%Y-%m-%d').strftime('%B (%d')}"
				date_format += {'1':'th'}.get(date_format[-2],{'1':'st','2':'nd','3':'rd'}.get(date_format[-1],'th')) + ')' # Add ordinality to day
			else:
				date_format = datetime.strptime(graph_data[0]['date'],'%Y-%m-%d').strftime('%d %B')

			confirmed = f"{graph_data[0]['confirmed']:,}".replace(',',' ')

			case_count = {'deaths':graph_data[0]['deaths'],'recovered':graph_data[0]['recovered'],'active':graph_data[0]['active']}
			case_color = {'deaths':'red','recovered':'green','active':'yellow'}
			cases,colors,labels = [],[],[]
			for case,count in case_count.items():
				if count > 0:
					cases.append(count)
					count_format = f"{count:,}".replace(',',' ')
					labels.append(f"{case.title()}: {count_format}")
					colors.append(case_color[case])
					

			plt.figure(figsize=(8,6))
			plt.pie(cases,labels=labels,colors=colors,autopct='%1.1f%%',pctdistance=0.85)
			plt.title(f"{country.upper()}\n{confirmed} confirmed cases as of {date_format}.")
			#plt.legend(legend,loc='center left')
			plt.show(block=False)

		else:
			interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()
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

			case = set(graph_data[0].keys()).intersection(['confirmed','deaths','recovered','active']).pop()
			cases, labels = [],[]
			for row in graph_data:
				if row['short_name'] == 'Global':
					global_cases = row[case]
					global_cases_formated = f"{global_cases:,}".replace(',',' ')
					continue
				else:
					cases.append(row[case])
					labels.append(f"{row['short_name']}: {row[case]:,}".replace(',',' '))

			cases.append(global_cases - sum(cases))
			labels.append(f"Others: {cases[-1]:,}".replace(',',' '))

			min_percent = 1.5
			cases,labels = zip(*sorted(zip(cases,labels)))
			percents = [100*amount/global_cases for amount in cases]
			pie_labels = ['' if percent < min_percent else label for label,percent in zip(labels,percents)]
			startangle = -(len(pie_labels) - pie_labels.count(''))*3
			#print(pie_labels)
			#print(startangle)

			plt.figure(figsize=(8,6))

			patches,_,_ = plt.pie(cases,
						labels=pie_labels,
						autopct=lambda percent: f'{percent:.1f}%' if percent > min_percent else '',
						pctdistance=0.85,
						startangle=startangle)

			#print(patches)
			
			legend_handles = [handle for handle,percent in zip(patches,percents) if percent < min_percent]
			legend_labels = [f"{label} ({percent:.2f}%)" for label,percent in zip(labels,percents) if percent < min_percent]

			#h,l = zip(*[(h,l) for h,l,p in zip(z,legend,percent) if p < 1])
			#print(legend_handles)
			#print(legend_labels)
			plt.title(f"Global {case} cases: {global_cases_formated}\n{title_period.upper()}")
			if legend_handles:				
				ncol = int(len(legend_handles)/3 + 2/3) if len(legend_handles) <= 6 else 3
				plt.legend(legend_handles,legend_labels,title=f"Countries below {min_percent}%",bbox_transform=plt.gcf().transFigure,ncol=ncol,loc=8,bbox_to_anchor=(0.5,0))
			#plt.tight_layout()
			plt.show()

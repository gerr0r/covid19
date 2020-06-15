# Module for creating graphics with matplotlib

from matplotlib import pyplot as plt
from matplotlib.ticker import EngFormatter,MaxNLocator
from datetime import datetime
from pprint import pprint
from math import ceil

def create(graph_args,graph_data):

	# "Unpack" validated arguments
	graph_type = graph_args['type']
	dummy,start_date_request,final_date_request = graph_args['period']
	graph_country = graph_args['country']
	graph_cases = graph_args['cases']
	graph_debug = graph_args['debug']

	# Print data if debug
	if graph_debug:
		for row in graph_data:
			print(dict(row))

	# Raise error if data empty
	if not graph_data:
		raise ValueError('*** No data found')

	# Check graph type
	if graph_type == 'plot':
		# Check if period is given correctly
		if start_date_request == final_date_request:
			raise ValueError('*** Initial and final period dates/weeks/months must differ for plot graphs.')

		# Create countries set to remove duplicates and count them
		countries = set(row['short_name'] for row in graph_data)
		countries_count = len(countries)

		valid_cases = ['confirmed','deaths','recovered','active']
		case_color = {'confirmed':'blue','recovered':'green','deaths':'red','active':'orange'}
		cases = set(graph_data[0].keys()).intersection(valid_cases)
		cases_count = len(cases)

		interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()

		if graph_data[0][interval] > start_date_request:
			date_asked = human_date(interval,start_date_request,'title')
			date_given = human_date(interval,graph_data[0][interval],'title')
			print(f"*** Warning: Data request is from {date_asked}. First data is from {date_given}. First date adjusted to fit.")

		if graph_data[-1][interval] < final_date_request:
			date_asked = human_date(interval,final_date_request,'title')
			date_given = human_date(interval,graph_data[-1][interval],'title')
			print(f"*** Warning: Data request is from {date_asked}. Last data is from {date_given}. Last date adjusted to fit.")

		plt.figure(figsize=(8,6))

		if countries_count == 1:
			# Get country name
			country = graph_data[0]['short_name']

			# Set main title
			main_title = f"{country} cases".upper()

			# Create cases dictionary
			cases_data = {case:[] for case in cases}

			# Create list with dates for X axis
			interval_data = list()

			# Fill list with formated dates and dictionary with lists of values
			for row in graph_data:
				interval_data.append(human_date(interval,row[interval]))
				for case in cases:
					cases_data[case].append(row[case])

			# Get number of points in time
			timepoints = len(interval_data)

			# Create title with period
			period_title = f"{human_date(interval,graph_data[0][interval],'title')} - {human_date(interval,graph_data[-1][interval],'title')}"

			# Plot lines for every case specified
			for case,case_numbers in cases_data.items():
					plt.plot(interval_data,case_numbers,label=case.upper(),color=case_color[case])

		else:
			# Get case name
			case = cases.pop()

			# Remove plural form from deaths case for the main title (avoids double plural form 'deaths cases') 
			main_title = f"{case[:-1]} cases".upper() if case == 'deaths' else f"{case} cases".upper()

			# Create dictionary with country names and empty lists for dates and case numbers
			countries_data = {country:{interval:[],case:[]} for country in countries}

			# Create set with dates
			interval_data = set()

			# Fill dictionary and set with data from database query result
			for row in graph_data:
				countries_data[row['short_name']][interval].append(human_date(interval,row[interval]))
				countries_data[row['short_name']][case].append(row[case])
				interval_data.add(row[interval])

			# Create sorted list with all unique dates for X axis labels.
			interval_data = [human_date(interval,value) for value in sorted(interval_data)]

			# Get number of points in time
			timepoints = len(interval_data)

			# Create title with period
			period_title = f"{human_date(interval,graph_data[0][interval],'title')} - {human_date(interval,graph_data[-1][interval],'title')}"

			# Plot dummy X axis with all dates because start date varies based on first cases
			plt.plot(interval_data,[0]*timepoints,visible=False)

			# Plot country data
			for country,country_data in countries_data.items():
				plt.plot(country_data[interval],country_data[case],label=country.upper())

		plt.gca().yaxis.set_major_formatter(EngFormatter())
		plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
		plt.margins(x=0,y=0)

		if interval in ('date','week'):
			if timepoints > 12: plt.xticks(rotation=45)
			jump = ceil(timepoints/30)
			for index, label in enumerate(plt.gca().xaxis.get_ticklabels()):
			    if index % jump != 0: label.set_visible(False)

		plt.title(f"{main_title}\n{period_title}")
		plt.legend(fontsize = 'small')
		plt.tight_layout()
		plt.grid()
		plt.show()

	if graph_type == 'bar':
		# Count countries
		countries_count = len(set(row['short_name'] for row in graph_data))

		valid_cases = ['confirmed','recovered','deaths']
		case_color = {'confirmed':'blue','recovered':'green','deaths':'red'}
		cases = set(graph_data[0].keys()).intersection(valid_cases)
		cases_count = len(cases)

		interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()

		interval_dict = {'date':'daily','week':'weekly','month':'monthly'}

		plt.figure(figsize=(8,6))

		if countries_count == 1:
			if graph_data[0][interval] > start_date_request:
				date_asked = human_date(interval,start_date_request,'title')
				date_given = human_date(interval,graph_data[0][interval],'title')
				print(f"*** Warning: Data request is from {date_asked}. First data is from {date_given}. First date adjusted to fit.")

			if graph_data[-1][interval] < final_date_request:
				date_asked = human_date(interval,final_date_request,'title')
				date_given = human_date(interval,graph_data[-1][interval],'title')
				print(f"*** Warning: Data request is from {date_asked}. Last data is from {date_given}. Last date adjusted to fit.")

			# Get country name
			country = graph_data[0]['short_name']

			# Create cases dictionary
			cases_data = {case:[] for case in cases}

			# Create list with dates for X axis
			interval_data = list()

			# Fill list with formated dates and dictionary with lists of values
			for row in graph_data:
				interval_data.append(human_date(interval,row[interval]))
				for case in cases:
					cases_data[case].append(row[case])

			# Get number of points in time
			timepoints = len(interval_data)

			# Set width of bars and offset of ticks for X axis labels
			width = 0.8/cases_count
			offset = width*((cases_count-1)/2)

			step = 0
			for case,numbers in cases_data.items():
				indices = [index+step for index in list(range(timepoints))]
				plt.bar(indices,numbers,width,label=case.upper(),color=case_color[case])
				step += width

			ticks = [index+offset for index in list(range(timepoints))]
			plt.xticks(ticks=ticks,labels=interval_data)

			if interval in ('date','week'):
				if timepoints > 12: plt.xticks(rotation=45)
				jump = ceil(timepoints/30)
				for index, label in enumerate(plt.gca().xaxis.get_ticklabels()):
				    if index % jump != 0: label.set_visible(False)

			plt.title(f"{country} ({interval_dict[interval]} cases)".upper())
			plt.gca().yaxis.set_major_formatter(EngFormatter())
			plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
			plt.margins(x=0.01)
			plt.tight_layout()
			plt.grid(axis='y')
			plt.legend(fontsize = 'small')
			#plt.savefig('test2.png')
			#plt.savefig(f'pngfiles/{datetime.datetime.now().timestamp()}.png',dpi=300)
			plt.show()

		else:
			if graph_data[-1][interval] < final_date_request:
				date_asked = human_date(interval,final_date_request,'title')
				date_given = human_date(interval,graph_data[-1][interval],'title')
				print(f"*** Warning: Data request is from {date_asked}. Last data is from {date_given}. Last date adjusted to fit.")

			countries = [f"{row['short_name'][0:9]}..." if len(row['short_name']) > 13 else row['short_name'] for row in graph_data]

			if start_date_request == final_date_request:
				period_title = f"{human_date(interval,graph_data[0][interval],'title')}"
			else:
				period_title = f"{human_date(interval,start_date_request,'title')} - {human_date(interval,graph_data[-1][interval],'title')}"

			# Create dictionary with case:values from query
			cases_data = {case:[] for case in cases}

			# Create list for country names for Y axis labels
			countries = list()

			# Fill list with formated names and dictionary with lists of values
			for row in graph_data:
				countries.append(f"{row['short_name'][0:9]}..." if len(row['short_name']) > 13 else row['short_name'])
				for case in cases:
					cases_data[case].append(row[case])

			# Set width of bars and offset of ticks for X axis labels
			width = 0.8/cases_count
			offset = width*((cases_count-1)/2)

			step = 0
			for case,numbers in cases_data.items():
				indices = [index+step for index in list(range(countries_count))]
				plt.barh(indices,numbers,width,label=case.upper(),color=case_color[case])
				step += width

			ticks = [index+offset for index in list(range(countries_count))]
			plt.yticks(ticks=ticks,labels=countries)

			plt.title(f"{period_title}".upper())
			plt.gca().xaxis.set_major_formatter(EngFormatter())
			plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
			plt.margins(x=0.01)
			plt.tight_layout()
			plt.grid(axis='x')
			plt.legend(fontsize = 'small')
			plt.show()


	if graph_type == 'pie':
		interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()

		if len(graph_data) == 1 and len(graph_country) > 1:
			raise ValueError('*** No data found for specified countries')


		elif len(graph_data) == 1:
			# Get country name
			country = graph_data[0]['short_name']

			# Set period title
			period_title = human_date(interval,graph_data[0][interval],'title')
			if interval in ('week','month'):
				period_title += f" ({human_date('date',graph_data[0]['last_day'],'title')})"

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
			plt.title(f"{country.upper()}\n{confirmed} confirmed cases until {period_title}.")
			#plt.legend(legend,loc='center left')
			plt.show(block=False)

		else:
			# Create title with period

			if start_date_request == final_date_request:
				period_title = human_date(interval,graph_data[-1][interval],'title')
			else:
				period_title = f"{human_date(interval,start_date_request,'title')} - {human_date(interval,graph_data[-1][interval],'title')}"

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
			plt.title(f"Global {case} cases: {global_cases_formated}\n{period_title}")
			if legend_handles:				
				ncol = int(len(legend_handles)/3 + 2/3) if len(legend_handles) <= 6 else 3
				plt.legend(legend_handles,legend_labels,title=f"Countries below {min_percent}%",bbox_transform=plt.gcf().transFigure,ncol=ncol,loc=8,bbox_to_anchor=(0.5,0))
			#plt.tight_layout()
			plt.show()

def human_date(interval,value,position='label'):
	if interval == 'week':
		if position == 'title':
			return f"Week {value}"
		else:
			return f"W{value}"
	elif interval == 'month':
		if position == 'title':
			return f"{datetime.strptime(str(value),'%m').strftime('%B')}"
		else:
			return f"{datetime.strptime(str(value),'%m').strftime('%b')}"
	else:
		if position == 'title':
			date_format = f"{datetime.strptime(value,'%Y-%m-%d').strftime('%B, %d')}"
			ordinality = {'1':'th'}.get(value[-2],{'1':'st','2':'nd','3':'rd'}.get(value[-1],'th'))
			return f"{date_format}{ordinality}"
		else:
			return f"{datetime.strptime(value,'%Y-%m-%d').strftime('%b %d')}"
	

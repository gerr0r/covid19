# Module for creating graphics with matplotlib

from matplotlib import pyplot as plt
from matplotlib.ticker import EngFormatter,MaxNLocator
from datetime import datetime
from pprint import pprint

def create(graph_args,graph_data):

	# "Unpack" validated arguments
	graph_type = graph_args['type']
	graph_period = graph_args['period']
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
		if graph_period[1] == graph_period[2]:
			raise ValueError('*** Plot graph requires initial and final period dates/weeks/months.')

		# Create countries set to remove duplicates and count them
		countries = set(row['short_name'] for row in graph_data)
		countries_count = len(countries)
		#print(f"Countries [{countries_count}]: {', '.join(countries)}")

		valid_cases = ['confirmed','deaths','recovered','active']
		case_color = {'confirmed':'blue','recovered':'green','deaths':'red','active':'orange'}
		cases = set(graph_data[0].keys()).intersection(valid_cases)
		cases_count = len(cases)
		#print(f"Cases [{cases_count}]: {', '.join(cases)}")

		interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()

		plt.figure(figsize=(8,6))

		if countries_count == 1:
			# Get country name
			country = countries.pop()

			# Create cases dictionary
			cases_data = {case:[] for case in cases}

			# Fill dictionary keys (cases) with lists of values
			for row in graph_data:
				for case in cases:
					cases_data[case].append(row[case])

			# Create list with dates
			interval_data = [row[interval] for row in graph_data]

			# Create lists with formated dates/weeks/months for X axis
			if interval == 'week':
				interval_data = [f'W{week}' for week in interval_data]
				period_title = f"{interval_data[0].replace('W','week ')} - {interval_data[-1].replace('W','week ')}"
			elif interval == 'month':
				interval_data = [datetime.strptime(str(month),'%m').strftime('%b') for month in interval_data]
				period_title = f"{datetime.strptime(interval_data[0],'%b').strftime('%B')} - {datetime.strptime(interval_data[-1],'%b').strftime('%B')}"
			else:
				interval_data = [datetime.strptime(date,'%Y-%m-%d').strftime('%b %d') for date in interval_data]
				period_title = f'{interval_data[0]} - {interval_data[-1]}'

			# Plot lines for every case specified
			for case,case_numbers in cases_data.items():
					plt.plot(interval_data,case_numbers,label=case.title(),color=case_color[case])

			# Set title
			plt.title(f'{country} cases\n{period_title}'.upper())
			
		else:
			# Get case name
			case = cases.pop()

			# Remove plural form from deaths case for the title (avoids double plural form 'deaths cases') 
			case_title = case[:-1] if case == 'deaths' else case

			# Create dictionary with country names and empty lists for dates and case numbers
			countries_data = {country:{interval:[],case:[]} for country in countries}

			# Fill dictionary with data
			for row in graph_data:
				countries_data[row['short_name']][interval].append(row[interval])
				countries_data[row['short_name']][case].append(row[case])

			# Create sorted list with all unique dates.
			interval_data = sorted(set(row[interval] for row in graph_data))

			# Create lists with formated dates/weeks/months for X axis
			if interval == 'week':
				interval_data = [f'W{week}' for week in interval_data]
				period_title = f"{interval_data[0].replace('W','week ')} - {interval_data[-1].replace('W','week ')}"
				for country,country_data in countries_data.items():
					country_data[interval] = [f'W{week}' for week in country_data[interval]]
			elif interval == 'month':
				interval_data = [datetime.strptime(str(month),'%m').strftime('%b') for month in interval_data]
				period_title = f"{datetime.strptime(interval_data[0],'%b').strftime('%B')} - {datetime.strptime(interval_data[-1],'%b').strftime('%B')}"
				for country,country_data in countries_data.items():
					country_data[interval] = [datetime.strptime(str(month),'%m').strftime('%b') for month in country_data[interval]]
			else:
				interval_data = [datetime.strptime(date,'%Y-%m-%d').strftime('%b %d') for date in interval_data]
				period_title = f'{interval_data[0]} - {interval_data[-1]}'
				for country,country_data in countries_data.items():
					country_data[interval] = [datetime.strptime(date,'%Y-%m-%d').strftime('%b %d') for date in country_data[interval]]

			# Plot dummy X axis with all dates because start date varies based on first cases
			plt.plot(interval_data,[0]*len(interval_data),visible=False)

			# Plot country data
			for country,country_data in countries_data.items():
				plt.plot(country_data[interval],country_data[case],label=f'{country}')

			# Set title
			plt.title(f'{case_title} cases\n{period_title}'.upper())


		plt.xlabel(interval.upper())
		plt.ylabel('Total cases')
		plt.margins(x=0,y=0)

		if interval == 'date':
			plt.xticks(rotation=90)
			jump = int(len(interval_data)/30 + 29/30)
			for index, label in enumerate(plt.gca().xaxis.get_ticklabels()):
			    if index % jump != 0: label.set_visible(False)
		plt.legend()
		plt.tight_layout()
		plt.grid()
		plt.show()

	if graph_type == 'bar':
		# Create countries set to remove duplicates and count them
		countries = set(row['short_name'] for row in graph_data)
		countries_count = len(countries)

		valid_cases = ['confirmed','recovered','deaths']
		case_color = {'confirmed':'blue','recovered':'green','deaths':'red'}
		cases = set(graph_data[0].keys()).intersection(valid_cases)
		cases_count = len(cases)

		interval = set(graph_data[0].keys()).intersection(['date','week','month']).pop()
		interval_dict = {'date':'daily','week':'weekly','month':'monthly'}

		if interval == 'week':
			if graph_period[1] == graph_period[2]:
				title_period = f"cases from week {graph_period[1]}"
			else:
				title_period = f"cases from week {graph_period[1]} to week {graph_period[2]}"
		elif interval == 'month':
			if graph_period[1] == graph_period[2]:
				title_period = f"cases from {datetime.strptime(str(graph_period[1]),'%m').strftime('%B')}"
			else:
				title_period = f"cases from {datetime.strptime(str(graph_period[1]),'%m').strftime('%B')} to {datetime.strptime(str(graph_period[2]),'%m').strftime('%B')}"
		else:
			if graph_period[1] == graph_period[2]:
				title_period = f"cases from {datetime.strptime(graph_period[1],'%Y-%m-%d').strftime('%B %d')}"
			else:
				title_period = f"cases from {datetime.strptime(graph_period[1],'%Y-%m-%d').strftime('%B %d')} to {datetime.strptime(graph_period[2],'%Y-%m-%d').strftime('%B %d')}"

		if countries_count > 1:

			plt.figure(figsize=(8,6))

			if cases_count == 1:
				case = cases.pop()
				case_data = [row[case] for row in graph_data]
				countries = [f"{row['short_name'][0:9]}..." if len(row['short_name']) > 13 else row['short_name'] for row in graph_data]

				plt.barh(countries,case_data,label=case.upper(),color=case_color[case])

			else: #more cases more bars
				countries = sorted(countries)
				# Create dictionary with case:values from query
				cases_data = {case:[] for case in cases}
				for row in graph_data:
					for case in cases:
						cases_data[case].append(row[case])

				width = 0.4 if cases_count == 2 else 0.27 # if cases_count == 3
				offset = width/2 if cases_count == 2 else width # if cases_count == 3

				tmp = 0
				for case,numbers in cases_data.items():
					plt.barh([x+tmp for x in list(range(countries_count))],numbers,width,label=case.upper(),color=case_color[case])
					tmp += width

				plt.yticks(ticks=[x+offset for x in list(range(countries_count))],labels=countries)

			plt.title(f"{title_period}".upper())
			plt.gca().xaxis.set_major_formatter(EngFormatter())
			plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
			plt.margins(x=0,y=0)
			plt.tight_layout()
			plt.grid(axis='x')
			plt.legend(fontsize = 'small')
			plt.show()

		else: # 1 country
			# Get country name
			country = countries.pop()

			# Get dates/weeks/months from query and create list
			interval_data = [row[interval] for row in graph_data]

			# Create list with formated dates/weeks/months for X axis labels
			if interval == 'week':
				interval_data = [f'W{week}' for week in interval_data]
			elif interval == 'month':
				interval_data = [datetime.strptime(str(month),'%m').strftime('%b') for month in interval_data]
			else:
				interval_data = [datetime.strptime(date,'%Y-%m-%d').strftime('%b %d') for date in interval_data]

			plt.figure(figsize=(8,6))

			if cases_count == 1:
				# Get case and create list with values from query
				case = cases.pop()
				case_data = [row[case] for row in graph_data]

				plt.bar(interval_data,case_data,label=case.upper(),color=case_color[case])

			else: # more cases more bars
				# Create dictionary with case:values from query
				cases_data = {case:[] for case in cases}
				for row in graph_data:
					for case in cases:
						cases_data[case].append(row[case])

				width = 0.4 if cases_count == 2 else 0.27 # if cases_count == 3
				offset = width/2 if cases_count == 2 else width # if cases_count == 3

				tmp = 0
				for case,numbers in cases_data.items():
					plt.bar([x+tmp for x in list(range(len(interval_data)))],numbers,width,label=case.upper(),color=case_color[case])
					tmp += width

				plt.xticks(ticks=[x+offset for x in list(range(len(interval_data)))],labels=interval_data)

			if interval in ('date','week'):
				if len(interval_data) > 12: plt.xticks(rotation=45)
				jump = int(len(interval_data)/30 + 29/30)
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


	if graph_type == 'pie':
		if len(graph_data) == 1 and len(graph_country) > 1:
			raise ValueError('*** No data found for specified countries')
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

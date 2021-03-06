import datetime
import requests
import readline
import sqlite3
import os, sys

import dbquery
import validate_csv
import graphics
import helpdocs

#line = 'graph --period w12:51'
def commandline(line):

	if not line.strip(): return
	cmd,sep,args = line.strip().partition(' ')
	parse = f' {args.strip()}'.split(' --')	# SPLIT COMMAND LINE BY SPACE AND TWO HYPHENS


				### FIRST CHECK : EXISTING COMMAND?

	if cmd == 'help': helpdocs.help(args)
	elif cmd in ('q','quit'): exit()
	elif cmd in ('re','retry','reload'):
		print('Reloading last input...')
		last_command = readline.get_history_item(readline.get_current_history_length()-1)
		os.execv(sys.executable,['python3',sys.argv[0],last_command])
	elif cmd in ('r','restart'):
		print('Restarting program...')
		os.execv(sys.executable,['python3',sys.argv[0]])
	elif cmd == 'update':
		csv_download()
		print() #clear input prompt
	elif cmd == 'graph':
		pre_args = [x.strip() for x in parse[1:]]	   # REMOVE SPACES AROUND ARGUMENTS AND THEIR VALUES
		post_args = graph_arguments(pre_args)
		#query = dbquery.graph_dbquery(**post_args)
		data = dbquery.dbrequest(cmd,post_args)
		graphics.create(post_args,data)
	elif cmd == 'list':
		data = dbquery.dbrequest(cmd,args)
		list_countries(args,data)
	elif cmd == 'stats':
		data = dbquery.dbrequest(cmd,args)
		show_stats(args,data)
	else: 
		raise ValueError(f'*** {cmd}: unknown command.') 	# IF COMMAND DO NOT EXIST raise error

def graph_arguments(args):

	def_args = {'type':'plot','country':'global','cases':'confirmed','period':':'} # DICTIONARY OF DEFAULT VALUES FOR ARGUMENTS
	cmd_args = ['type','country','cases','period','debug']                     # LIST OF EXPECTED ARGUMENTS

	if args:									# IF THERE IS ANY ARGUMENTS
		for x in args:
			argument,separator,value = x.partition(' ')
			def_args[argument] = value.lstrip() 	# ADD OR UPDATE THEM IN THE DICTIONARY WITH DEFAULTS

#	print('Arguments:')
#	for key,value in def_args.items():
#		print('--',key,':',value)
#	print()



				### SECOND CHECK : NON-EXISTING ARGUMENTS?

	for key in def_args.keys():
		if key not in cmd_args: 
			raise ValueError(f'--{key}: invalid argument. Try <help graph> for info.')	# IF ARGUMENT DO NOT EXIST raise error



				### THIRD CHECK : INCORRECT NUMBER OF VALUES FOR ARGUMENTS?

	for key,value in def_args.items():
		#if key in cmd_args:
		if not value and key != 'debug':
			raise ValueError(f'--{key}: Argument reqiures a value.')		# IF THERE ISN'T VALUE
		if len(value.split()) > 1:
			raise ValueError(f'--{key}: Too many values. Expected 1, got {len(value.split())}')	# IF THERE IS MORE THAN ONE VALUE FOR ARGUMENT

	country = set(def_args['country'].split(',')) # REMOVE DUPLICATES
	

				### FOURTH CHECK : INVALID VALUE FOR TYPE ARGUMENT?
	type = def_args['type']
	valid_types = ['plot','bar','pie']
	if type not in valid_types:
		raise ValueError(f'--type {type}: Expecting values plot, bar or pie.')

				### FIFTH CHECK : VALID VALUES FOR CASES ARGUMENT?
	if def_args['cases'] == 'all':
		if type == 'bar':
			def_args['cases'] = 'confirmed,deaths,recovered'
		else:
			def_args['cases'] = 'confirmed,deaths,recovered,active'
	cases = set(def_args['cases'].split(',')) # REMOVE DUPLICATES
	valid_cases = ['confirmed','deaths','recovered','active']
	if type == 'bar': valid_cases.remove('active') # active cases pointless for bar charts
	for case in cases:
		if case not in valid_cases:
			raise ValueError(f'--cases {case}: Expecting values {valid_cases}')

				### SIXTH: DEBUG

	debug = True if 'debug' in def_args else False

				### SEVENTH: VALIDATE PERIOD

	period = set_bounderies(def_args['period'])

	if type == 'plot' and period[1] == period[2]:
		raise ValueError('*** Initial and final period dates/weeks/months must differ for plot graphs.')

	return {'type':type,'country':country,'cases':cases,'period':period,'debug':debug}

def set_bounderies(period):

	last_update = dbquery.dbrequest('last_update')
	if not last_update:
		raise ValueError('*** Warning: Can not retrieve last update from database. Use <update> to fix.')
	else:
		last_update = last_update[0][0]

	if period.startswith(('d','w','m')):
		interval = period[0]
		from_,sep,to_ = period[1:].partition(':')
	else:
		interval = 'd'
		from_,sep,to_ = period.partition(':')

	if not sep: to_ = from_


	if interval == 'd':
		last_day = int(datetime.datetime.strptime(last_update,'%Y-%m-%d').strftime('%d'))
		last_month = int(datetime.datetime.strptime(last_update,'%Y-%m-%d').strftime('%m'))

		if not from_: from_ = '22.01'
		if not to_: to_ = f"{last_day}.{last_month}"

		parse_from = from_.split('.')
		parse_to = to_.split('.')

		try:
			from_day = int(parse_from[0])
			from_month = int(parse_from[1])
			to_day = int(parse_to[0])
			to_month = int(parse_to[1])
		except:
			raise ValueError('Invalid period parameter(s).')

		month_days = [0,31,29,31,30,31,30,31,31,30,31,30,31]
		if not (1 <= from_month <= 12 and 1 <= from_day <= month_days[from_month]):
			raise ValueError('First date is invalid.')
		if not (1 <= to_month <= 12 and 1 <= to_day <= month_days[to_month]):
			raise ValueError('Last date is invalid.')
		if from_month > to_month or (from_month == to_month and from_day > to_day):
			raise ValueError('First date exceeds last date.')
		if to_month > last_month or (to_month == last_month and to_day > last_day):
			raise ValueError(f"Last date exceeds last update ({datetime.datetime.strptime(last_update,'%Y-%m-%d').strftime('%B, %d')})")

		from_ = datetime.date(2020,from_month,from_day).isoformat()
		to_ = datetime.date(2020,to_month,to_day).isoformat()

	if interval == 'w':
		last_ = int(datetime.datetime.strptime(last_update,'%Y-%m-%d').strftime('%W'))

		if not from_: from_ = 3 # first week default if not set
		if not to_: to_ = last_ # last week default if not set

		try: 
			from_ = int(from_)
			to_ = int(to_)
		except ValueError:
			raise ValueError('Invalid period parameter(s).')

		if from_ not in range(0,54):
			raise ValueError('First week out of range. Expected value between 0 and 53.')
		if to_ not in range(0,54):
			raise ValueError('Last week out of range. Expected value between 0 and 53.')
		if from_ > to_:
			raise ValueError('First week exceeds last week.')
		if to_ > last_:
			raise ValueError(f"Last week exceeds last update (week {last_}).")

		interval = 'W' # for sqlite week numbering notation

	if interval == 'm':
		last_ = int(datetime.datetime.strptime(last_update,'%Y-%m-%d').strftime('%m'))

		if not from_: from_ = 1 # first month default if not set
		if not to_: to_ = last_ # last month default if not set

		try: 
			from_ = int(from_)
			to_ = int(to_)
		except ValueError:
			raise ValueError('Invalid period parameter(s).')

		if from_ not in range(1,13):
			raise ValueError('First month out of range. Expected value between 1 and 12.')
		if to_ not in range(1,13):
			raise ValueError('Last month out of range. Expected value between 1 and 12.')
		if from_ > to_:
			raise ValueError('First month exceeds last month.')
		if to_ > last_:
			raise ValueError(f"Last month exceeds last update ({datetime.datetime.strptime(last_update,'%Y-%m-%d').strftime('%B')}).")


	return tuple((interval,from_,to_))


def csv_download():

	START_DATE = datetime.date(2020,1,22)
	TODAY_DATE = datetime.date.today()

	site = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports'
	filelist = [f"{(START_DATE + datetime.timedelta(days=x)).strftime('%m-%d-%Y')}.csv" for x in range(0,(TODAY_DATE-START_DATE).days+1)]

	for file in filelist:
		if not os.path.exists(f'csv_files/{file}'):
			url = f'{site}/{file}'
			try:
				response = requests.get(url)
			except requests.exceptions.ConnectionError as e:
				print('Error: check your connection and try again.')
				break
			print('*** Updating database:',round(100/len(filelist)*(filelist.index(file)+1)),'%','\r',end="",flush=True)
			if response.status_code == 200:
				# if response is ok - download csv file
				with open(f'csv_files/{file}','wb') as f:
					f.write(response.content)
				db_update(file)


def db_update(file):
	csv_file_date = datetime.datetime.strptime(file[0:-4],'%m-%d-%Y').date() # parse m-d-Y and convert to Y-m-d
	update_dates = dbquery.dbrequest('check')
	datelist = [row[0] for row in update_dates]
	#print(csv_file_date,datelist)
	if str(csv_file_date) in datelist:
		print(f'Data from {csv_file_date} already in database.')
	else:
		data = validate_csv.csv_optimize(f'csv_files/{file}')
		dbquery.dbwrite(data,csv_file_date)


def list_countries(string,data):
	if not data: 
		print(f'{string}: Results not found...')
		return
	if string: 
		print(f'Search for: {string}')
		print(30*'=')
	print('ISO2\tISO3\tCode\tNames')
	print(30*'=')
	for row in data:
		print(f'{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}')
	print(30*'=')
	print(f'{len(data)} results found.')

# Some database corrections:
def db_correction():

	c.execute("UPDATE daily_cases SET confirmed = 0 WHERE confirmed = ''")
	c.execute("DELETE FROM daily_cases WHERE confirmed = 0")
	c.execute("UPDATE daily_cases SET deaths = 0 WHERE deaths = ''")
	c.execute("UPDATE daily_cases SET recovered = 0 WHERE recovered = ''")
	conn.commit()



# Text statistics
def show_stats(country,data):
	if len(data) == 0:
		raise ValueError(f'{country.upper()}: Input not found...')
	elif len(data) == 1: new,old = data[0],(0,0,0)
	else: new,old = data
	CN,DN,RN = new # Confirmed Deaths Recovered - New
	CO,DO,RO = old # Confirmed Deaths Recovered - Old

	print((11+len(country))*'=')
	print(f'Last info: {country.upper()}')
	print((11+len(country))*'=')

	try:
		print(f'{CN} cases confirmed: {CN-CO} new. Growth: {round((CN-CO)/CO*100,1)}%')
	except ZeroDivisionError:
		print(f'{CN} cases confirmed.')

	try: 
		print(f'{DN} death cases reported: {DN-DO} new. Growth: {round((DN-DO)/DO*100,1)}%')
	except ZeroDivisionError: 
		print(f'{DN} death cases reported.')

	try: 
		print(f'{RN} recoveries reported: {RN-RO} new. Growth: {round((RN-RO)/RO*100,1)}%')
	except ZeroDivisionError: 
		print(f'{RN} recoveries reported.')

	try:
		print(f'Active cases: {CN-DN-RN} ({round((CN-DN-RN)/CN*100,1)}%)')
		print(f'Closed cases: {DN+RN} ({round((DN+RN)/CN*100,1)}%)')
		print(f'Dynamic death rate: {round(DN/CN*100,1)}% \t*Death cases against total confirmed cases ratio.')
		print(f'Dynamic recovery rate: {round(RN/CN*100,1)}% \t*Recovery cases against total confirmed cases ratio.')
	except ZeroDivisionError:
		pass

	try:
		print(f'Static death rate: {round(DN/(DN+RN)*100,1)}% \t*Death cases against total closed cases ratio.')
		print(f'Static recovery rate: {round(RN/(DN+RN)*100,1)}% \t*Recovery cases against total closed cases ratio.')
	except ZeroDivisionError:
		pass


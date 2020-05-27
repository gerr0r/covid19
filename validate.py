import datetime
import requests
import sqlite3
import os, sys

import dbquery
import validate_csv
import graphics

#line = 'graph --period w12:51'
def commandline(line):

	if not line.strip(): return
	cmd,sep,args = line.strip().partition(' ')
	parse = f' {args.strip()}'.split(' --')	# SPLIT COMMAND LINE BY SPACE AND TWO HYPHENS


				### FIRST CHECK : EXISTING COMMAND?

	if cmd == 'help': pass
	elif cmd in ('q','quit'): exit()
	elif cmd in ('r'):
		print('Restarting program...')
		os.execv(sys.executable, ['python3'] + sys.argv)
	elif cmd == 'update':
		csv_download()
		print() #clear input prompt
	elif cmd == 'graph':
		pre_args = [x.strip() for x in parse[1:]]	   # REMOVE SPACES AROUND ARGUMENTS AND THEIR VALUES
		post_args = graph_arguments(pre_args)
		query = dbquery.graph_dbquery(**post_args)
		data = get_db_data(query)
		graphics.create(post_args['type'],post_args['period'],data)
	elif cmd == 'list':
		list_countries(args)
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

	return {'type':type,'country':country,'cases':cases,'period':period,'debug':debug}

def set_bounderies(period):

	if period.startswith(('d','w','m')):
		interval = period[0]
		from_,sep,to_ = period[1:].partition(':')
	else:
		interval = 'd'
		from_,sep,to_ = period.partition(':')

	if not sep: to_ = from_


	if interval == 'd':
		if not from_: from_ = '01.01'
		if not to_: to_ = '31.12'

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

		from_ = datetime.date(2020,from_month,from_day).isoformat()
		to_ = datetime.date(2020,to_month,to_day).isoformat()

	if interval == 'w':
		if not from_: from_ = 0 # first week default if not set
		if not to_: to_ = 53 # last week default if not set

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

		interval = 'W' # for sqlite week numbering notation

	if interval == 'm':
		if not from_: from_ = 1 # first month default if not set
		if not to_: to_ = 12 # last month default if not set

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
	conn = sqlite3.connect('covid19.db')
	c = conn.cursor()
	c.execute("SELECT DISTINCT date FROM daily_cases")
	update_dates = c.fetchall()
	filelist = []
	for row in update_dates:
		filelist.append(row[0])
	print(csv_file_date,filelist)
	if str(csv_file_date) in filelist:
		print('Data from this date already in database.')
	else:
		data = validate_csv.csv_optimize(f'csv_files/{file}')
		conn = sqlite3.connect('covid19.db')
		c = conn.cursor()
		for code,cases in data.items():
			c.execute("INSERT INTO daily_cases VALUES (?,?,?,?,?)",(code,cases['confirmed'],cases['deaths'],cases['recovered'],csv_file_date))
		conn.commit()


def list_countries(string = ''):
	conn = sqlite3.connect('covid19.db')
	c = conn.cursor()
	c.execute("SELECT iso2,iso3,country_code,short_name FROM countries WHERE short_name LIKE ? ORDER BY short_name",(f'%{string}%',))
	data = c.fetchall()
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

	

def init_db():
	conn = sqlite3.connect('covid19.db')
	c = conn.cursor()
	query = dbquery.init_dbquery()
	c.execute(query)
	conn.commit()

def get_db_data(query):
	conn = sqlite3.connect('covid19.db')
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
	c.execute(query)
	data = c.fetchall()
	return data




# Some database corrections:
def db_correction():

	c.execute("UPDATE daily_cases SET confirmed = 0 WHERE confirmed = ''")
	c.execute("DELETE FROM daily_cases WHERE confirmed = 0")
	c.execute("UPDATE daily_cases SET deaths = 0 WHERE deaths = ''")
	c.execute("UPDATE daily_cases SET recovered = 0 WHERE recovered = ''")
	conn.commit()

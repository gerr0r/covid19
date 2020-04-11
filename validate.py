import datetime

def period(size,string):
	if size not in ('d','w','m','daily','weekly','monthly'):
		raise ValueError('Unknown format. Expected daily, weekly or monthly.') 
	margin = string.split(':')

	try:
		from_ = margin[0]
		to_ = margin[1]
	except IndexError:
		from_ = margin[0]
		to_ = margin[0]

	if size in ('d','daily'):
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

		ref_ = False
		from_ = datetime.date(2020,from_month,from_day).isoformat()
		if from_ > '2020-01-01':
			from_ = (datetime.date.fromisoformat(from_) - datetime.timedelta(days=1)).isoformat()
			ref_ = True
		to_ = datetime.date(2020,to_month,to_day).isoformat()
		unit_ = 'csv_file'

	if size in ('w','weekly'):
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

		ref_ = False
		if from_ > 0:
			from_ -= 1 # decrease with one week to get the difference between requered week and the one before it
			ref_ = True
		from_ = str(from_).zfill(2)
		to_ = str(to_).zfill(2)
		unit_ = 'week'


	if size in ('m','monthly'):
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

		ref_ = False
		if from_ > 1:
			from_ -= 1 # decrease with one month to get the difference between requered month and the one before it
			ref_ = True
		from_ = str(from_).zfill(2)
		to_ = str(to_).zfill(2)
		unit_ = 'mnt'


	return tuple((unit_,ref_,from_,to_))



def commandline(parse):
	if parse[0] == 'bar':
		try: country = parse[1]
		except IndexError: country = 'global'

		try: case = parse[2]
		except IndexError: case = 'confirmed'
		if case not in ('c','d','r','confirmed','deaths','recovered'):
			raise ValueError('Unexpected case value.\nTry c-confirmed, d-deaths, r-recovered or a-active.')
		else:
			case_options = {'confirmed':'confirmed','c':'confirmed','deaths':'deaths','d':'deaths','recovered':'recovered','r':'recovered'}		
			case = case_options[case]

		try: grouping = parse[3]
		except IndexError: grouping = 'daily'
		if grouping not in ('d','w','m','daily','weekly','monthly'):
			raise ValueError('Unexpected case value.\nTry d-daily, w-weekly or m-monthly.')
		else:
			grouping_options = {'daily':'daily','d':'daily','weekly':'weekly','w':'weekly','monthly':'monthly','m':'monthly'}		
			grouping = grouping_options[grouping]


		try: period = parse[4]
		except IndexError: period = ':'

		return tuple((country,case,grouping,period))


def dbquery(command,**kwargs):
	if command == 'bar':
		country_where_clause = ' '
		if kwargs['country'] != 'global':
			country_where_clause = f"WHERE country = (SELECT short_name FROM countries WHERE '{kwargs['country']}' IN (lower(short_name),lower(iso2),lower(iso3)))"

		if kwargs['grouping'] == 'daily':
			query = f"""
				SELECT csv_file,csv_file,sum({kwargs['case']}) AS {kwargs['case']},sum({kwargs['case']}) - lag(sum({kwargs['case']}),1,0) OVER (ORDER BY csv_file) AS difference FROM daily_cases
				{country_where_clause}
				GROUP BY csv_file
				HAVING csv_file BETWEEN '{kwargs['first_date']}' AND '{kwargs['last_date']}'
				"""
		else:
			strformat = "'%m'" if kwargs['grouping'] == 'monthly' else "'%W'" # monthly or weekly
			query = f"""
				SELECT max(csv_file),{kwargs['db_group']},{kwargs['case']},{kwargs['case']} - lag({kwargs['case']},1,0) OVER (ORDER BY {kwargs['db_group']}) AS difference FROM (
					SELECT csv_file,strftime({strformat},csv_file) AS {kwargs['db_group']},sum({kwargs['case']}) AS {kwargs['case']} FROM daily_cases
					{country_where_clause}
					GROUP BY csv_file
					HAVING {kwargs['db_group']} BETWEEN '{kwargs['first_date']}' AND '{kwargs['last_date']}')
				GROUP BY {kwargs['db_group']}
				"""

	return query
		

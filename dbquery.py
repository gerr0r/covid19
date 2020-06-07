
def init_dbquery():
	
	query = """CREATE TABLE IF NOT EXISTS daily_cases (
						code TEXT,
						confirmed INTEGER NOT NULL DEFAULT 0,
						deaths INTEGER NOT NULL DEFAULT 0,
						recovered INTEGER NOT NULL DEFAULT 0,
						date TEXT)"""
	return query




def graph_dbquery(**kwargs):

#	print (kwargs)
	type = kwargs['type']
	country = kwargs['country']
	cases = kwargs['cases']
	debug = kwargs['debug']
	interval,first_date,last_date = kwargs['period']
	group_by = 'month' if interval == 'm' else 'week' if interval == 'W' else 'date'
#	print(type)
#	print(country)
#	print(cases)
#	print(group_by,first_date,last_date)



										#####	#	#####	#####
										#   #	#	#   #	  #
										#####	#	#   #	  #
										#	#	#   #	  #
										#	#####	#####	  #

	if type == 'plot':
		if len(country) == 1 and 'global' in country:
			if group_by == 'date':
				db_sums = ''
				for case in cases:
					if case == 'active':
						db_sums += "sum(confirmed) - sum(deaths) - sum(recovered) AS active,\n\t"
					else:
						db_sums += f"sum({case}) AS {case},\n\t"
				db_sums = db_sums[0:-3]

				query = f"""
SELECT
	{db_sums},
	'Global' AS short_name,
	date
FROM daily_cases
WHERE date BETWEEN '{first_date}' AND '{last_date}'
GROUP BY date
ORDER BY date;
"""
			else: # if group_by in ('week','month')
				db_cases,db_sums = '',''
				for case in cases:
					db_cases += f"{case},\n\t"
					if case == 'active':
						db_sums += "sum(confirmed) - sum(deaths) - sum(recovered) AS active,\n\t\t"
					else:
						db_sums += f"sum({case}) AS {case},\n\t\t"
				db_cases = db_cases[0:-3]
				db_sums = db_sums[0:-4]

				query = f"""
SELECT
	{db_cases},
	'Global' AS short_name,
	max(date) AS last_day,
	{group_by}
FROM (
	SELECT
		{db_sums},
		date,
		CAST(strftime('%{interval}',date) AS INT) AS {group_by}
	FROM daily_cases
	GROUP BY date
	HAVING {group_by} BETWEEN {first_date} AND {last_date}
)
GROUP BY {group_by}
ORDER BY {group_by};
"""

		else:
			country_list = str(country)[1:-1] # just represent country set as a string and remove the closing curly braces
			if len(country_list) > 1 and len(cases) > 1:
				print('Only one case possible at same time for a list of countries. Case is set to default.')
				cases = ['confirmed']
			db_cases = ''
			for case in cases:
				if case == 'active':
					db_cases += "confirmed - deaths - recovered AS active,\n\t"
				else:
					db_cases += f"{case},\n\t"
			db_cases = db_cases[0:-3]

			if group_by == 'date': query = f"""
SELECT
	{db_cases},
	short_name,
	date
FROM daily_cases
LEFT JOIN countries ON code = country_code
WHERE code IN (
	SELECT country_code
	FROM countries
	WHERE lower(iso2) IN ({country_list})
	OR lower(iso3) IN ({country_list})
	OR lower(short_name) IN ({country_list})
	OR country_code IN ({country_list})
)
AND date BETWEEN '{first_date}' AND '{last_date}'
ORDER BY date;
"""
			else: query = f"""
SELECT
	{db_cases},
	short_name,
	max(date) AS last_day,
	CAST(strftime('%{interval}',date) AS INT) AS {group_by}
FROM daily_cases
LEFT JOIN countries ON code = country_code
WHERE code IN (
	SELECT country_code
	FROM countries
	WHERE lower(iso2) IN ({country_list})
	OR lower(iso3) IN ({country_list})
	OR lower(short_name) IN ({country_list})
	OR country_code IN ({country_list})
)
GROUP BY short_name,{group_by}
HAVING {group_by} BETWEEN {first_date} AND {last_date}
ORDER BY {group_by};
"""

										####	 ###	#####
										#  #	#   #	#   #
										#####	#####	#####
										#   #	#   #	#  #
										#####	#   #	#   #

	elif type == 'bar':
		if len(country) == 1 and 'global' in country:
			db_cases,db_sums,db_cases_lag_function,db_sums_lag_function = '','','',''
			for case in cases:
				db_cases += f"{case},\n\t"
				db_cases_lag_function += f"{case} - lag({case},1,0) OVER (ORDER BY date) AS {case},\n\t\t"
				db_sums_lag_function += f"sum({case}) - lag(sum({case}),1,0) OVER (ORDER BY date) AS {case},\n\t\t"
				db_sums += f"sum({case}) AS {case},\n\t\t\t"
				
			db_cases = db_cases[0:-3]
			db_cases_lag_function = db_cases_lag_function[0:-4]
			db_sums_lag_function = db_sums_lag_function[0:-4]
			db_sums = db_sums[0:-5]

			if group_by == 'date': query = f"""
SELECT 
	{db_cases},
	'Global' AS short_name,
	date
FROM (
	SELECT
		{db_sums_lag_function},
		date
	FROM daily_cases
	GROUP BY date
	HAVING date BETWEEN date('{first_date}','-1 day') AND '{last_date}'
)
WHERE date BETWEEN '{first_date}' AND '{last_date}'
ORDER BY date;
"""
			else: query = f"""
SELECT
	{db_cases},
	'Global' AS short_name,
	{group_by}
FROM (
	SELECT
		{db_cases_lag_function},
		max(date),
		{group_by}
	FROM (
		SELECT
			{db_sums},
			date,
			CAST(strftime('%{interval}',date) AS INT) AS {group_by}
		FROM daily_cases
		GROUP BY date
		HAVING {group_by} BETWEEN {first_date} - 1 AND {last_date}
	)
	GROUP BY {group_by}
)
WHERE {group_by} BETWEEN {first_date} AND {last_date}
ORDER BY {group_by};
"""

		elif len(country) == 1 and 'global' not in country:
			country = country.pop()
			db_cases,db_cases_lag_function = '',''
			for case in cases:
				db_cases += f"{case},\n\t"
				db_cases_lag_function += f"{case} - lag({case},1,0) OVER (ORDER BY date) AS {case},\n\t\t"
			db_cases = db_cases[0:-3]
			db_cases_lag_function = db_cases_lag_function[0:-4]

			if group_by == 'date': query = f"""
SELECT
	{db_cases},
	short_name,
	date
FROM (
	SELECT
		{db_cases_lag_function},
		short_name,
		date
	FROM daily_cases
	LEFT JOIN countries ON code = country_code
	WHERE code = (
		SELECT country_code
		FROM countries
		WHERE '{country}' IN (lower(iso2),lower(iso3),lower(short_name),CAST(country_code AS TEXT))
		)
	AND date BETWEEN date('{first_date}','-1 day') AND '{last_date}'
	)
WHERE date BETWEEN '{first_date}' AND '{last_date}'
ORDER BY date;
"""

			else: query = f"""
SELECT
	{db_cases},
	short_name,
	{group_by}
FROM (
	SELECT
		{db_cases_lag_function},
		short_name,
		max(date),
		CAST(strftime('%{interval}',date) AS INT) AS {group_by}
	FROM daily_cases
	LEFT JOIN countries ON code = country_code
	WHERE code = (
		SELECT country_code
		FROM countries
		WHERE '{country}' IN (lower(iso2),lower(iso3),lower(short_name),CAST(country_code AS TEXT))
		)
	GROUP BY {group_by}
	HAVING {group_by} BETWEEN {first_date}-1 AND {last_date}
	)
WHERE {group_by} BETWEEN {first_date} AND {last_date}
ORDER BY {group_by};
"""

		else:
			country_list = str(country)[1:-1] # just represent country set as a string, remove the closing curly braces and place parenthesis
			db_cases,db_cases_lag_function = '',''
			for case in cases:
				db_cases += f"{case},\n\t"
				db_cases_lag_function += f"{case} - lag({case},1,0) OVER (PARTITION BY short_name ORDER BY date) AS {case},\n\t\t"
			db_cases = db_cases[0:-3]
			db_cases_lag_function = db_cases_lag_function[0:-4]

			if group_by == 'date': query = f"""
SELECT
	{db_cases},
	short_name,
	max(date) AS date
FROM (
	SELECT
		{db_cases_lag_function},
		short_name,
		date
	FROM daily_cases
	LEFT JOIN countries ON code = country_code
	WHERE code IN (
		SELECT country_code
		FROM countries
		WHERE lower(iso2) IN ({country_list})
		OR lower(iso3) IN ({country_list})
		OR lower(short_name) IN ({country_list})
		OR country_code IN ({country_list})
		)
	AND (
		date = date('{first_date}','-1 day')
		OR date = (
			SELECT max(date)
			FROM daily_cases
			WHERE date <= '{last_date}'
			)
		)
	)
GROUP BY short_name
ORDER BY {f'{case} DESC,short_name;' if len(cases) == 1 else 'short_name;'}
"""

			else: query = f"""
SELECT
	{db_cases},
	short_name,
	{group_by},
	max(last_{group_by}_day) AS last_{group_by}_day
FROM (
	SELECT
		{db_cases_lag_function},
		short_name,
		max(date) AS last_{group_by}_day,
		CAST(strftime('%{interval}',date) AS INT) AS {group_by}
	FROM daily_cases
	LEFT JOIN countries ON code = country_code
	WHERE code IN (
		SELECT country_code
		FROM countries
		WHERE lower(iso2) IN ({country_list})
		OR lower(iso3) IN ({country_list})
		OR lower(short_name) IN ({country_list})
		OR country_code IN ({country_list})
		)
	GROUP BY short_name,{group_by}
	HAVING {group_by} = {first_date} - 1
	OR {group_by} = (
		SELECT CAST(strftime('%{interval}',max(date)) AS INT)
		FROM daily_cases
		WHERE CAST(strftime('%{interval}',date) AS INT) <= {last_date}
		)
	)
GROUP BY short_name
ORDER BY {f'{case} DESC,short_name;' if len(cases) == 1 else 'short_name;'}
"""

										#####	#####	#####
										#   #	  #	#
										#####	  #	###
										#	  #	#
										#	#####	#####

	elif type == 'pie':
		if len(country) == 1 and 'global' in country:
			if group_by == 'date': query = f"""
SELECT 
	'Global' AS short_name,
	date,
	sum(confirmed) AS confirmed,
	sum(deaths) AS deaths,
	sum(recovered) AS recovered,
	sum(confirmed) - sum(deaths) - sum(recovered) AS active
FROM daily_cases
WHERE date = (
	SELECT max(date)
	FROM daily_cases
	WHERE date <= '{last_date}'
	)
"""


			else: query = f"""
SELECT 
	'Global' as short_name,
	CAST(strftime('%{interval}',date) AS INT) AS {group_by},
	date,
	sum(confirmed) AS confirmed,
	sum(deaths) AS deaths,
	sum(recovered) AS recovered,
	sum(confirmed)-sum(deaths)-sum(recovered) AS active
FROM daily_cases
WHERE date = (
	SELECT max(date)
	FROM daily_cases
	WHERE CAST(strftime('%{interval}',date) AS INT) <= {last_date}
	)
"""

		elif len(country) == 1 and 'global' not in country:
			country = country.pop()
			if group_by == 'date': query = f"""
SELECT 	
	short_name,
	date,
	confirmed,
	deaths,
	recovered,
	confirmed - deaths - recovered AS active
FROM daily_cases
LEFT JOIN countries ON code = country_code
WHERE code = (
	SELECT country_code
	FROM countries
	WHERE '{country}' IN (lower(iso2),lower(iso3),lower(short_name),CAST(country_code AS TEXT))
	)
AND date = (
	SELECT max(date)
	FROM daily_cases
	WHERE date <= '{last_date}'
	)
"""


			else: query = f"""
SELECT 	
	short_name,
	CAST(strftime('%{interval}',date) AS INT) AS {group_by},
	date,
	confirmed,
	deaths,
	recovered,
	confirmed - deaths - recovered AS active
FROM daily_cases
LEFT JOIN countries ON code = country_code
WHERE code = (
	SELECT country_code
	FROM countries
	WHERE '{country}' IN (lower(iso2),lower(iso3),lower(short_name),CAST(country_code AS TEXT))
	)
AND date = (
	SELECT max(date)
	FROM daily_cases
	WHERE CAST(strftime('%{interval}',date) AS INT) <= '{last_date}'
	)
"""


		else: # if len(country) > 1 (list of countries)
			country_list = str(country)[1:-1] # just represent the whole country set as a string and get rid of closing curly braces
			if len(cases) > 1:
				print('Only one case possible at same time for a list of countries. Case is set to default.')
				case = 'confirmed' # default
			else:
				case = cases.pop()

			if case == 'active':
				first_date = '2020-01-01' if group_by == 'date' else 0

			if group_by == 'date': query = f"""
SELECT
	short_name,
	max(date) AS date,
	{case}
FROM (	
	SELECT
		short_name,
		date,
		{case} - lag({case},1,0) OVER (PARTITION BY short_name ORDER BY date) AS {case}
	FROM (	
		SELECT 	
			short_name,
			date,
			{'confirmed - deaths - recovered AS active' if case == 'active' else case}
		FROM daily_cases
		LEFT JOIN countries ON code = country_code
		WHERE code IN (		
			SELECT country_code
			FROM countries 
			WHERE lower(iso2) IN ({country_list})
			OR lower(iso3) IN ({country_list})
			OR lower(short_name) IN ({country_list})
			OR country_code IN ({country_list})
			)
		AND (
			date = date('{first_date}','-1 day')
			OR date = (
				SELECT max(date)
				FROM daily_cases
				WHERE date <= '{last_date}'
			)
		)
		UNION
		SELECT 
			'Global',
			date,
			{'sum(confirmed) - sum(deaths) - sum(recovered) AS active' if case == 'active' else f'sum({case})'}
		FROM daily_cases
		WHERE date = date('{first_date}','-1 day')
		OR date = (
			SELECT max(date)
			FROM daily_cases
			WHERE date <= '{last_date}'
			)		
		GROUP BY date
		)
	)
GROUP BY short_name	
"""


			else: query = f"""
SELECT
	short_name,
	{group_by},
	max(date),
	{case}
FROM (	
	SELECT
		short_name,
		{group_by},
		date,
		{case} - lag({case},1,0) OVER (PARTITION BY short_name ORDER BY date) AS {case}
	FROM (	
		SELECT 
			short_name,
			CAST(strftime('%{interval}',date) AS INT) AS {group_by},
			date,
			{'confirmed - deaths - recovered AS active' if case == 'active' else case}
		FROM daily_cases
		LEFT JOIN countries ON code = country_code
		WHERE code IN (		
			SELECT country_code
			FROM countries 
			WHERE lower(iso2) IN ({country_list})
			OR lower(iso3) IN ({country_list})
			OR lower(short_name) IN ({country_list})
			OR country_code IN ({country_list})
			)
		AND (date = (
			SELECT max(date)
			FROM daily_cases
			WHERE CAST(strftime('%{interval}',date) AS INT) = {first_date} - 1
			)
		OR date = (
			SELECT max(date)
			FROM daily_cases
			WHERE CAST(strftime('%{interval}',date) AS INT) <= {last_date}
			)
		)
		UNION
		SELECT 
			'Global',
			CAST(strftime('%{interval}',date) AS INT) as {group_by},
			date,
			{'sum(confirmed) - sum(deaths) - sum(recovered) AS active' if case == 'active' else f'sum({case})'}
		FROM daily_cases
		WHERE date =  (
			SELECT max(date)
			FROM daily_cases
			WHERE CAST(strftime('%{interval}',date) AS INT) = {first_date} - 1
			)
		OR date = (
			SELECT max(date)
			FROM daily_cases
			WHERE CAST(strftime('%{interval}',date) AS INT) <= {last_date}
			)
		GROUP BY date
	)
)	
GROUP BY short_name	
"""

		
	if debug: print(query) # leave for debug or add --debug switch
	return query

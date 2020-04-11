from os import path
import requests
import csv
import json
import sqlite3
import readline
import datetime
import math
from matplotlib import pyplot as plt
from pprint import pprint

import validate

readline.parse_and_bind('tab: complete')

commands = ['stats','list','graph','quit','exit','update','q','info','pie']

def complete(text, state):
	# generate tab completion list
	if text == '': matches = commands
	else: matches = [x for x in commands if x.startswith(text)]

	# return current completion match
	if state > len(matches): return None
	else: return matches[state]

readline.set_completer(complete)

# Check if csv_headers.json file exists
def load_json():
	if not path.exists('csv_headers.json'):
		db_fields = ['country','region','last_update','confirmed','deaths','recovered']
		csv_headers = {key: [] for key in db_fields}
		with open('csv_headers.json','w') as f:
			json.dump(csv_headers,f,indent=2)
	else:
		with open('csv_headers.json') as f:
			csv_headers = json.load(f)
	return csv_headers



conn = sqlite3.connect('covid19.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS daily_cases ( 
					country TEXT,
					region TEXT,
					csv_file TEXT,
					last_update TEXT,
					confirmed INTEGER NOT NULL DEFAULT 0,
					deaths INTEGER NOT NULL DEFAULT 0,
					recovered INTEGER NOT NULL DEFAULT 0)
					""")


START_DATE = datetime.date(2020,1,22)
TODAY_DATE = datetime.date.today()
print('Dec   2019 - COVID-19 anounced in Wuhan, China.')
print('22.01.2020 - First cases.')
print('11.03.2020 - World Health Organization declares coronavirus COVID-19 as pandemic.')
print(f'{TODAY_DATE.strftime("%d.%m.%Y")} - Today...')

# Update database:
def db_update():
	csv_headers_json = load_json()
	site = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports'
	filelist = [f"{(START_DATE + datetime.timedelta(days=x)).strftime('%m-%d-%Y')}.csv" for x in range(0,(TODAY_DATE-START_DATE).days+1)]

	for file in filelist:
		if not path.exists(file):
			print('Updating database:',round(100/len(filelist)*(filelist.index(file)+1)),'%','\r',end="",flush=True)
			url = f'{site}/{file}'
			csv_file = f"{file.split('.')[0].split('-')[2]}-{file.split('.')[0].split('-')[0]}-{file.split('.')[0].split('-')[1]}"
			response = requests.get(url)
			if response.status_code == 200:
				# if response is ok - download csv file
				with open(file,'wb') as f:
					f.write(response.content)

				# now read the file and parse headers to update database
				with open(file, 'r', encoding='utf-8-sig') as f:
					f_data = csv.DictReader(f)
					csv_headers_current = f_data.fieldnames
					csv_headers_for_db = {}
					current_headers_selector = {i: csv_headers_current[i] for i in range(0, len(csv_headers_current))}
					update_db = True
					update_json = False
					messages = True
					for key,value in csv_headers_json.items():
						if any(i in value for i in csv_headers_current): # True or False if header exists
							header = list(set(value).intersection(csv_headers_current))[0]
							csv_headers_for_db[key] = header
						else:
							if messages:
								print(f'Warning - headers not found.')
								print(f'To avoid database corruption please check csv file {f.name} and select the correct header number or press ctrl+c to abort...')
								print(f'Current headers are: ')
								for x,y in current_headers_selector.items():
									print(f'{x}: {y}')
								messages = False
							header = input(f'Select header for {key}: ')
							while True:
								try:
									new_header = current_headers_selector[int(header)]
									confirm = input(f'New header for {key} will be added as: {new_header}. Are you sure? (y/n): ')
									if confirm == 'y':
										print(f'{new_header} added to {key} headers.')
										csv_headers_json[key].append(new_header)
										csv_headers_for_db[key] = new_header
										update_json = True
										break
									elif confirm == 'n':
										update_db = False
										break
									else:
										continue
								except:
									header = input('Invalid header selection. Try again: ')
							else:
								continue
							if confirm != 'y': break
					else: # else statement will be executed if for loop isn't broken
						if update_json:
							with open('csv_headers.json','w') as f:
								json.dump(csv_headers_json,f,indent=2)
							csv_headers_json = load_json()
							
					if update_db:
						for row in f_data:
							c.execute("INSERT INTO daily_cases VALUES (?,?,?,?,?,?,?)",
								  (row[csv_headers_for_db['country']],
								   row[csv_headers_for_db['region']],
								   csv_file,
								   row[csv_headers_for_db['last_update']],
								   row[csv_headers_for_db['confirmed']],
								   row[csv_headers_for_db['deaths']],
								   row[csv_headers_for_db['recovered']])
								  )
						conn.commit()
					else:
						print('Database can not be updated because csv structure is incompatible.')
						print('You can update manually later using the update command.')
						print('For more information type: help update')


# Some database corrections:
def db_correction():
	c.execute("UPDATE daily_cases SET confirmed = 0 WHERE confirmed = ''")
	c.execute("DELETE FROM daily_cases WHERE confirmed = 0")
	c.execute("UPDATE daily_cases SET deaths = 0 WHERE deaths = ''")
	c.execute("UPDATE daily_cases SET recovered = 0 WHERE recovered = ''")
	c.execute("UPDATE daily_cases SET country = 'China' WHERE country IN ('Mainland China','Macau','Macao SAR','Hong Kong','Hong Kong SAR')")
	c.execute("UPDATE daily_cases SET country = 'Azerbaijan' WHERE country = ' Azerbaijan'")
	c.execute("UPDATE daily_cases SET country = 'Iran' WHERE country = 'Iran (Islamic Republic of)'")
	c.execute("UPDATE daily_cases SET country = 'South Korea' WHERE country IN ('Korea, South','Republic of Korea')")
	c.execute("UPDATE daily_cases SET country = 'Ireland' WHERE country IN ('North Ireland','Republic of Ireland')")
	c.execute("UPDATE daily_cases SET country = 'Vietnam' WHERE country = 'Viet Nam'")
	c.execute("UPDATE daily_cases SET country = 'Czech Republic' WHERE country = 'Czechia'")
	c.execute("UPDATE daily_cases SET country = 'Taiwan' WHERE country = 'Taiwan*'")
	c.execute("UPDATE daily_cases SET country = 'Russia' WHERE country = 'Russian Federation'")
	c.execute("UPDATE daily_cases SET country = 'Moldova' WHERE country = 'Republic of Moldova'")
	c.execute("UPDATE daily_cases SET country = 'UK' WHERE country = 'United Kingdom'")
	c.execute("UPDATE daily_cases SET country = 'Bahamas' WHERE country IN ('Bahamas, The','The Bahamas')")
	c.execute("UPDATE daily_cases SET country = 'Gambia' WHERE country IN ('Gambia, The','The Gambia')")
	c.execute("UPDATE daily_cases SET country = 'Palestine' WHERE country = 'occupied Palestinian territory'")
	conn.commit()

#db_update()
#db_correction()
print()
while True:
	command = False
	while not command:
		command = input('Covid-19 >> ').split()

	if command[0] == 'graph':
		if len(command) == 1:
			req = 'Global'
			c.execute("SELECT csv_file,sum(confirmed),sum(deaths),sum(recovered) FROM daily_cases GROUP BY csv_file ORDER BY csv_file")
		else:
			req = command[1].replace('_',' ')
			c.execute("""SELECT csv_file,sum(confirmed),sum(deaths),sum(recovered) FROM daily_cases
					WHERE country = 
					(SELECT short_name FROM countries WHERE ? IN (lower(short_name),lower(iso2),lower(iso3)))
					GROUP BY csv_file
					ORDER BY csv_file""",(req,))
		data = c.fetchall()
		if len(data) == 0:
			print(f'{req.upper()}: Input not found...')
			continue
		else:
			dates,confirmed,deaths,recovered,active = [], [], [], [], []
		for row in data:
			dates.append(row[0])
			confirmed.append(row[1])
			deaths.append(row[2])
			recovered.append(row[3])
			active.append(row[1] - row[2] - row[3])
		plt.plot(dates,confirmed,label='Confirmed',color='r')
		plt.plot(dates,deaths,label='Deaths',color='k')
		plt.plot(dates,recovered,label='Recovered',color='g')
		plt.plot(dates,active,label='Active',color='y')
		plt.xlabel('Date')
		plt.ylabel('Total cases')
		plt.title(f'COVID-19 {req.upper()} CASES')
		plt.legend()
		plt.show()


	elif command[0] == 'pie':
		if len(command) == 1:
			c.execute("SELECT sum(confirmed),sum(deaths),sum(recovered) FROM daily_cases GROUP BY csv_file ORDER BY csv_file DESC LIMIT 1")
			data = c.fetchall()
			country = 'Global'
			confirmed,deaths,recovered = data[0]
			active = confirmed - deaths - recovered
		else:
			req = command[1].replace('_',' ')
			c.execute("""SELECT country,sum(confirmed),sum(deaths),sum(recovered) FROM daily_cases 
					WHERE country = 
					(SELECT short_name FROM countries WHERE ? IN (lower(short_name),lower(iso2),lower(iso3))) 
					GROUP BY csv_file 
					ORDER BY csv_file DESC 
					LIMIT 1""", (req,))
			data = c.fetchall()
			if len(data) == 0:
				print(f'{req}: Input not found...')
				continue
			else:
				country,confirmed,deaths,recovered = data[0]
				active = confirmed - deaths - recovered
		if confirmed == 0: #Currently its impossible confirmed to be 0
			print(f'No cases confirmed in {country.upper()}.')
			continue
		else:
			cases,labels,legend,colors,pcts = [],[],[],[],[]
			if deaths > 0:
				cases.append(deaths)
				labels.append(f'Deaths ({deaths})')
				colors.append('red')
				pcts.append(100*deaths/confirmed)
				legend.append(f'Deaths {round(pcts[-1],1)}% ({deaths})')
			if recovered > 0:
				cases.append(recovered)
				labels.append(f'Recovered ({recovered})')
				colors.append('green')
				pcts.append(100*recovered/confirmed)
				legend.append(f'Recovered {round(pcts[-1],1)}% ({recovered})')
			if active > 0:
				cases.append(active)
				labels.append(f'Active ({active})')
				colors.append('yellow')
				pcts.append(100*active/confirmed)
				legend.append(f'Active {round(pcts[-1],1)}% ({active})')

			if len([i for i in pcts if i >= 97]) == 1 and len(pcts) == 3:
				plt.pie(cases,colors=colors)
				plt.legend(legend,loc='center left')
			else:
				plt.pie(cases,labels=labels,colors=colors,autopct='%1.1f%%',pctdistance=0.85)
			plt.title(f'{country.upper()}: Confirmed cases: {confirmed}.')
			plt.tight_layout()
			plt.show()


	elif command[0] == 'stats':
		if len(command) == 1:
			country = 'Global'
			c.execute("SELECT sum(confirmed),sum(deaths),sum(recovered) FROM daily_cases GROUP BY csv_file ORDER BY csv_file DESC LIMIT 2")
		else:
			country = command[1]
			c.execute("SELECT sum(confirmed),sum(deaths),sum(recovered) FROM daily_cases WHERE country=? GROUP BY csv_file ORDER BY csv_file DESC LIMIT 2", (country.capitalize(),))
		data = c.fetchall()
		if len(data) == 0:
			print(f'{country.upper()}: Input not found...')
			continue
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


	elif command[0] == 'bar':
		""" Usage: bar [country] [case] [grouping] [period] """
		try:
			country,case,grouping,period = validate.commandline(command) 
		except ValueError as error:
			print(str(error))
			continue
		try:
			db_group,reference,first_date,last_date = validate.period(grouping,period)
		except ValueError as error:
			print(str(error))
			continue
		print(db_group,first_date,last_date)
		#continue
		
		query = validate.dbquery(command[0],country=country,case=case,grouping=grouping,db_group=db_group,first_date=first_date,last_date=last_date)
		c.execute(query)
#		print(query)
#		continue
#		c.execute(f"""
#				SELECT max(csv_file),mnt,week,{case},{case}-lag({case},1,0) OVER (ORDER BY {db_group}) as diff FROM (
#					SELECT csv_file,strftime('%m',csv_file) AS mnt,strftime('%W',csv_file) AS week, sum({case}) AS {case} FROM daily_cases
#					WHERE country =  
#						(SELECT short_name FROM countries WHERE ? IN (lower(short_name),lower(iso2),lower(iso3))) 
#					AND {db_group} BETWEEN ? AND ?
#					GROUP BY csv_file)
#				GROUP BY {db_group}
#			""",(country,first_date,last_date))
		data = c.fetchall()
		pprint(data)
		print(query)
		#continue
		if len(data) == 0:
			print(f'{country.upper()}: Input not found...')
			continue
		#print(data)
		# next check is if the week we asked is referenced by the week before it
		# and if this is the case then first row is only for reference so we delete it
		# !!! refactor later !!!
		if (db_group == 'week' and reference and int(data[0][1]) < int(first_date) + 1) or \
                   (db_group == 'mnt' and reference and int(data[0][1]) < int(first_date) + 1) or \
                   (db_group == 'csv_file' and reference and data[0][1] < (datetime.date.fromisoformat(first_date) + datetime.timedelta(days=1)).isoformat()):
			del data[0]
		pprint(data)
		#continue
		db_dummy, db_dates, db_cases, db_diff = list(zip(*data))
		
		if grouping in ('m','monthly'): graph_dates = [f"M{int(i)}" for i in db_dates]
		elif grouping in ('w','weekly'): graph_dates = [f"W{int(i)}" for i in db_dates]
		else: graph_dates = [f"{i.split('-')[2]}.{i.split('-')[1]}" for i in db_dates]

		#for i in range(0,len(data)):
		#	print(db_dates[i],db_months[i],db_weeks[i],db_cases[i],'\t',dates[i],months[i],weeks[i],cases[i-1])
		#continue
		#print(dates)
		#print(cases)
		plt.bar(graph_dates,db_diff)
		plt.title(country)
		plt.show()

	elif command[0] == 'update':
		db_update()
		print()
		db_correction()


	elif command[0] == 'list':
		command.append('') # this will add empty second parameter which will cause printing of all results if not specified
		c.execute("SELECT iso2,iso3,short_name FROM countries WHERE short_name LIKE ? ORDER BY short_name",(f'%{command[1]}%',))
		data = c.fetchall()
		if not data: 
			print(f'{command[1]}: Results not found...')
			continue
		if command[1]: 
			print(f'Search for: {command[1]}')
			print(30*'=')
		print('ISO2\tISO3\tNames')
		print(30*'=')
		for row in data:
			print(f'{row[0]}\t{row[1]}\t{row[2]}')
		print(30*'=')
		print(f'{len(data)} results found.')


	elif command[0] == 'info':
		try:
			c.execute("SELECT * FROM daily_cases WHERE country=? ORDER BY csv_file", (command[1].capitalize(),))
			pprint(c.fetchall())
		except:
			print('Info error: country not specified.')
			


	elif command[0] in ('q','quit','exit'):
		break


	else: 
		print('Unknown command')

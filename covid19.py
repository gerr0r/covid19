import readline
import datetime
import math
from matplotlib import pyplot as plt
from pprint import pprint
import os, sys

import validate

readline.parse_and_bind('tab: complete')

commands = ['stats','list','graph','quit','exit','update','q','info','help']

def complete(text, state):
	# generate tab completion list
	if text == '': matches = commands
	else: matches = [x for x in commands if x.startswith(text)]

	# return current completion match
	if state > len(matches): return None
	else: return matches[state]

readline.set_completer(complete)
readline.read_history_file('histfile')

#os.system('clear')

def motd():
	print('December 2019 - COVID-19 anounced in Wuhan, China.')
	print('   22.01.2020 - First cases.')
	print('   11.03.2020 - World Health Organization declares coronavirus COVID-19 as pandemic.')
	print(f'   {datetime.date.today().strftime("%d.%m.%Y")} - Today.')
	print()

validate.init_db()
#print(sys.argv)
try:
	last_command = sys.argv[1]
except:
	last_command = False
	motd()

while True:
	command = False
	while not command:
		#command = input('Covid-19 >> ')
		if not last_command:
			command = input('Covid-19 >> ')
		else:	
			command = last_command
			print(f"Covid-19 >> {last_command}")
			last_command = False
		readline.write_history_file('histfile')
		try:
			validate.commandline(command)
		except ValueError as error:
			print(str(error))

while True:

	if command[0] == 'stats':
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


	elif command[0] == 'info':
		try:
			c.execute("SELECT * FROM daily_cases WHERE country=? ORDER BY csv_file", (command[1].capitalize(),))
			pprint(c.fetchall())
		except:
			print('Info error: country not specified.')


	elif command[0] == 'help':
		command.append('')
		if not command[1]:
			print("")
			print("Quick list of available commands.")
			print("For more info type help [command].")
			print("")
			print("Commands:")
			print("")
			print("  help    Displays this quick help information or help on specified available command.")
			print("  graph   Displays current status on specified country.")
			print("  update  Updates database.")
			print("  bar     Displays specified cases on a daily, weekly or monthly period for the given country.")
			print("")
		elif command[1] == 'bar':
			print("")
			print("BAR:     Displays specified cases on a daily, weekly or monthly period for the given country.")
			print("")
			print("Usage:   bar [country] [case] [grouping] [period]")
			print("Default: bar global confirmed daily 1.1:31.12")
			print("")
			print("Options:")
			print("  [country]   country name, iso2, iso3 or code of the country")
			print("  [case]      confirmed, deaths or recovered. 'c', 'd' or 'r' as shortcuts")
			print("  [grouping]  daily, weekly or monthly stats. 'd', 'w' or 'm' as shortcuts")
			print("  [period]    format is from_date:to_date")
			print("")
			print("Period format:")
			print("  [day.month:day.month] if daily grouping (ex. 30.3:4.4 means 30th March to 4th April inclusive)")
			print("  [week:week]           if weekly grouping (ex. 12:15 means ISO week 12 to week 15 inclusive)")
			print("  [month:month]         if monthly grouping (ex. 2:5 means months February to May inclusive)")
			print("  If period is ommited it is replaced with full period for the year (daily - 1.1:31.12, weekly - 0:53, monthly 1:12)")
			print("  If one side in period is ommited it is replaced with begining or the end of the year:")
			print("  - [from_date:] from given day (week, month) to the end of the year")
			print("  - [:to_date]   from begining of the year to given day (week, month)")
			print("")
			print("Examples:")
			print("  bar italy recovered weekly 9:14 --- Weekly recovered cases in Italy between weeks 9 to 14")
			print("  bar global c m :5               --- Monthly confirmed cases worldwide from begining of the year to May")
			print("  bar china c daily 1.3:15.3      --- Daily confirmed cases in China from 1st to 15th March")
			print("")
			



import readline
import datetime
import math
from matplotlib import pyplot as plt
from pprint import pprint
import os, sys

import validate
import dbquery

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

os.system('clear')

dbquery.dbinit()
last_update = dbquery.dbrequest('last_update')
last_update = datetime.datetime.strptime(last_update[0][0],'%Y-%m-%d').strftime('%d.%m.%Y') if last_update else 'N/A'.rjust(10)
current_date = datetime.date.today().strftime('%d.%m.%Y')

def header_msg():
	print('December 2019 - COVID-19 anounced in Wuhan, China.')
	print('   22.01.2020 - First reported cases.')
	print('   11.03.2020 - World Health Organization declares coronavirus COVID-19 as pandemic.')
	print()
	print(f"   {last_update} - Last update.")
	print(f"   {current_date} - Current date.")
	print()
	print('Type <help> for a quick list of available commands.')


#print(sys.argv)
try:
	last_command = sys.argv[1]
except:
	last_command = False
	header_msg()

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

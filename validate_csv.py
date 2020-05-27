from os import path
import csv, json, time, datetime

def load_json():
	""" Create or load JSON file to get csv headers from downloaded files. """

	if not path.exists('csv_headers.json'):
		fieldnames = ['country','region','confirmed','deaths','recovered']
		csv_headers = {key: [] for key in fieldnames}
		with open('csv_headers.json','w') as f:
			json.dump(csv_headers,f,indent=2)
	else:
		with open('csv_headers.json') as f:
			csv_headers = json.load(f)
	return csv_headers


def select_csv_headers(file,csv_headers_current):
	""" Compare current headers with existing ones in JSON file. Update JSON file. """

	csv_headers_json = load_json()
	csv_headers_to_read = {}
	current_headers_selector = {i+1: csv_headers_current[i] for i in range(0, len(csv_headers_current))}
	#update_db = True
	update_json = False
	notice = True

	while True:
		for key,value in csv_headers_json.items():
			if any(i in value for i in csv_headers_current): # True or False if header exists
				header = list(set(value).intersection(csv_headers_current))[0]
				csv_headers_to_read[key] = header
			else:
				if notice:
					print()
					print(f'*** Warning - headers not found.')
					print(f'*** Select correct headers to avoid wrong data in database.')
					print(f'*** If unsure check data in {file} file.')
					print()
					print(f'File headers: ')
					for x,y in current_headers_selector.items():
						print(f'{x}: {y}')
					print()
					notice = False
				msg = f'Set {key.upper()} : '
				while True:
					header = input(msg)
					try:
						new_header = current_headers_selector[int(header)]
						csv_headers_to_read[key] = new_header
						csv_headers_json[key].append(new_header)
						update_json = True
						break
					except:
						msg = f'*** {key.upper()} : '
		else:
			if update_json:
				confirm = input(f'*** Confirm? (Y/n): ').lower() or 'y'
				if confirm in ('y','yes'):
					with open('csv_headers.json','w') as f:
						json.dump(csv_headers_json,f,indent=2)
					break
				elif confirm in ('n','no'):
					csv_headers_json = load_json()
				else:
					print('*** Invalid input...')
					continue
			else:
				break

	return csv_headers_to_read



def csv_optimize(file):

	with open('countries_v2.json') as f:
		countries = json.load(f)

	with open(file,'r',encoding='utf-8-sig') as f:
		csv_data = csv.DictReader(f)
		headers = select_csv_headers(file,csv_data.fieldnames)
		#print(f"CODE CONFIRMED DEATHS RECOVERED {'COUNTRY'.ljust(32)} REGION")
		totals = {}
		table = ''
		for row in csv_data:
			if not row[headers['confirmed']] or row[headers['confirmed']] == '0': 
				continue # ignore data with zero confirmed cases
			else:
				if not row[headers['deaths']]: row[headers['deaths']] = '0'
				if not row[headers['recovered']]: row[headers['recovered']] = '0'
				
				row['code'] = get_code(row[headers['country']],row[headers['region']],countries)

			#table += f"{row['code'].rjust(4)} {row[headers['confirmed']].rjust(9)} {row[headers['deaths']].rjust(6)} {row[headers['recovered']].rjust(9)} {row[headers['country']].ljust(32)} {row[headers['region']]}\n"
			if row['code'] in totals:
				totals[row['code']]['confirmed'] += int(row[headers['confirmed']])
				totals[row['code']]['deaths'] += int(row[headers['deaths']])
				totals[row['code']]['recovered'] += int(row[headers['recovered']])
			else:
				totals[row['code']] = {'confirmed':int(row[headers['confirmed']]),'deaths':int(row[headers['deaths']]),'recovered':int(row[headers['recovered']])}
		#print(table)
	with open('countries_v2.json','w') as f:
		json.dump(countries,f,indent=2)

	return(totals)
		


def get_code(country,region,countries):

	# some preliminary normalization
	country = country.lower().strip()
	region = region.lower().strip()

	if country == 'others':	country = region if region else 'unknown' # hacky... figure it out!
	if region == 'none' or region == country: region = ''

	for country_code,country_data in countries.items():
		if country in country_data['names']:
			code = country_code
			break
	else:
		print(f'*** Country {country.upper()} not found. Enter ISO3166-1 code. For info type <help|?>.')
		code = check_country(country,countries)

	if region and region not in countries[code]['places']:
		code = check_region(country,region,countries,code)

	return(code)




def check_country(country,countries):

	while True:
		search_code = input(f'Code [{country.title()}]: ').lower().split()
		search_code.append('')
		if search_code[0] in countries.keys():
			code = search_code[0]
			countries[code]['names'].append(country)
			break
		elif search_code[0] == 'new':
			next_code = max(max([int(i) for i in countries.keys()]),1000)+1
			confirm = input(f"{country.upper()} will be created with code {next_code}. Proceed? (Y/n): ").lower() or 'y'
			if confirm in ('y','yes'):
				code = str(next_code)
				countries[code] = {'names':[country],'places':[country],'territories':[]}
				break
			else:
				print("*** Canceled.")
		elif search_code[0] in ('?','help'):
			print_help()
		elif search_code[0] in ('s','search'):
			print_search(countries,search_code[1])
		elif not search_code[0]:
			pass
		else:
			print(f'*** Code {search_code[0]} not found. For info type <help|?>.')

	return(code)



def check_region(country,region,countries,code):

	if region not in countries[code]['territories']:
		while True: # outer loop
			confirm = input(f'*** Add {region.upper()} to {country.upper()} regions? (type <n|no> if unsure or to set ISO3166-1 code) (Y/n): ').lower() or 'y'
			if confirm in ('y','yes'):
				countries[code]['places'].append(region)
				break
			elif confirm in ('n','no'):
				print(f'*** Enter ISO3166-1 code. For info type <help|?>.')
				while True: # inner loop
					search_code = input(f'Code [{country.title()}, {region.title()}]: ').lower().split()
					search_code.append('')
					if search_code[0] in countries.keys():
						if region not in countries[search_code[0]]['names']:
							countries[search_code[0]]['names'].append(region)
						countries[code]['territories'].append(region)
						code = search_code[0] # for the region check
						break
					elif search_code[0] == 'new':
						next_code = max(max([int(i) for i in countries.keys()]),1000)+1
						confirm = input(f"{region.upper()} will be created with code {next_code}. Proceed? (Y/n): ").lower() or 'y'
						if confirm in ('y','yes'):
							countries[code]['territories'].append(region)
							code = str(next_code)
							countries[code] = {'names':[region],'places':[region],'territories':[]}
							break
						else:
							print("*** Canceled...")
					elif search_code[0] in ('?','help'):
						print_help()
					elif search_code[0] in ('s','search'):
						print_search(countries,search_code[1])
					elif search_code[0] == 'skip':
						countries[code]['places'].append(region)
						break
					elif not search_code[0]:
						pass
					else:
						print(f'*** Code {search_code[0]} not found. For info type <help|?>.')
				break # this will break outer loop if inner loop broken

			else:
				print('*** Invalid input...')
	else: # if region is in country territories
		for country_code,country_data in countries.items():
			if region in country_data['names']:
				code = country_code
				break

	return(code)


def print_help():

	print('*** To view list of codes type <s|search [search_text]>.')
	print('*** To list all codes type <s|search> without search text.')
	print('*** To create new country type <new> and press enter.')
	


def print_search(countries,search_text,count=0):

	for country_code,country_data in countries.items():
		for country_name in country_data['names']:
			if search_text in country_name:
				count += 1
				if count == 1: print(f'\nCode\tNames\n----\t-----')
				country_names_list = ', '.join(map(lambda name: name.title(),country_data['names']))
				print(f"{country_code}\t{country_names_list}")
				break
	print(f'----\n{count} results found.\n') if count > 0 else print('*** 0 results found.')


def debug_function():

	START_DATE = datetime.date(2020,1,22)
	END_DATE = datetime.date(2020,4,26)
	filelist = [f"{(START_DATE + datetime.timedelta(days=x)).strftime('%m-%d-%Y')}.csv" for x in range(0,(END_DATE-START_DATE).days+1)]

	for file in filelist:
		data = csv_optimize(f'csv_files/{file}')

		print(f'\nBEGIN: {file}\n')
		print("Totals:\n")

		for k,v in data.items():
			print(f"{str(k).rjust(4)} {str(v['confirmed']).rjust(9)} {str(v['deaths']).rjust(6)} {str(v['recovered']).rjust(9)}")
		print(f'\nEND: {file}\n')


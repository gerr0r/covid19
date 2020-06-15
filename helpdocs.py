#Help function
def help(arg):

	if not arg: print("""
Quick list of available commands.
For more info type help [command].

Commands:

  help    Show this help information.
  graph   Show statistics in graphic format.
  stats   Show statistics in text format.
  update  Updates database.
  list    Show list of countries.
  quit    Quits program.
""")

	elif arg == 'graph': print("""
GRAPH:   Draw graphics based on specified parameters.

Usage:   graph --type <graphics_type> --country <country/countries> --cases <cases> --period <period>
Default: graph --type plot --country global --cases confirmed --period :

Options:
  --type      plot, bar or pie
  --country   country name|iso2|iso3|code of the country or comma separated country list
  --cases     all or confirmed, deaths, recovered or active (latter only for plot graphs)
  --period    format is [d|w|m][from_date:to_date]

Graph type:
  plot  -  Shows linear function of TOTAL cases over time.
           Without country specified (or global set as country) draws global cases.
           With single country all cases can be drawn in one graph.
           With list of countries only one case can be drawn at same time.
           Period can be defined for specific start and end date/week/month.
           Active cases can be drawn also.
  bar   -  Shows bars with CALCULATED cases based on period given.
           With single country draw bars broken down to pieces of a daily, weekly or monthly cases for given period.
           With list of countries draw horizontal bars with calculated amount of cases for given period.
           Active cases can NOT be drawn.
  pie   -  Shows pie chart with PROPORTIONAL data based on last date given.
           With single country draws pie chart of deaths, recovered and active cases as part of total confirmed cases (in percents).
           With list of countries draws pie chart with given case as part of global cases. One case at a time.
           Period can be specified but only last date is processed. Start date is considered the begining and is ignored.
           Active cases can NOT be drawn.

Country selection:
  one   -  Default is 'global'. Specified by name, iso2, iso3 or code.
  many  -  Comma separated list of countries. Specified by name, iso2, iso3 or code. Can be mixed.
           Type <list> to show list of countries.

Period:
           If period is ommited it is replaced with full period for the year (daily - d1.1:31.12, weekly - w0:53, monthly m1:12)
           If one side in period is ommited it is replaced with begining or the end of the year:
           - [from_date:] from given day (week, month) to the end of the year
           - [:to_date]   from begining of the year to given day (week, month)
           - [:] from begining to the end of the year

Period format:
  date  -  d[first_day.month:last_day.month]
           since date is default d-prefix can be omitted
              ex. d30.3:4.4 (or 30.4:4.4 without the d-prefix) means 30th March to 4th April inclusive
  week  -  w[first_week:last_week]
              ex. w12:15 means ISO week 12 to week 15 inclusive
  month -  m[first_month:last_month]
              ex. m2:5 means months February to May inclusive

Synonyms:
           d == d: == d1.1: == d:31.12 == d1.1:31.12 == : == 1.1: == :31.12 == 1.1:31.12
           w == w: == w0: == w:53 == w0:53
           m == m: == m1: == m:12 == w1:12
Examples:
           Weekly recovered cases in Italy between weeks 9 to 14
           #   graph --type bar --country italy --cases recovered --period w9:14
           Monthly confirmed cases worldwide from begining of the year to May
           #   graph --type bar --period m:5
           Daily confirmed cases in China from 1st to 15th March
           #   graph --type bar --country cn --period 1.3:15.3
""")

	elif arg == 'stats': print("""
TODO
""")

	elif arg == 'list': print("""
TODO
""")

	elif arg == 'update': print("""
TODO
""")

	else: raise ValueError(f"*** {arg}: No help available.")

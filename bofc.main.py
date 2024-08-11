import argparse
from countriescurrency import is_country_found
from bofcapp import get_rates
from bofcapp import check_date_rules
from bofcapp import check_country_rules
from bofcapp import GetRatesFromBofC
from datemethods import DateRange
import datetime




    
    

parser = argparse.ArgumentParser(description='Country\'s exchange rate with Cdn$ over a date range - using Bank of Canada API ')

parser.add_argument('--startdate', dest='startdate', 
                    required=True, type=str,
                    help='YYYY-MM-DD')
parser.add_argument('--enddate', dest='enddate', 
                    required=True, type=str,
                    help='YYYY-MM-DD')
parser.add_argument('--country', dest='country', 
                    required=True, type=str,
                    help='country\'s currency')
parser.add_argument('--username', dest='username', 
                    required=True, type=str, 
                    help='username')


args = parser.parse_args()

enddate, startdate = [args.enddate, args.startdate]
country = args.country
user = args.username





print ("bank of canada api")

if not is_country_found(country):
    print("Country", country, "not found.")
    exit(0)
 
if not check_country_rules(user, country):
    string = "After applying the country access rules for " + user + ". No matching countries were found that were allowed."
    print(string)
    exit(0)

daterange = DateRange(startdate, enddate)

daterange_list = check_date_rules([], user, daterange)

if (not daterange_list):
    string = "After applying the date access rules for " + user + ". No matching date ranges were found that were allowed."
    print(string)
    exit(0)

rate_dict = GetRatesFromBofC([country], daterange_list)
if (not rate_dict):
    print("No values returned from Bank of Canada site")
    exit(0)

exit(0)
     
if(0):     
    last_rate_dict = GetRatesFromBofC(new_country_list, new_dates_list)

    if (not pruned_country_list):
        string = "After applying the country access rules for " + user + ". No matching countries were found that were allowed."
        infolog(string)
    #    return (False, pruned_country_list, newdaterange_list)
    string = "After applying country access rules for " + user + ". The allowed list is" + str(pruned_country_list)
    infolog(string)

    for daterange in daterange_list:
        newdaterange_list = check_date_rules(newdaterange_list, user, daterange)

    if (not newdaterange_list):
     
        last_rate_dict = GetRatesFromBofC(new_country_list, new_dates_list)

    if (last_rate_dict):
     
     exit(0)

if (check_country_rules(username, country) == False):
    print("No permission to view this Geo")

 
country_code = get_country_code(country)
if (country_code != "" ):
    start = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    end = datetime.datetime.strptime(enddate, "%Y-%m-%d")

    ratedict = get_rates( start, end, country_code )

    filtereddict = check_date_rules(ratedict, username, startdate, enddate)

    #print(ratedict)
    print(filtereddict)


    last_rate_dict = GetRatesFromBofC(new_country_list, new_dates_list)

    if (last_rate_dict):
        pass
        #TODO - ask another question about the data
        AnalyzeRateInfo(last_rate_dict)


exit(0)

query = {'start_date' : '2016-01-01', 'end_date' : '2016-02-02'}

#urlstring = "https://www.bankofcanada.ca/valet/observations/IEXE1901/json/?{start_date=2016-01-01&end_date=2016-02-02}"
urlstring = "https://www.bankofcanada.ca/valet/observations/IEXE1901/json"

response = requests.get(urlstring, params=query )

print(response)

print(response.json())

jsonobject = response.json()
# fred = json.loads(jsonobject)

next1 = jsonobject['seriesDetail']
print(next1)

iterate_nested_json_recursive(jsonobject)




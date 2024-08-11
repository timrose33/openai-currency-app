import requests
import urllib
import json
import datetime
from datetime import date
from datemethods import DateRange
from countriescurrency import is_country_found
from countriescurrency import get_currency_code
from countriescurrency import get_currency_name



class AccessRule:
  def __init__(self,user):
    self.user = user

class DateRangeAccessRule(AccessRule):
      def __init__(self,user, start, end):
          super().__init__(user)
          if (start == "all" and end == "all"):
              self.daterange = DateRange(date(datetime.MINYEAR, 1, 1), date(datetime.MAXYEAR, 12, 31))
          else:
              self.daterange = DateRange(start, end)

class CountryAccessRule(AccessRule):
      def __init__(self,user, geo):
          super().__init__(user)
          self.geo = geo



inclusionrules = []   
exclusionrules = []
users = ["bob", "alice", "joe", "priya", "tom", "roberta"]


inclusionrules.append(CountryAccessRule( "alice", "all"))
inclusionrules.append(DateRangeAccessRule( "alice", "all", "all"))
exclusionrules.append(CountryAccessRule( "alice", "Australia"))
exclusionrules.append(CountryAccessRule( "alice", "Fiji"))
exclusionrules.append(DateRangeAccessRule( "alice", "2015-01-01", "2016-01-01"))

inclusionrules.append(CountryAccessRule( "bob", "United States"))
inclusionrules.append(CountryAccessRule( "bob", "Mexico"))
inclusionrules.append(CountryAccessRule( "bob", "Jamaica"))
inclusionrules.append(DateRangeAccessRule( "bob", "2013-03-01", "2013-03-31"))

exclusionrules.append(CountryAccessRule( "roberta", "Mexico"))
exclusionrules.append(CountryAccessRule( "roberta", "Canada"))
inclusionrules.append(CountryAccessRule( "roberta", "all"))
inclusionrules.append(DateRangeAccessRule( "roberta", "2013-03-01", "2013-03-31"))

inclusionrules.append(CountryAccessRule( "priya", "Germany"))
inclusionrules.append(CountryAccessRule( "priya", "Poland"))
inclusionrules.append(DateRangeAccessRule( "priya", "2014-08-12", "2015-01-15"))
inclusionrules.append(DateRangeAccessRule( "priya", "2016-05-01", "2016-10-31"))

inclusionrules.append(CountryAccessRule( "joe", "Germany"))
inclusionrules.append(CountryAccessRule( "joe", "Slovakia"))
inclusionrules.append(CountryAccessRule( "joe", "Poland"))
inclusionrules.append(CountryAccessRule( "joe", "Romania"))
inclusionrules.append(DateRangeAccessRule( "joe", "2014-01-01", "2016-12-31"))
exclusionrules.append(DateRangeAccessRule( "joe", "2014-08-01", "2014-08-31"))





def infolog(str):
    print("        INFO:", str)

def is_user_valid(user):
    return user in users

def traverse_array(json_arr):
    print("... ARRAY")
    for item in json_arr:
        print("***", item, "  ", type(item))
        if isinstance(item, list):
            traverse_array(item)
        else:
            iterate_nested_json_recursive(item)
        

def iterate_nested_json_recursive(json_obj):
    for key, value in json_obj.items():
        if isinstance(value, dict):
            iterate_nested_json_recursive(value)
        elif isinstance(value, list):
            traverse_array(value)
        else:
           print(f"{key}: {value}")

def get_bofc_country_value(country):
    result = None
    urlstring = "https://www.bankofcanada.ca/valet/lists/series/json"
    response = requests.get(urlstring)
    if (response.status_code != 200):
       print ("Error accessing Bank of Canada site. Http code=", response, "url", urlstring)
       exit(1)

    json_obj = response.json()
    country_code = get_currency_code(country)
    if (country_code != None):
        noon_country_code = country_code +"_NOON"
    for key, value in json_obj.items():
        if (key == "series"):
            for key1, value1 in value.items():
                if ((value1["label"].find("NOON") != -1) and
                    (value1["description"].find(country) != -1)):
                    result = key1
                    break
                elif (country_code and value1["label"].find(noon_country_code) != -1): 
                    result = key1
                    break
                
    return result         

def get_rates ( start, end, country_code):
    
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')

    query = {'start_date' : start_str, 'end_date' : end_str}
    mydict = {}

    urlstring = "https://www.bankofcanada.ca/valet/observations/"+ country_code + "/json"

    response = requests.get(urlstring, params=query)
    if (response.status_code != 200):
       print ("Error accessing Bank of Canada site. Http code=", response, "url", urlstring, str(query))
       exit(1)
    json_obj = response.json()
    series_obj = json_obj["observations"]
    for value in series_obj:
        date_element = ""
        rate_element = 0
        for key1, value1 in value.items():
            #print(key1, value1)
            if (key1 == "d"): 
               date_element = value1
            elif (key1 == country_code):
               rate_element = value1["v"]
               mydict.update({date_element: rate_element})
    return(mydict)        




def check_country_rules(username, country):
    result = False
    for accessrule in exclusionrules:
        if not isinstance(accessrule, CountryAccessRule): continue
        if ( accessrule.user == username):
            if (accessrule.geo == "none"):
                # no restrictions for this rule
                pass
            elif (accessrule.geo == country):
                result = False
                return (result)
            
    for  accessrule in inclusionrules:
        if not isinstance(accessrule, CountryAccessRule): 
            continue
        if ( accessrule.user == username):
            if (accessrule.geo == "all"):
                # no restrictions for this rule
                result = True
                break
            elif (accessrule.geo == country):
                result = True
                break    
    return(result) 


def check_date_rules(listOfRanges, username, rangeToMatch):

       # build up list of inclusion ranges that match
       for  accessrule in inclusionrules:
            if not isinstance(accessrule, DateRangeAccessRule): continue
            if ( accessrule.user == username):
                if (accessrule.daterange.overlaps(rangeToMatch)):
                   intersect = accessrule.daterange.intersection(rangeToMatch)
                   if listOfRanges == []: #empty
                       listOfRanges.append(intersect)
                       continue
                   newListOfRanges = listOfRanges
                   for i, value1 in enumerate(listOfRanges):
                       # if overlaps existing range, expand it by merging
                       if (value1.overlaps(intersect)):
                           intersect1 = value1.intersection(intersect)
                           newvalue = value1.merge(intersect1)
                           newListOfRanges[i] = newvalue
                       # else no overlap, add new range to list
                       else:
                           newListOfRanges.append(intersect)
                   listOfRanges = newListOfRanges 
       if (not listOfRanges):                # empty, no matches - no point to check exclusions
           return listOfRanges 
       
       for accessrule in exclusionrules:
            if not isinstance(accessrule, DateRangeAccessRule): continue
            if ( accessrule.user == username):
                if (accessrule.daterange.overlaps(rangeToMatch)):
                   intersect = accessrule.daterange.intersection(rangeToMatch)
                   newListOfRanges = listOfRanges
                   for i, value1 in enumerate(listOfRanges):
                       # if overlaps existing range, reduce it by the exclusion amount
                       if (value1.overlaps(intersect)):
                           newvalues = value1.subtract(intersect)
                           del newListOfRanges[i]
                           newListOfRanges.extend(newvalues)
                   listOfRanges = newListOfRanges 
                
       return listOfRanges
    

def create_date_ranges_from_dict(data):
    date_ranges = []

    
    if 'dates' in data:
        for date_dict in data['dates']:
            if 'start_date' in date_dict and 'end_date' in date_dict:
                try:
                    date_range = DateRange(date_dict['start_date'], date_dict['end_date'])
                    date_ranges.append(date_range)
                except ValueError as e:
                    print(f"Error creating DateRange: {e}")
    else:
        if 'start_date' in data and 'end_date' in data:
            try:
                date_range = DateRange(data['start_date'], data['end_date'])
                date_ranges.append(date_range)
            except ValueError as e:
                print(f"Error creating DateRange: {e}")

    return date_ranges    
                          
def ApplyAccessRulesFilters (user, country_dict, date_dict):
    countries_list = country_dict.get('countries')
    if not countries_list:
        infolog("Error parsing country list")
    daterange_list = create_date_ranges_from_dict(date_dict)

    pruned_country_list = []
    newdaterange_list = []
 

    # Make sure the countries ChatGPT found are real countries
    for country in countries_list:
        if is_country_found(country):
            if check_country_rules(user, country):
              pruned_country_list.append(country)

    if (not pruned_country_list):
        string = "After applying the country access rules for " + user + ". No matching countries were found that were allowed."
        infolog(string)
        return (False, pruned_country_list, newdaterange_list)
    string = "After applying country access rules for " + user + ". The allowed list is" + str(pruned_country_list)
    infolog(string)

    for daterange in daterange_list:
        newdaterange_list = check_date_rules(newdaterange_list, user, daterange)

    if (not newdaterange_list):
        string  = "After applying the date range access rules for " + user + ". No matching ranges were found that were allowed."
        infolog(string)
        return (False, pruned_country_list, newdaterange_list)
    
    list_str = ""
    for value in newdaterange_list:
        list_str += " "
        list_str += str(value)
    string = "After applying date-based access rules for " + user + ". The allowable date ranges are:" + list_str
    infolog(string)

    return (True, pruned_country_list, newdaterange_list)

def GetRatesFromBofC(country_list, daterange_list):
    for country in country_list:
        ratedict = {}
        for daterange in daterange_list:
             bofc_country_value = get_bofc_country_value(country)
             if (bofc_country_value != None):
                oneratedict = get_rates( daterange.start_date, daterange.end_date, bofc_country_value )
                ratedict.update(oneratedict)
             else:
                name = get_currency_name(country)
                code = get_currency_code(country)
                if (name != None and code != None):
                    mystr = country + " currency is " + name + "(" + code + "). However, the Bank of Canada application does not support it."
                    infolog(mystr)
                else:
                    mystr = "No currency code found for " + country
                    infolog(mystr)
        if ratedict:
           print("Rates from the Bank Of Canada application for", country, ":", ratedict)
    return ratedict
    

         



        
    

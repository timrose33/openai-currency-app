from openai import OpenAI
import sys
import json
import re
import getpass
from bofcapp import is_user_valid
from bofcapp import ApplyAccessRulesFilters
from bofcapp import GetRatesFromBofC
from bofcapp import infolog


# global
client = None 
user = ""


# Had to craft this question to answer Yes in both cases by trying in Chat.
# The answer was actually different vs. in the program
def isCountry(str):
   teststring = "Answer Yes if " + str + " is a country."
   result = YesOrNoQuestion(teststring)
   return(result)

def isCollectionOfCountries(str):
   teststring = "Answer Yes if " + str + " is a collection of countries."
   result = YesOrNoQuestion(teststring)
   return(result)
 
def YesOrNoQuestion(teststring):
        result = False

        stream = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[{"role": "user", "content": teststring}],
          stream=True,
       )
        
        for chunk in stream:
          for choice in chunk.choices:
             if (choice.delta.content == "Yes"): 
                result = True
                break
             elif (choice.delta.content == "No"):
                break 
          if (result == True): break        
 
        return(result)


def  ListOfCountries(str):
   teststring = "What countries are represented in the following string: '" + str + "'. Return result as a JSON object with a key called 'countries'."
   result = ListOfItems(teststring)
   return result

def  ListOfDateRanges(str):
   teststring = "What date ranges occur in the following string: '" + str + "'. Format dates in ISO format. Return result as a JSON object with start dates and end dates. End date should not be None"
   result = ListOfItems(teststring, True)
   return result



# Partly written by ChatGPT though with manual help to get
# it right.
# Extracts the first JSON object it finds in a string
def extract_first_json_object(input_string):
   stack = []
   start = -1

   for i, char in enumerate(input_string):
        if char == '{':
            if not stack:
                start = i
            stack.append(char)
        elif char == '}':
            if stack:
                stack.pop()
                if not stack:
                    substr = input_string[start:i+1]
                    try:
                      # Attempt to parse the JSON string to ensure it is valid
                      json_obj = json.loads(substr)
                      return json_obj
                    except json.JSONDecodeError:
                      continue
   
   return None

def NormalizeJson(mystring):
    modified_string = mystring.replace("start:", "start_date:")
    modified_string = modified_string.replace("end:", "end_date:")
    modified_string = modified_string.replace("endDate:", "end_date:")
    modified_string = modified_string.replace("startDate:", "start_date:")

    modified_string = modified_string.replace("date_ranges:", "dates:")
    modified_string = modified_string.replace("dateRanges:", "dates:")
    modified_string = modified_string.replace("date:", "dates:")
 
 
 
    return modified_string


def ListOfItems(teststring, normalize=False):
      stream = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[{"role": "user", "content": teststring}],
          stream=True,
       )

      mystr = ""     
      for chunk in stream:
         for choice in chunk.choices:
              # TODO - make more efficient if needed
              mystr += str(choice.delta.content).strip()
      if (normalize):
          mystr = NormalizeJson(mystr)
      json_object = extract_first_json_object(mystr)
      return json_object
 

def RunTests():
# Test Code
   print(isCountry( "Fred"))
   print(isCountry( "Georgia"))
   print(isCountry( "Canterbury"))
   print(isCountry( "Europe"))
   print(isCountry( "Commonwealth"))

   print(isCollectionOfCountries( "Fred"))
   print(isCollectionOfCountries( "Georgia"))
   print(isCollectionOfCountries( "Canterbury"))
   print(isCollectionOfCountries( "Europe"))
   print(isCollectionOfCountries( "Commonwealth"))    

   print(ListOfCountries("Iberia"))





def ContainsCountry(data):
    
   if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                return True
   return False

def ContainsStartEndDate(data):
    if isinstance(data, dict):
        # Check top-level keys
        if 'start_date' in data and 'end_date' in data:
            return data['start_date'] is not None and data['end_date'] is not None
        
        # Check nested dictionaries
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and 'start_date' in item and 'end_date' in item:
                        if item['start_date'] is not None and item['end_date'] is not None:
                            return True

    return False


def MainDialogue():
    print("Welcome!")
    print("What is your username?")
    global user 
    user = sys.stdin.readline().strip()
    passwd = getpass.getpass("Enter password:")
 
    if ( not is_user_valid(user)):
        print("Login Failed")
        exit(0)
    print("Login for ", user, "succeeded.")
    print ("Please pose your question about exchange rates with the Canadian dollar over a time period. Type Quit to exit")
 
    hasCountry = False
    hasDateRange = False
    while (not hasCountry or not hasDateRange):
        line = sys.stdin.readline().strip()
        if (line.lower() == "quit"): exit(0)

        country_json = ListOfCountries(line)
        hasCountry = ContainsCountry(country_json)
        date_json = ListOfDateRanges(line)
        hasDateRange = ContainsStartEndDate(date_json)
    
        if (hasCountry and hasDateRange):
            continue
        elif (not hasCountry and not hasDateRange):
            nextprompt = "Please rephrase the question to include at least one country or currency and to include one or more dates. Type Quit to exit"
        elif (not hasDateRange):
            nextprompt = "Please rephrase the question to include include one or more dates. Type Quit to exit"
        else:
            nextprompt = "Please rephrase the question to include at least one country, group of countries or currency. Type Quit to exit"
        print(nextprompt)
    
    mystring = "ChatGPT has analyzed your question and found it contains these countries: " + str(country_json)
    infolog(mystring)
    mystring = "ChatGPT also found these dates in your question: " + str(date_json)
    infolog(mystring)
    infolog("Passing the countries and dates in your question to the Bank of Canada application....")

    return country_json, date_json

def AnalyzeRateInfo (rate_dict):
    exit_loop = False
    while (not exit_loop):
        print("Do you have a question for ChatGPT about the data that was returned? e.g. Maximum value in range.")
        print("If so, type your question or type 'Quit' to exit")
        line = sys.stdin.readline().strip()
        if (line.lower() == "quit"): exit(0)
    
        question = "Given these numeric values: " + str(rate_dict) + ". " + line
        
        stream = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=[{"role": "user", "content": question}],
          stream=True,
       )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")





   

client = OpenAI(
  organization='',
  project='',
)


country_list, dates_list = MainDialogue()

#country_json, date_json = ApplyAccessRulesFilters(user, country_json, date_json)
#pruned_country_list, pruned_date_list = 
result, new_country_list, new_dates_list = ApplyAccessRulesFilters(user, country_list, dates_list)
if (result == True):
    last_rate_dict = GetRatesFromBofC(new_country_list, new_dates_list)

    if (last_rate_dict):
        pass
        #TODO - ask another question about the data
        AnalyzeRateInfo(last_rate_dict)


exit(0)



stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": "Assistant"},
              {"role": "user", "content": line}],
    stream=True,
)

for chunk in stream:
    for choice in chunk.choices:
        print(chunk.choices[0].delta.content, end="")

stream1 = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": "Assistant"},
              {"role": "user", "content": "What countries are represented in the following string: '" + line+ "'. Return result as a JSON object."}],
    stream=True,
)

for chunk in stream1:
    #print(chunk.choices)
    for choice in chunk.choices:
        print(chunk.choices[0].delta.content, end="")


 
 



    
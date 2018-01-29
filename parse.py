from bs4 import BeautifulSoup
import requests
import json

debug = False



def get_results(url):
    r  = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    return convert_results(soup)
    
def convert_results(soup):
    results = []
    crews = []
    losers = []
    for result in soup.select(".race-results-bg"):
        winner = result.select_one(".winner").text
       	loser = result.select_one(".loser").text

       	# For some vents (e.g. Thames Challenge Cup 2001) crew names have question marks for some races
       	# which prevents the crews from being 'joined up'
        winner = winner.replace('?', '')
       	loser = loser.replace('?', '')

        margin = result.select_one(".verdict-content").text
            
        margin_string = margin    
        margin = margin.replace(u'\xbd', ' 1/2')
        margin = margin.replace(u'\u2153', ' 1/3')
        margin = margin.replace(u'\u2154', ' 2/3')
        margin = margin.replace(u'\xbc', ' 1/4')
        margin = margin.replace(u'\xbe', ' 3/4')
        margin = margin.replace(u'\xa0', ' ')
        margin.encode('ascii', 'ignore')


        if debug:
            print "%s beat %s by %s\n" % (winner, loser, margin)
            
        results.append({"winner": winner, "loser": loser, "margin": convert_distance(margin), "margin_string": margin_string})
        
        if winner not in crews:
            crews.append(winner)

        if loser not in crews:
            crews.append(loser)
            
        if loser not in losers:
            losers.append(loser)
            
    margins = {}
    
    if len(crews) == 0:
    	return {"crews": [], "races": []}  # 2006 Steward's challenge Cup....

    for winner in list(set(crews) - set(losers)):
    	# Yes, there should always be a unique winner, but in 2017 Wyford Challenge Cup, 
    	# City of Bristol R.C. 'B' beat Sydney R.C., AUS then disappeared

	    margins[winner] = 0
    

    while len(margins.keys()) < len(crews):
    	for crew in crews:

    		if crew in margins.keys():
    			continue

	        for result in results:
	            if result["loser"] == crew and result["winner"] in margins.keys():
	                margins[crew] = margins[result["winner"]] + result["margin"]
	                break

        
    crew_results = []
    i = 0
    for crew, margin in sorted(margins.items(), key=lambda x: x[1]):
        crew_results.append({"crew": crew, "margin": margin, "id": i, "country": get_country(crew)})
        i += 1
    
    return {"crews": crew_results, "races": results}


def get_country(team_name):
    parts = team_name.split(",")
    
    if len(parts) == 1:
        return ""
    else:
        return parts[-1].strip()


def convert_distance(distance):
    #distance.encode('utf-8').decode('ascii', 'ignore')

    distance = distance.replace(u'\xbd', '1/2')
    distance = distance.replace(u'\u2153', '1/3')
    distance = distance.replace(u'\u2154', '2/3')
    distance = distance.replace(u'\xbc', '1/4')
    distance = distance.replace(u'\xbe', '3/4')
    distance = distance.replace(u'\xa0', ' ')
    distance.encode('ascii', 'ignore')


    distance = str(distance).strip().lower()

    distance = distance.replace("one", "1")  # "one foot"
    distance = distance.replace("foot", "feet") # "one foot"
    distance = distance.replace("ft", "feet") 

    for bad_phrase in ["disq", "dsq", "no time taken", "to be re-rowed", "sculled over", "rowed over", "not rowed out", "not sculled out", "withdrawn", "n/a"]:
    	if bad_phrase in distance:
    		return 0

    if distance == "2ft":
    	return 2 / 62

    if distance == "easily":
        return 3
    elif distance == "canvas":
        return 1/6

    elif len(distance) == 0:
    	return 0

    elif "feet" in distance:
        distance = distance.replace("feet", "")

        return float(distance) / 62 # TODO: correct conversion factor for other boat classes

        # single 27ft, double/pair 34ft, quad/four 44ft; eight 62 (accoridng to http://www.rudern-ooe.at/fileadmin/wru23ch2013/Website-Fotos/Sonstiges/Boat_Classes-1.pdf)

    distance = distance.replace("lengths", "")
    distance = distance.replace("length", "")
    
    if "/" in distance:
        (numerator, denominator) = distance.split("/")
        
        integer = 0        
        if len(numerator) > 1:
        	integer = numerator[0:-1]
        	numerator = numerator[-1]

        return float(integer) + float(numerator) / float(denominator)
    else:
        return float(distance)
    

    # distance may be:
    # - an integer number of lengths
    # - a fractional number of lengths (1/2, 3 1/4, etc.)
    # - 'easily'
    # - 'a canvas'
    # - a numebr of feet (e.g. 3 feet)


def getEventNames(year):

    data = {
        'form_build_id': 'form-KTaIp12fMy6UUoYdxItUc5dwmTc3oHf35XeOAAR_dB0',  # this field changes
        'form_id': 'henley_search_results_form',
        'year_select': year,
        'trophy_event_select': '0',
        'crew_search': '0',
        '_triggering_element_name': 'year_select'
    }

    url = 'https://www.hrr.co.uk/system/ajax'
    r = requests.post(url, data=data)


    html = filter(lambda x: 'data' in x.keys(), r.json())[0] # array index seems to change between requests
    soup = BeautifulSoup( html["data"] )

    event_names = {}

    for option in soup.find("select").findAll("option"):
        event_names[option["value"]] = option.text

    return event_names


def getAll():
	all_results = []

	for year in range(2000, 2018):
	    event_names = getEventNames(year)
	    for event_id in event_names:

	    	if event_id == "0":
	    		continue

	        url = "https://www.hrr.co.uk/henley-results/search/%s/%s/0" % (year, event_id)
	        event_name = event_names[event_id].split("-")[0].strip()

	        print "\n\nLoading %s (%s)"  % (event_name, year)
	        result = get_results(url)
	        print result

	        all_results.append({"year": year, "event_id": event_id, "event_name": event_name, "results": result})


	with open("all_results.json", "w") as fp:
	    json.dump(all_results, fp)

getAll()

#url = "https://www.hrr.co.uk/henley-results/search/2017/38390/0"
#url = "https://www.hrr.co.uk/henley-results/search/1999//0"

#print json.dumps(get_results(url))
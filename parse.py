from bs4 import BeautifulSoup
import requests
import json

debug = False



def get_results(url):
    r  = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data)
    convert_results(soup)
    
def convert_results(soup):
    results = []
    crews = []
    losers = []
    for result in soup.select(".race-results-bg"):
        winner = result.select_one(".winner").text
        loser = result.select_one(".loser").text
        margin = result.select_one(".verdict-content").text
            
        if debug:
            print "%s beat %s by %s\n" % (winner, loser, margin)
            
        results.append({"winner": winner, "loser": loser, "margin": convert_distance(margin), "margin_string": margin})
        
        if winner not in crews:
            crews.append(winner)

        if loser not in crews:
            crews.append(loser)
            
        if loser not in losers:
            losers.append(loser)
            
    margins = {}
    
    winner = list(set(crews) - set(losers))[0]
    margins[winner] = 0
    
    for crew in crews:
        for result in results:
            if result["loser"] == crew and result["winner"] in margins.keys():
                margins[crew] = margins[result["winner"]] + result["margin"]
        
    crew_results = []
    i = 0
    for crew, margin in sorted(margins.items(), key=lambda x: x[1]):
        crew_results.append({"crew": crew, "margin": margin, "id": i, "country": get_country(crew)})
        i += 1

            
    
    print json.dumps({"crews": crew_results, "races": results})



def get_country(team_name):
    parts = team_name.split(",")
    
    if len(parts) == 1:
        return ""
    else:
        return parts[-1].strip()


def convert_distance(distance):
    distance = str(distance)
    distance = distance.replace("lengths", "")
    distance = distance.replace("length", "")
    
    if "/" in distance:
        (numerator, denominator) = distance.split("/")
        
        integer = 0
        if " " in numerator:
            (integer, numerator) = numerator.split(" ")
        
        return float(integer) + float(numerator) / float(denominator)
    else:
        return float(distance)
    
    # distance may be:
    # - an integer number of lengths
    # - a fractional number of lengths (1/2, 3 1/4, etc.)
    # - 'easily'
    # - 'a canvas'
    # - a numebr of feet (e.g. 3 feet)


url = "https://www.hrr.co.uk/henley-results/search/2016/38376/0"
get_results(url)
from bs4 import BeautifulSoup
import requests
import json

# TODO: FIXME
def get_country(crew):
    return ""

def convert_distance(distance):
    # distance.encode('utf-8').decode('ascii', 'ignore')

    distance = distance.replace(u'\xbd', '1/2')
    distance = distance.replace(u'\u2153', '1/3')
    distance = distance.replace(u'\u2154', '2/3')
    distance = distance.replace(u'\xbc', '1/4')
    distance = distance.replace(u'\xbe', '3/4')
    distance = distance.replace(u'\xa0', ' ')
    distance.encode('ascii', 'ignore')

    distance = str(distance).strip().lower()

    distance = distance.replace("one", "1")  # "one foot"
    distance = distance.replace("foot", "feet")  # "one foot"
    distance = distance.replace("ft", "feet")

    distance = distance.replace("easiy", "easily") # typo in 2022
    distance = distance.replace("lenghts", "lengths") # typo in 2022

    for bad_phrase in ["disq", "dsq", "no time taken", "to be re-rowed", "sculled over", "rowed over", "not rowed out",
                       "not sculled out", "withdrawn", "n/a", "nro"]:
        if bad_phrase in distance:
            return 0

    if distance == "1 inch":
        return (2/12) / 62

    if distance == "2ft":
        return 2 / 62

    if distance == "easily":
        return 3
    elif distance == "canvas":
        return 1 / 6

    elif len(distance) == 0:
        return 0

    elif "feet" in distance:
        distance = distance.replace("feet", "")

        return float(distance) / 62  # TODO: correct conversion factor for other boat classes

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

def calculate_crew_margins(results):
    crews = []
    losers = []

    for result in results:
        winner = result["winner"]
        loser = result["loser"]

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

    return crew_results



def get_results_for_year(year):
    page = 1

    results = {}
    event_name = {}

    while True:
        url = f"https://www.hrr.co.uk/wp-admin/admin-ajax.php?action=results_get_results&race-year={year}&result-page={page}"
        print(f"Fetching page {page} for {year}")
        r = requests.get(url)
        data = r.json()

        # this happens for 2020 results, as even cancelled
        if data["pagination"]["totalPages"] == page:
            break

        for result_data in data["results"]:
            event_id = result_data["trophy"]["id"]
            event_name[event_id] = result_data["trophy"]["name"]

            if event_id not in results:
                results[event_id] = []

            results[event_id].append({
                "winner": result_data["winner"]["name"],
                "loser": result_data["loser"]["name"],
                "margin_string": result_data["verdict"],
                "margin": convert_distance(result_data["verdict"])
            })

        if data["pagination"]["totalPages"] == page:
            break
        page += 1

    output = []
    for event_id in event_name.keys():
        output.append({
            "event_id": event_id,
            "event_name": event_name[event_id],
            "results": {
                "races": results[event_id],
                "crews": calculate_crew_margins(results[event_id])
            },
            "year": year
        })

    return output

year = 2018

for year in [2018, 2019, 2021, 2022]:
    with open(f"{year}.json", "w") as fp:
        json.dump(get_results_for_year(year), fp, indent=4)


# {
#                 "event_id": result_data["trophy"]["id"],
#                 "event_name": result_data["trophy"]["name"],
#
#             }
import csv
import json
import requests
import os

main_url = "https://warhammerunderworlds.com/wp-json/wp/v2/"
sub_pages = ["cards", "card_types", "sets", "warbands"]
options = {"cards": "?per_page=1000", "card_types": "?per_page=100", "sets": "?per_page=100",  "warbands": "?per_page=100"}

icon_folder = os.path.join("img/icon")
  
#"builds" - Starter decks
#"types" - card_types, sets, warbands
#"categories" - ?

def main():
  data = {}
  for p in sub_pages:
    data[p] = fetch_gw_data (p)#
    
  # make_card
  cards = gw_to_cards(data["cards"])
  
  with open('cards-en.json', 'w+') as jsonfile:
    json.dump(cards, jsonfile, sort_keys=True, indent=2)
  
  # download card images
  for c in cards:
    image_folder = os.path.join("img/card")
    filepath = os.path.join(image_folder, c["image_filename"])
    if not os.path.exists(filepath):
      response = requests.get( c["image_url"], allow_redirects=True)
      with open(filepath, 'wb') as imgfile:
        imgfile.write(response.content)
  
  # download warband icons
  for wb in data["warbands"]:
    filepath = os.path.join(icon_folder, 'warband_' + str(wb['id']) + '.png')
    if not os.path.exists(filepath):
      response = requests.get( wb['acf']['icon']['url'], allow_redirects=True)
      with open(filepath, 'wb') as imgfile:
        imgfile.write(response.content)
        
  # download card_type icons
  for ct in data["card_types"]:
    filepath = os.path.join(icon_folder, 'type_' + str(ct['id']) + '.png') #ct['acf']['icon']['filename']
    if not os.path.exists(filepath):
      response = requests.get( ct['acf']['icon']['url'], allow_redirects=True)
      with open(filepath, 'wb') as imgfile:
        imgfile.write(response.content)
      
  # download set icons
  for s in data["sets"]:
    filepath = os.path.join(icon_folder, 'set_' + str(s['id']) + '.png')
    if not os.path.exists(filepath):
      response = requests.get( s['acf']['icon']['url'], allow_redirects=True)
      with open(filepath, 'wb') as imgfile:
        imgfile.write(response.content)

def fetch_gw_data(page):
  url =  main_url + page + "/" + options[page]
  print(url)
  response = requests.get(url)
  if response.status_code != 200:
    print("Error ({}) fetching GW data".format(response.status_code))
    return None
  
  return response.json()
  
def gw_to_cards(gw_data):
  return [create_card_from_gw(gw) for gw in gw_data]

# some names in GW data are '123. Foo' and others are just 'Foo'
def normalize_name(name):   
  if '.' in name:
    name = '.'.join(name.split('.')[1:]).strip()
  return name.replace(u"\u2018", "'").replace(u"\u2019", "'").replace("&#8217;", "'").replace("&#8216;", "'")

def create_card_from_gw(gw):
  return {
    "gw_id": gw["id"],
    "name": normalize_name(gw["title"]["rendered"]),
    "gw_card_type_id": gw["card_types"][0],
    "gw_card_set_id": gw["sets"][0],
    "gw_warband_id": gw["warbands"][0],
    "gw_number": gw["acf"]["card_number"],
    "image_url": gw["acf"]["card_image"]["url"],
    "image_filename": gw["acf"]["card_image"]["filename"],
    "is_new": gw["acf"]["is_new"]
  }		
  
main()
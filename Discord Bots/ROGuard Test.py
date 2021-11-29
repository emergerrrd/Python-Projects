from discord.ext import commands
import discord, chalk
import requests
import bs4 as bs
import pandas as pd
import re

command_pref = "rog "
max_no_shown = 5
exclusions = ["Type", "Zone", "Passive Lv", "Max Stack", "Sellable", 
                "Sell Price", "Auctionable", "Storageable", "Base Exp", "Job Exp"]

def search_roguard(link):
    soup = bs.BeautifulSoup(requests.get(link).text, features="html.parser")
    search_table = soup.find('table', {'class':'table text-center'})
    if search_table is not None:
        return search_table.findAll('a')
    else:
        return None

def get_page(results_list, search_item):
    link_to_item = "https://www.roguard.net"
    for a in results_list:
        if a.string.lower() == search_item.lower().replace("*", "★"):
            link_to_item += a['href']
    return bs.BeautifulSoup(requests.get(link_to_item).text, features="html.parser"), link_to_item

def get_table(soup, table):
    header = soup.find('h2', text=table)
    if header is None:
        return None
    else:
        return header.find_next_sibling('table').findAll('tr')

def get_card_effects(soup, search_item):
    if not search_item[-4:] == "card":
        return None
    else:
        card_effects_list = []
        card_effects_list.append(soup.find('h2', text="Effect").find_next_sibling('div'))
        card_effects_list.append(soup.find('h2', text="Perma Buff").find_next_sibling('div'))
        card_effects_list.append(soup.find('h2', text="Slot").find_next_sibling('div'))
        card_effects_list.append(soup.find('h2', text="Type").find_next_sibling('div'))
    return card_effects_list

def get_dropped_by(soup):
    dropped_by_header = soup.find('h2', text="Dropped By")
    if dropped_by_header is None:
        return None
    else:
        return dropped_by_header.find_parent('div').findAll('div', style="display: inline-block; padding-left: 5px;")

def get_locations(soup):
    locations_header = soup.find('h2', text="Locations")
    if locations_header is None:
        return None
    else:
        return locations_header.find_parent('div').findAll('div', style="text-align: center; margin-top: 5px;")

def get_drops(soup):
    locations_header = soup.find('h2', text="Drops")
    if locations_header is None:
        return None
    else:
        return locations_header.find_parent('div').findAll('div', style="text-align: center; margin-bottom: 4px;")

def build_table_str(tr_list, link):
    if tr_list is None:
        return None
    else:
        table_str = "```\n"
        for tr in tr_list:
            if (tr.findAll('td')[0].string in exclusions or 
                (tr.findAll('td')[0].string == "Level" and "/items/" in link)):
                pass
            else:
                for br in tr.findAll('br'):
                    br.extract()
                for td in tr.findAll('td'):
                    table_str += td.text if not (td.text == "") else ""
                    table_str += ": "
                table_str = table_str[:-2]+"\n"
        table_str += "\n```"

        if table_str.replace("`", "").replace("\n", "") == "":
            table_str = None
        
        return table_str

def build_card_effects_str(card_effects):
    if card_effects is None:
        return None
    switcher = {
            0: "Effects: ",
            1: "Perma Buff: ",
            2: "Slot: ",
            3: "Type: ",
        }
    card_effects_str = "\n```\n"
    for idx, effect in enumerate(card_effects[:-1]):
        card_effects_str += switcher.get(idx)+effect.text.replace("\n\n", ", ")+"\n"
    card_effects_str += "```\n"
    
    return card_effects_str

def build_dropped_by_str(monsters):
    if monsters is None:
        return None
    else:
        df = pd.DataFrame(columns=['Monster', 'Drop%'])
        dropped_by_list_str = "```\nDropped by:\n"
        
        for div in monsters:
            df2 = pd.DataFrame([[div.find('a').string, float(div.findAll('div')[2].string.replace("%", "").replace("?", "0"))]], 
                columns=['Monster', 'Drop%'])
            df = df.append(df2)
        df = df.sort_values(by=['Drop%'], ascending=False)

        count = 0
        for index, monster in df.iterrows():
            dropped_by_list_str += monster['Monster']+" "+(str(monster['Drop%']) if not monster['Drop%'] == 0 else "?")+"%\n"
            count += 1
            if count == max_no_shown: break
        dropped_by_list_str = dropped_by_list_str[:-1]
        if len(df) > max_no_shown:
            dropped_by_list_str += "\nand {} more...".format(len(df)-max_no_shown)
        del count
        dropped_by_list_str += "\n```"
        
        if dropped_by_list_str.replace("Dropped by:", "").replace("`", "").replace("\n", "") == "":
            dropped_by_list_str = None
        
        return dropped_by_list_str

def build_locations_str(locations):
    if locations is None:
        return None
    else:
        locations_str = "```\nLocations:\n"
        for div in locations:
            locations_str += re.sub(' +', ' ', div.text.replace("\n", ""))+"\n"
        locations_str += "```\n"
        
        return locations_str

def build_drops_str(drops):
    if drops is None:
        return None
    else:
        drops_str = "```\nDrops:\n"
        for div in drops:
            drops_str += re.sub(' +', ' ', div.text.replace("\n", ""))+"\n"
        drops_str += "```\n"
        
        return drops_str

search_item = "garlet"
search_link = 'https://www.roguard.net/db/search/?search='
search_link += search_item.lower().replace(' ', '+').replace("*", "★")
print("rog search", search_item)
print(search_link)
    
results_list = search_roguard(search_link[:-1])
if results_list is None:
    print("No search results!")
else:
    soup, link_to_item = get_page(results_list, search_item)
    print(link_to_item)
        
    common_table_str = build_table_str(get_table(soup, "Common"), link_to_item)
    dropped_by_str = build_dropped_by_str(get_dropped_by(soup))
    locations_str = build_locations_str(get_locations(soup))
    card_effects_str = build_card_effects_str(get_card_effects(soup, search_item))
    # attributes_table_str = build_table_str(get_table(soup, "Attributes"))
    # stats_table_str = build_table_str(get_table(soup, "Stats"))
    # drops_str = build_drops_str(get_drops(soup))

    if not card_effects_str is None and not dropped_by_str is None:
        print("```"+card_effects_str.replace("```", "")+dropped_by_str.replace("```", "")+"\n```")
    elif not common_table_str is None and not dropped_by_str is None:
        print("```"+common_table_str.replace("```", "")+dropped_by_str.replace("```", "")+"\n```")
    elif not common_table_str is None and not locations_str is None: # and not drops_str is None:
        print("```"+common_table_str.replace("```", "")+locations_str.replace("```", "")+"\n```")
        # print("```"+common_table_str.replace("```", "")+locations_str.replace("```", "")+drops_str.replace("```", "")+"\n```")
    elif not common_table_str is None:
        print(common_table_str)
    elif not dropped_by_str is None:
        print(dropped_by_str)
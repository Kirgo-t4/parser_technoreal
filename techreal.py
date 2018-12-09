
# -*- coding: utf-8 -*-

import urllib.request
import re
import csv
from bs4 import BeautifulSoup

BASE_LINK = "https://technoreal.ru"

def get_html(url):
   response = urllib.request.urlopen(url)
   return response.read()

def get_cathegories(html):
    cathegories = []
    bs = BeautifulSoup(html,features="html.parser")
    c_block = bs.select("div[class=moduletable]")
    for cb in c_block:
        if (cb.find("h3") is not None) and (cb.find("h3").text == "Каталог ТЕХНОРЕАЛ"):
            group_links = cb.select("li")
            cur_group = None
            for link in group_links:
                if repr(link).find("<ul>") == -1:
                    if link.a.has_attr('href'):
                        cathegories.append({'name':link.a.text, 'link': BASE_LINK + link.a['href'], 'isGroup':False, 'group': cur_group})
                else:
                    cur_group = link.a.text
                    if link.a.has_attr('href'):
                        cathegories.append({'name':cur_group, 'link': BASE_LINK + link.a['href'], 'isGroup':True, 'group': None})
    return cathegories

def get_goods(html):
    goods = []
    bs = BeautifulSoup(html, features="html.parser")
    good_links_headers = bs.select("div[class=row] table tr td h2")
    for glh in good_links_headers:
        if glh.a is not None:
            if glh.a.has_attr('href'):
                goods.append({'name':glh.a.text, 'link': BASE_LINK + glh.a['href']})
    return goods

def get_characteristiks_of_good(name, cathegory, html):
    chars = {}
    chars['Имя'] = name
    chars['Категория'] = cathegory
    bs = BeautifulSoup(html, features="html.parser")
    art = bs.find("div",{"class": "addtocart-area"})
    chars['Артикул'] = (re.sub(r'^арт. ','',art.text.strip().split('\n')[0]).strip())
    good_table = bs.select_one("table[class=tech]")
    if good_table is not None:
        for row in good_table.select("tr"):
            cols = row.select("td")
            try:
                chars[cols[0].text.strip()] = cols[1].text.strip()
            except:
                pass
    return chars

def make_common_list_of_headers(headers):
    first_keys = ['Имя', 'Категория', 'Артикул']
    return first_keys + list(headers.difference(first_keys))

def print_in_csv_file(filename,keys,list_disct_values):
    with open(filename, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";")
        csv_writer.writerow(keys)
        for ch_good in list_disct_values:
            values = list()
            for ch_key in keys:
                if ch_key in ch_good:
                    values.append(ch_good[ch_key])
                else:
                    values.append('NULL')
            csv_writer.writerow(values)


def main():
    ch_goods = []
    ch_keys = set()
    for cathegory in get_cathegories(get_html(BASE_LINK))[:2]:
        print(cathegory)
        if not cathegory['isGroup']:
            goods = get_goods(get_html(cathegory['link']))
            for good in goods:
                print(good)
                ch = get_characteristiks_of_good(good['name'],cathegory['name'],get_html(good['link']))
                ch_goods.append(ch)
                ch_keys = ch_keys.union(set(list(ch.keys())))
    print(len(ch_keys))

    list_ch_keys = make_common_list_of_headers(ch_keys)

    print(ch_keys)
    print_in_csv_file('parsed.csv',list_ch_keys,ch_goods)


if __name__ == '__main__':
    main()

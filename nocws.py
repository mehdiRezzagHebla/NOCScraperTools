# Created by Mehdi Rezzag Hebla
# A set of functions to automate data collection from
# National Olympic Committees' websites.
from requests_html import HTMLSession
import pprint
import webbrowser
import csv
import json
import re
from copy import deepcopy
from time import sleep
import time
import copy

# change this path to the browser of choice on your machine
link_to_browser = 'C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
# registring browser
webbrowser.register('brave', None, webbrowser.BackgroundBrowser(
    link_to_browser))
# setting browser as the one that opens the provided links
open_link = webbrowser.get('brave')
session = HTMLSession()
noc_url = {}

# link to the csv container contry, url
csv_file = 'D:\\Doctorat\\Doctorat\\Book2.csv'
with open(csv_file, 'r') as csv_r:
    lines = csv.reader(csv_r, delimiter=';')
    for line in lines:
        # print(line[1])
        noc_url.update({line[0]: line[1]})
# print(noc_url)
fb_links_country = {}
recursion_degree = 1
error_dict = {}


def write_to_json(dictionary):
    with open('country_fb.json', 'w') as writable:
        json.dump(dictionary, writable, indent=4)


err_country = None


def func(noc_url, recursion_degree, error_dict):
    global err_country
    error_dict = error_dict
    global fb_links_country
    dict_copy = noc_url
    print(f'Recursion degree {recursion_degree}')
    time.sleep(2)
    for country in list(dict_copy.keys()):
        url = dict_copy.get(country, None)
        if not url or (country == err_country) or (country == 'syrian arab republic'):
            try:
                dict_copy.pop(country)
            except Exception as e:
                print(e)
            continue
        if url.startswith('www'):
            url = 'http://' + url
        try:
            fb_links_country.update({country: []})
            print(f'Fetching data for: {country}...')
            session = HTMLSession()
            error_dict.update({country: 1})
            r = session.get(url)
            urls = r.html.absolute_links
            dict_copy.pop(country)
            print('looking for facebook related links...')
            for link in urls:
                if 'facebook' in link:
                    fb_links_country[country].append(link)
        except Exception as e:
            print('Exception occured:')
            print(e)
            print('sleeping for 2 secs.')
            time.sleep(2)
            error_dict[country] += 1
            if error_dict[country] == 5:
                err_country = country
                dict_copy.pop(country)
            recursion_degree += 1
            if dict_copy:
                func(dict_copy, recursion_degree, error_dict)
    write_to_json(fb_links_country)
    print('Done.')
    with open('countr_fb.json', 'a') as writable:
        data = json.dumps(error_dict)
        writable.write(data)


# just a function that indents lines in the json file
def serialize():
    content = {}
    sanitized = {}
    with open('country_fb.json') as file:
        f = json.load(file)
        content = copy.deepcopy(f)
    for country in content.keys():
        if content[country]:
            sanitized.update({country: content[country]})
    # with open('country_fb_serialized.json', 'w') as f:
    #     json.dump(sanitized, f, indent=4)
    x = 0
    for _ in sanitized.keys():
        x += 1
    print(x)


# func(noc_url, recursion_degree, error_dict)


serialized_json_fb = 'C:\\Users\\EM\\Desktop\\Scripts\\gui\\modified_country_fb_serialized.json'
csv_file_wfb = r'D:\Doctorat\Doctorat\Book2.csv'


def read_json(path):
    fb_links = {}
    with open(path, 'r') as file:
        fb_links = json.load(file)
    # pprint.pprint(fb_links)
    return fb_links


def read_csv(path):
    lines = {}
    with open(path, 'r') as f:
        r = csv.reader(f, delimiter=';')
        for line in r:
            lines.update({line[0]: line[1]})
    # print(list(lines.items())[0])
    return lines


def write_custom_json(countries_and_fb, websites):
    new_dict = {}
    for country, fbs in countries_and_fb.items():
        wb = websites[country]
        x = {country: {'website': wb, 'facebook links': fbs, 'email': None}}
        new_dict.update(x)
    # pprint.pprint(new_dict, indent=4)
    with open('semi_final_json.json', 'w') as w:
        json.dump(new_dict, w, indent=4)


def fetch(session, url):
    r = session.get(url)
    return r


def fetch_cntct_urls(path_to_json):
    content_dict = {}
    with open(path_to_json, 'r') as rr:
        cont = json.load(rr)
        content_dict = deepcopy(cont)
    error_dict = {}
    new_content_dict = {}
    session = HTMLSession()
    for country, data in content_dict.items():
        print(f'Fetching data for {country}:    {data["website"]}')
        try:
            try:
                for x in range(3):
                    print(f'loop {x}')
                    r = fetch(session, data['website'])
                    sleep(1)
                    status_code = r.status_code
                    print(status_code)
                    if status_code == 200:
                        break
            except:
                pass
            if status_code != 200:
                continue
            print('fetching absolute links...')
            links = r.html.absolute_links
            list_of_contact_links = []
            num = 1
            for link in links:
                if ('contact' in link) or ('email' in link) or ('mail' in link):
                    print(f'email link found: {num}')
                    list_of_contact_links.append(link)
                num += 1
            new_data = deepcopy(data)
            if list_of_contact_links:
                new_data.update({'email_links': list_of_contact_links})
            else:
                new_data.update({'email_links': None})
            new_content_dict.update({country: new_data})
        except Exception as e:
            print('Exception occured')
            print(e)
            error_dict.update({country: data['website']})
    print(error_dict)
    with open('error_dict.json', 'w') as f:
        json.dump(error_dict, f, indent=4)
    with open('new_content_dict.json', 'w') as f:
        json.dump(new_content_dict, f, indent=4)
    print("done")


path = r'C:\Users\EM\Desktop\Scripts\gui\semi_final_json.json'
# fetch_cntct_urls(path)

# this function needs html content already populated
# this function populates email list with emails


def reg_fetch_email(json_source):
    # create empty dict
    content_dict = {}
    # open json_source
    with open(json_source, 'r') as js:
        #   deepcopy content to e_d
        x = json.load(js)
        content_dict = deepcopy(x)
    # for country, data in e_d.items():
    for data in content_dict.values():
        #   e_d['email'] = []
        data['email'] = []
    # for country, data in e_d.items():
    for data in content_dict.values():
        #   for html in data['html content']:
        for html in data['html content']:
            #       reg_expression
            matches = reg_email_lookup(html)
    #       if result found:
            if matches:
                #           for email in result:
                for email in matches:
                    #               e_d['email].append(result)
                    data['email'].append(email)
    # with open('some name.json', 'w') as wtable:
    with open(json_source, 'w') as js:
        #   json.dump(e_d, wtable, indent=4)
        json.dump(content_dict, js, indent=4)
    print('email addresses added to the json file')


# this function loops through html list
# matches email
# returns list of emails
def reg_email_lookup(string):
    matched_strings = []
    # experiment with regex: DONE
    expression = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    compiled = re.compile(expression)
    matches = compiled.findall(string)
    if matches:
        for match in matches:
            matched_strings.append(match)
        return matched_strings
    else:
        return None

# this function only consolidates links
# passes them to the fetch function which downloads the content


def consolidate_link_list(json_source):
    c_d = {}
    with open(json_source, 'r') as rdable:
        c = json.load(rdable)
        c_d = deepcopy(c)
    # for country, data in e_d.items():
    for data in c_d.values():
        list_of_urls = []
    #   list_of_urls.append(data['website])
        list_of_urls.append(data['website'])
        if data['email_links']:
            #   for url in data['email_links']:
            for url in data['email_links']:
                #       list_of_urls.append(url)
                list_of_urls.append(url)
        data.update({'list_of_urls': list_of_urls})
    with open(json_source, 'w') as wtable:
        json.dump(c_d, wtable, indent=4)


# this function handles fetching and returning a string
# of html content of a page
def get_function(url, session):
    failed = False
    status_code = None
    try:
        for i in range(3):
            print(f'get loop {i}: {url}')
            if failed:
                sleep(2)
            r = session.get(url)
            status_code = r.status_code
            if status_code == 200:
                break
            else:
                failed = True
    except Exception as e:
        print(f'>>> exception occured\n{e}')
    if status_code == 200:
        print(f'Captured HTML content successfully: {status_code}')
        return str(r.html.html)
    else:
        return None

# this is the second to final function


def fet_page_html(json_source):
    session = HTMLSession()
    # create empty dict
    c_dict = {}
    # open json_source
    with open(json_source, 'r') as rdabl:
        c = json.load(rdabl)
        c_dict = deepcopy(c)
    # for country in e_d
    for data in c_dict.values():
        #   update with html content: []
        data.update({'html content': []})
    #   list_of_urls = consolidate_link_list(e_d)
    with open(json_source, 'w') as wtabl:
        json.dump(c_dict, wtabl, indent=4)
    consolidate_link_list(json_source)
    with open(json_source, 'r') as rdabl:
        c = json.load(rdabl)
        c_dict = deepcopy(c)
    #   for url in list_of_urls
    for country, data in c_dict.items():
        print(f'Fetching data for {country}...')
        for url in data['list_of_urls']:
            r = get_function(url, session)
            if r:
                data['html content'].append(r)
    with open(json_source, 'w') as wtable:
        json.dump(c_dict, wtable, indent=4)
    print('Done.')

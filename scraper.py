# # # -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import sqlite3
import datetime
import os.path

# I was thinking about using selenium to search for an element
# via the search-bar on top of the website.
# But I've realized it consumes too much time to open the driver,
# type in there, and then reload it again...
# I search for the product by extracting the source code of every page
# using BeautifulSoup.
# Having a 'soup' I search for the product by its name
# and extract the url to it.
# With url we send a get request and extract products' source code
# I search for the products' specifications, i.e. needle_size and
# safe it in the list. The list is then saved into the database
# Might be that you need to adjust the headers, that is your user agent.

# I used sqlite3 as a database.
# To open the sqlite3 database in vs-code you need to install the sqlite extension

# TODO: Schedule the script to run at specific times during the day

# headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
items = ['Stylecraft Special DK', 
		'DMC Natura XL',
		'Drops Safran',
		'Drops Baby Merino Mix',
		'Hahn Alpacca Speciale']

def get_delivery_time():
	url = 'https://www.wollplatz.de/versandkosten-und-lieferung'
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	table = soup.find('div', style='overflow-x: auto')
	tokens = []
	for i in table.find_all('td'):
		title = i.text
		tokens.append(title)
	delivery_time = tokens[9] #TODO: make it not hard-coded way
	return delivery_time

def get_number_of_pages():
	url = 'https://www.wollplatz.de/wolle'
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	divs = soup.find_all('div', class_='paginginnerholder')
	for item in divs:
		title = item.find('span', class_="paginavan").text.strip()
	number_of_pages = title.split(" ")[3]
	return int(number_of_pages)

# Extracts page source code
def extract(page):
	url = 'https://www.wollplatz.de/wolle?page={}'.format(page)
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	return soup

# Groups name and the url of matching items in a dictionary 
def get_products(soup):
	my_dict = {}
	divs = soup.find_all('div', class_='productlistholder')
	for item in divs:
		title = item.find('h3', class_="productlist-title").text.strip()
		if title in items:
			for i in item.find_all('a'):
				link = i.get('href')
				break
			my_dict[title] = link
	return my_dict

def get_product_info(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')

	name = soup.find('h1', id='pageheadertitle').text.strip()
	price = soup.find('span', class_='product-price').text.strip()
	# get specifications table
	specifications_table = soup.find('div', id='pdetailTableSpecs')
	specifications_tokens = []
	for i in specifications_table.find_all('td'):
		title = i.text
		specifications_tokens.append(title)
	needle_size_index = specifications_tokens.index('Nadelstärke') + 1
	composition_index = specifications_tokens.index('Zusammenstellung') + 1
	composition = specifications_tokens[composition_index]
	needle_size = specifications_tokens[needle_size_index]
	e = datetime.datetime.now()
	current_date = "{}/{}/{} {}:{}:{}".format(e.day, e.month, e.year, e.hour, e.minute, e.second)

	result = [current_date, name, price, get_delivery_time(), needle_size, composition]
	return result

def table_exists(db, tablename):
	c = db.cursor()
	c.execute('''
		SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{}';
		'''.format(tablename))
	if (c.fetchone()[0] == 1):
		return True

	return False

def main():
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	db_path = os.path.join(BASE_DIR, "wool_comparison.db")
	with sqlite3.connect(db_path) as db:
		c = db.cursor()
		if (table_exists(db, "wool_comparison") == False):
			c.execute('''CREATE TABLE wool_comparison(Date DATE, Name TEXT, Price TEXT, Delivery_time TEXT, Needle_size TEXT, Composition TEXT)''')

		number_of_pages = get_number_of_pages()
		found = 0
		print('START...')
		for page in range(1, number_of_pages + 1):
			print('page number {}/{}'.format(str(page), number_of_pages))
			soup = extract(page)
			products = get_products(soup)
			for key in products:
				if key in items:
					info = get_product_info(products[key])
					c.execute('''INSERT INTO wool_comparison VALUES(?, ?, ?, ?, ?, ?)''', info)
					found = found + 1
			if found == len(items): break
		print('DONE!')

		db.commit()

	db.close()

if __name__ == "__main__":
	main()

# # # -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from csv import writer

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}

# schedule the script to run at specific times during the day

# create a database and store csv files in it

def get_delivery_time():
	url = "https://www.wollplatz.de/versandkosten-und-lieferung"
	r = requests.get(url, headers=headers)
	soup = BeautifulSoup(r.content, 'html.parser')
	table = soup.find('div', style="overflow-x: auto")
	tokens = []
	for i in table.find_all('td'):
		title = i.text
		tokens.append(title)

	delivery_time = tokens[9]
	return delivery_time

def extract(page):
	url = "https://www.wollplatz.de/wolle?page={}".format(page)
	# print(url)
	r = requests.get(url, headers=headers)
	soup = BeautifulSoup(r.content, 'html.parser')
	return soup

def transform(soup):
	my_dict = {}
	divs = soup.find_all('div', class_='productlistholder')
	for item in divs:
		title = item.find('h3', class_="productlist-title").text.strip()
		for i in item.find_all('a'):
			link = i.get('href')
			break
		my_dict[title] = link
	return my_dict

def get_product_info(url):
	r = requests.get(url, headers=headers)
	soup = BeautifulSoup(r.content, 'html.parser')

	name = soup.find('h1', id="pageheadertitle").text.strip()
	price = soup.find('span', class_="product-price").text.strip()
	# get specifications table
	specifications_table = soup.find('div', id="ContentPlaceHolder1_upPanelTemplateValues")
	specifications_tokens = []
	for i in specifications_table.find_all('td'):
		title = i.text
		specifications_tokens.append(title)
	composition = specifications_tokens[7]
	needle_size = specifications_tokens[9]
	result = [name, price, get_delivery_time(), needle_size, composition]
	return result

with open('wool_comparison.csv', 'w', encoding='utf8', newline='') as f:
	thewriter = writer(f)
	head = ['Name', 'Price', 'Delivery time', 'Needle size', 'Composition']
	thewriter.writerow(head)
	products = []
	number_of_pages = 31
	page = 1
	for i in range(1, 31):
		c = extract(page)
		products = transform(c)
		for key in products:
			if (key == "Stylecraft Special DK"):
				info = get_product_info(products[key])
				thewriter.writerow(info)
			if (key == "DMC Natura XL"):
				info = get_product_info(products[key])
				thewriter.writerow(info)
			if (key == "Drops Safran"):
				info = get_product_info(products[key])
				thewriter.writerow(info)
			if (key == "Drops Baby Merino Mix"):
				info = get_product_info(products[key])
				thewriter.writerow(info)
			if (key == "hahn Alpacca Speciale"):
				info = get_product_info(products[key])
				thewriter.writerow(info)
		page = page + 1
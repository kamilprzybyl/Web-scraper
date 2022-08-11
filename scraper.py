# # # -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from csv import writer

# I was thinking about using selenium to search for an element in a search bar,
# but I've realized it consumes too much time to open the driver and type in there

# TODO: Schedule the script to run at specific times during the day
# TODO: Create a database and store csv files in it

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}

items = ['Stylecraft Special DK', 
		'DMC Natura XL',
		'Drops Safran',
		'Drops Baby Merino Mix',
		'Hahn Alpacca Speciale']

def get_delivery_time():
	url = 'https://www.wollplatz.de/versandkosten-und-lieferung'
	r = requests.get(url, headers=headers)
	soup = BeautifulSoup(r.content, 'html.parser')
	table = soup.find('div', style='overflow-x: auto')
	tokens = []
	for i in table.find_all('td'):
		title = i.text
		tokens.append(title)
	delivery_time = tokens[9] #TODO: make it not hard-coded way
	return delivery_time

# Extracts page source code 
def get_page_info(page):
	url = 'https://www.wollplatz.de/wolle?page={}'.format(page)
	r = requests.get(url, headers=headers)
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
	r = requests.get(url, headers=headers)
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
	composition = specifications_tokens[needle_size_index]
	needle_size = specifications_tokens[composition_index]
	result = [name, price, get_delivery_time(), needle_size, composition]
	return result


def main():
	try:
		f = open('wool_comparison.csv', 'w', encoding='utf8', newline='')
	except OSError:
		print('Could not open file wool_comparison.csv')
		sys.exit()

	with f:
		thewriter = writer(f)
		head = ['Name', 'Price', 'Delivery time', 'Needle size', 'Composition']
		thewriter.writerow(head)
		number_of_pages = 32
		found = 0
		for page in range(1, number_of_pages):
			print('page number ' + str(page))
			page_info = get_page_info(page)
			products = get_products(page_info)
			for key in products:
				if key in items:
					info = get_product_info(products[key])
					thewriter.writerow(info)
					found = found + 1
			if found == len(items): break

if __name__ == "__main__":
	main()
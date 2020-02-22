import itertools
import json
import os
import time

from bs4 import BeautifulSoup
import requests

PIC_URL = 'https://usdawatercolors.nal.usda.gov/pom/download.xhtml?id=POM{}'
LOW_RES_PIC_URL = 'https://usdawatercolors.nal.usda.gov/download/POM{}/screen'
MD_URL = 'https://usdawatercolors.nal.usda.gov/pom/catalog.xhtml?id=POM{}'
DOWNLOAD_DIR = '../data/images'

START = 1201

def run():
	for counter in range(START, 7585):
		num = str(counter).zfill(8)
		download_pic(num)
		time.sleep(3)
		download_metadata(num)

		time.sleep(10)


def download_metadata(num):
	url = MD_URL.format(num)
	print('Getting %s' % url)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	all_md = soup.findAll("dl", {"class": "defList"})
	if len(all_md) != 1:
		print('ERROR, len(all_md) should be 1, but was %s' % len(all_md))
		exit()

	all_md = all_md[0]
	zipped_md = itertools.zip_longest(all_md.find_all('dt'), all_md.find_all('dd'))
	json_data = dict()

	for dt, dd in zipped_md:
		k = dt.string.replace(':', '')
		v = dd.string if dd.string is not None else dd.a.string
		json_data[k] = v

	filepath = os.path.join(DOWNLOAD_DIR, 'POM{}.json'.format(num))
	with open(filepath, 'w') as f_out:
		f_out.write(json.dumps(json_data, indent=4, sort_keys=True))




def download_pic(num):
	url = PIC_URL.format(num)

	print('Getting %s' % url)
	response = requests.get(url)
	cd = response.headers.get('Content-Disposition')
	if cd is not None:
		filename = cd.split('filename=')[1].replace('"', '')
		filepath = os.path.join(DOWNLOAD_DIR, filename)

		with open(filepath, 'wb') as f_out:
			f_out.write(response.content)
	else:
		print('High resolution picture not available, getting low resolution picture instead')
		download_low_res_pic(num)


# For some reason high resolution downloads are not always available, so get the low resolution
# picture instead
def download_low_res_pic(num):
	url = LOW_RES_PIC_URL.format(num)
	print('Getting %s' % url)
	response = requests.get(url)
	if response.status_code == 200:
		filename = 'POM{}.jpg'.format(num)
		filepath = os.path.join(DOWNLOAD_DIR, filename)

		with open(filepath, 'wb') as f_out:
			f_out.write(response.content)
	else:
		print('ERROR: Unable to find a picture to download for %s' % num)

if __name__ == '__main__':
	run()
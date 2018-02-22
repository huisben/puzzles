# usr/bin/env python3

import io
import os
import requests
from bs4 import BeautifulSoup as bs

import scrapy
#from urllib.request import urlretrieve

# 2010: 6 - 28

BASE_URL = 'https://www.collegepuzzlechallenge.com/'
results = {} # {'puzzle', 'solution'}

def main():
	years = list(range(2010, 2018))

	for year in years:
		url = BASE_URL + 'Archive/' + str(year) + '/Default.aspx'

		resp = requests.get(url)
		
		#print (resp.content)
		print(resp.status_code)
		if(resp.status_code < 400):
			soup = bs(resp.text, 'lxml')

			for link in soup.find_all('a', class_='PdfFile'):
				pdf = link['href']
				print(pdf[6:])
				if 'solution' not in pdf:
					results[pdf[6:]] =  pdf[6:] + '&view=solution'


	# output = open('puzzles.csv','w')

	for k, v in results.items():
		# output.write(BASE_URL+k)
		# output.write(',')
		# output.write(BASE_URL+v)
		# output.write('\n')

		with open('pdfs/'+k.split('=',1)[-1]+'.pdf', 'wb') as file:
			response = requests.get(BASE_URL+k)
			file.write(response.content)

		#urlretrieve(BASE_URL+k,"pdfs/"+k+".pdf")



if __name__ == '__main__':

	main()

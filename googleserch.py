from googleapiclient.discovery import build
import pprint
from lxml import html  
import csv,os,json
import requests
from exceptions import ValueError
from time import sleep


TOKEN = '271351745:AAE_4DTR_vHXXdnEz3Qx08dCdeikOK86Pvo'

my_api_key = 'AIzaSyCwpJ-KXyDpc4M8WRy3KryUwt7J52hyKGQ'

my_cse_id = '006238012235751387519:fgmbxyqr9dc'

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']
	
def QuickParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    while True:
        try:
            doc = html.fromstring(page.content)
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE) 
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            if SALE_PRICE:
                return True
            return False
        except Exception as e:
            print e
			
def AmazonParser(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(url,headers=headers)
    while True:
        try:
            doc = html.fromstring(page.content)
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
 
            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAw_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
 
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None
 
            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE
 
            if page.status_code!=200:
                raise ValueError('captha')
            data = {
                    'NAME':NAME,
                    'SALE_PRICE':SALE_PRICE,
                    'CATEGORY':CATEGORY,
                    'ORIGINAL_PRICE':ORIGINAL_PRICE,
                    'AVAILABILITY':AVAILABILITY,
                    'URL':url,
                    }
 
            return data
        except Exception as e:
            print e	
	
searchWord = 'shoes'

results = google_search(searchWord, my_api_key, my_cse_id, num=10)
	
for u in results:
    if (QuickParser(u['link'])):
        results3 = AmazonParser(u['link'])
        break
if 'results3' in locals():
    print(results3['SALE_PRICE'] + ' '+ results3['URL'])

    
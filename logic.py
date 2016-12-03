import sys
import asyncio
import requests
import telepot
from googleapiclient.discovery import build
import pprint
from lxml import html  
import csv,os,json
import requests
from time import sleep
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space
        
class RecognizeProduct(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(RecognizeProduct, self).__init__(*args, **kwargs)
            
    async def _getImageURL(self, file_id):
        #prepare file
        domain = 'https://api.telegram.org/'
        payload = {'file_id': file_id}
        getFileUrl = domain + 'bot' + TOKEN + '/getFile'
        r = requests.post(getFileUrl, data=payload)
        returnData = r.json()
        FileUrl = domain + 'file/bot' + TOKEN + '/' + returnData['result']['file_path']
        #await self.sender.sendMessage(FileUrl)
        return FileUrl;
        
    async def _getObjectDescription(self, imgURL):
        headers = {"Authorization":"CloudSight qWAN2Kc8W0V5VAUtE2hBLA"}
        payload = {'image_request[remote_image_url]': imgURL, "image_request[locale]": "en-US"}
        url = 'https://api.cloudsightapi.com/image_requests'
        r = requests.post(url, headers=headers, data=payload)
        postReturn = r.json()
        returnToken = postReturn['token'];
        getUrl = 'https://api.cloudsightapi.com/image_responses/' + returnToken;
        status = postReturn['status'];
        while(status=="not completed"):
            await asyncio.sleep(1);
            r = requests.get(getUrl, headers=headers)
            getReturn = r.json()
            status = getReturn['status'];
        object = getReturn['name'];
        return object;
        
    async def _queryAmazon(self, object):
        await self.sender.sendMessage("Querying Amazon...")
        amzn = AmazonSearch()
        result = amzn.search(object)
        return result;

    async def open(self, initial_msg, seed):
        await self.sender.sendMessage('Welcome to buybot, brought to you by Team 1 of Queen\'s University!\n\nSend us an image of what you want to buy, or just know more about!')
        return True  # prevent on_message() from being called on the initial message

    async def on_chat_message(self, msg):
        try: 
            content_type, chat_type, chat_id = telepot.glance(msg)
            if content_type == 'photo':
                await self.sender.sendMessage('We\'ve recieved your image!');
                file_id = msg['photo'][-1]['file_id'];
                imgUrl = await self._getImageURL(file_id);
                object = await self._getObjectDescription(imgUrl);
                await self.sender.sendMessage("Object Description: " + object)
                queryResult = await self._queryAmazon(object);
                message = queryResult['Name'] + '\n' + queryResult['SALE_PRICE'] + '\n' + queryResult['URL']
                await self.sender.sendMessage(message)
                self.close()
        except Exception as e:
            print('caught')
        
    async def on__idle(self, event):
        await self.sender.sendMessage('session expired')
        self.close()
        
def google_search(search_term, cse_id, api_key, **kwargs):
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
            print(e)
            
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
            print(e)
            
            
class AmazonSearch:
    def __init__(self):
        self.my_api_key = 'AIzaSyCwpJ-KXyDpc4M8WRy3KryUwt7J52hyKGQ'
        self.my_cse_id = '006238012235751387519:fgmbxyqr9dc'
   
    def search(self, searchWord):
        results = google_search(searchWord, self.my_cse_id, self.my_api_key, num=10)
        try: 
            results[0]
        except NameError:
            print('The search didn\'t find anything')

        for u in results:
            if (QuickParser(u['link'])):
                return AmazonParser(u['link'])
        return False

TOKEN = "271351745:AAE_4DTR_vHXXdnEz3Qx08dCdeikOK86Pvo"

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, RecognizeProduct, timeout=60),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
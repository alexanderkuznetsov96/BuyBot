import sys
import asyncio
import requests
import telepot
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
                await self.sender.sendMessage(nouns);
        except Exception as e:
            print('caught')
        
    async def on__idle(self, event):
        await self.sender.sendMessage('session expired')
        self.close()


TOKEN = "271351745:AAE_4DTR_vHXXdnEz3Qx08dCdeikOK86Pvo"

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, RecognizeProduct, timeout=60),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
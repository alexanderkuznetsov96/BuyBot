import telepot
import requests
#from amazonproduct import API
from pprint import pprint
TOKEN = '271351745:AAE_4DTR_vHXXdnEz3Qx08dCdeikOK86Pvo'
bot = telepot.Bot(TOKEN)


updates =  bot.getUpdates()
if ‘photo’ in updates[0][‘message’]:
	try: 
		var1 = 'https://api.telegram.org/bot<' + TOKEN + '>' + updates[0]['message']['photo'][0]['file_path']
	except KeyError, e: 
		print ('No image found in picture message’)
else:
	print('That\'s not a photo')





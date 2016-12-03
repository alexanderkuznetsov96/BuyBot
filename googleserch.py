from googleapiclient.discovery import build
import pprint

TOKEN = '271351745:AAE_4DTR_vHXXdnEz3Qx08dCdeikOK86Pvo'

my_api_key = 'AIzaSyCwpJ-KXyDpc4M8WRy3KryUwt7J52hyKGQ'

my_cse_id = '006238012235751387519:fgmbxyqr9dc'

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

results = google_search(
    'shoes', my_api_key, my_cse_id, num=10)

for result in results:
    pprint.pprint(result)


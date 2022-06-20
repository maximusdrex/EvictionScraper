import requests
import urllib3

SEARCH_URL = "https://portal.cmcoh.org/CMCPORTAL/SmartSearch/SmartSearch/SmartSearch"


s = requests.session()

s.get('https://portal.cmcoh.org/CMCPORTAL/Home/Dashboard/29')

#r1= s.get('https://portal.cmcoh.org/CMCPORTAL/')
#print(r1.cookies)

search_data = {'Host': 'portal.cmcoh.org',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate, br',
'Content-Type': 'application/x-www-form-urlencoded',
'Origin': 'https://portal.cmcoh.org',
'Connection': 'keep-alive',
'Referer': 'https://portal.cmcoh.org/CMCPORTAL/Home/Dashboard/29',
}
try:
    r = s.post(SEARCH_URL, headers=search_data, data={'caseCriteria.SearchCriteria':'2010-CVG-0000*'}, timeout=3)
except (requests.ReadTimeout):
    print("no response")



#f = open("response.html", "w")
#f.write(r1.text)
#f.close()
print(r.status_code)
print(s.cookies)
print(r.history[0].headers["Location"])

GET_RESULTS="https://portal.cmcoh.org/CMCPORTAL/SmartSearch/SmartSearchResults"
try:
    r2 = s.get(GET_RESULTS, timeout=3, cookies=s.cookies)
except (requests.ReadTimeout):
    print("no response")

print(r2.status_code)
print(r2.text)

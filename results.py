import requests
import urllib3

GET_RESULTS="https://portal.cmcoh.org/CMCPORTAL/SmartSearch/SmartSearchResults"


s = requests.session()

heads = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Accept":"*/*",
    "Accept-Language":"en-US,en;q=0.5",
    "Accept-Encoding":"gzip, deflate, br",
    "Connection":"keep-alive",
    "Referer":"https://portal.cmcoh.org/CMCPORTAL/Home/WorkspaceMode?p=0",
    "Cookie":"ASP.NET_SessionId=ihyzbjkwc2u4wfibvzhcfjaf; SmartSearchCriteria=Criteria=2d1c40d2-4a3b-46e5-be42-fc278fd549ed"
}

r2 = s.get(GET_RESULTS, timeout=5, headers=heads)

print(r2.text)
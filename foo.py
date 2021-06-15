import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time


ua = UserAgent()
hdr = {'User-Agent': ua.random,
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}
req = requests.get("https://www.amazon.com/s?bbn=11444071011&rh=n%3A3375251%2Cn%3A%213375301%2Cn%3A10971181011%2Cn%3A11444071011%2Cp_n_feature_six_browse-bin%3A11463658011%2Cp_6%3AATVPDKIKX0DER&lo=image&pf_rd_i=11444071011&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=057239e1-130a-432a-a061-57834f670c79&pf_rd_r=AG1ZA39AWQT6B7HMSJTD&pf_rd_s=merchandised-search-2&pf_rd_t=101&qid=1529611956&ref=s9_acss_bw_cg_sports_3c1_w",headers=hdr)
soup = BeautifulSoup(req.text,"html.parser")
# print(soup)
next = soup.find('li','a-last')
b= next.find('a')
print(b['href'])
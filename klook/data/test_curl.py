from curl_cffi import requests
from bs4 import BeautifulSoup
import time

def test():
    url = "https://www.klook.com/ko/activity/7955-hanbok-rental-voucher-at-kyeonbokgung-store-in-hanboknam-seoul/"
    # Try different impersonates like chrome120, safari15_3, edge101
    try:
        response = requests.get(url, impersonate="chrome120")
        print("Status code:", response.status_code)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Title:", soup.title.string if soup.title else "No Title")
        
        texts = [p.get_text() for p in soup.find_all(['p', 'h1', 'h2'])][:5]
        print("Texts:", texts)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()

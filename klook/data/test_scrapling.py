from scrapling import StealthyFetcher
import time

def test():
    url = "https://www.klook.com/ko/activity/7955-hanbok-rental-voucher-at-kyeonbokgung-store-in-hanboknam-seoul/"
    try:
        fetcher = StealthyFetcher()
        # Fetch the page
        page = fetcher.fetch(url)
        print("Title:", page.title)
        
        # Scrapling Selector has `css` or similar methods. Let's just dump some texts.
        print("Texts:", page.css('p').text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()

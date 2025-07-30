import requests
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
from selenium.webdriver.chrome.service import Service


def getdata(url):
    try:
        r = requests.get(url)
        return r.text
    except requests.RequestException as e:
        print(f"Request to {url} failed: {e}")
        return None


def crawl_website(website):
    print("Website Crawling Started:", website)
    web_content = []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    def crawl_page(url):
        if url in visited_urls:
            return
        visited_urls.add(url)

        driver.get(url)
        page_source = driver.page_source
        parsed_html = BeautifulSoup(page_source, "html.parser")

        for link in parsed_html.find_all("a", href=True):
            href = link["href"]
            absolute_url = urllib.parse.urljoin(url, href)
            if absolute_url.startswith(website) and absolute_url not in visited_urls:
                crawl_page(absolute_url)

        web_content.append({"url": url, "html_data": getdata(url)})

    visited_urls = set()
    crawl_page(website)

    driver.quit()
    print("Website Crawling Finished:", website)
    return web_content

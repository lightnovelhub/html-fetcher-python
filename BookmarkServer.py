#!/usr/bin/env python3
#
# A *bookmark server* or URI shortener.
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import http.server
import os
from urllib.parse import unquote
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
memory = {}
chrome_options = Options()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
browser = webdriver.Chrome(executable_path=os.environ.get(
    "CHROMEDRIVER_PATH"), chrome_options=chrome_options)


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."


class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            delay = 3  # seconds
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            query = urlparse(self.path).query
            query_components = dict(qc.split("=") for qc in query.split("&"))
            searchQuery = query_components["query"]
            myquery = "https://www.y2mate.com/youtube-mp3/" + searchQuery
            browser.get(myquery)
            WebDriverWait(browser, delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'caption')))
            l = browser.find_element(
                By.CSS_SELECTOR, "#result > div > div.col-xs-12.col-sm-7.col-md-8 > div > div > div.btn-group.inline.p-r-md > button.btn.btn-default.dropdown-toggle")
            l.click()
            browser.find_element(By.CSS_SELECTOR, "#result > div > div.col-xs-12.col-sm-7.col-md-8 > div > div > div.btn-group.inline.p-r-md.open > div > div.panel-body.panel_file_type > div.col-xs-5.p-t-md > ul > li:nth-child(1) > a").click()
            browser.find_element(By.CSS_SELECTOR, "#process_mp3").click()
            WebDriverWait(browser, delay).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#process-result > div')))
            url = browser.find_element(
                By.CSS_SELECTOR, "#process-result > div > a").get_attribute("href")
            self.wfile.write(bytes(url, "utf-8"))
        except TimeoutException:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            print("Loading took too much time!")
            self.wfile.write(bytes("Failed", "utf-8"))


if __name__ == '__main__':
    server_address = ('', int(os.environ.get('PORT', '8000')))
    httpd = ThreadHTTPServer(server_address, Shortener)
    httpd.serve_forever()

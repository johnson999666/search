
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import requests
import html
import re
from flask import Flask, render_template, request, redirect, url_for
import textwrap

app = Flask(__name__)

class MediumScraper:
    def __init__(self, driver_path, search_query):
        self.driver_path = driver_path
        self.search_query = search_query
        self.driver = None

    def start(self):
        global flag
        self.driver = webdriver.Chrome(self.driver_path)
        self.driver.get(f"https://medium.com/search?q={self.search_query}")
        flag = True

    def scrape(self):
        if not self.driver:
            raise Exception("Webdriver is not initialized. Call start() first.")

        # Find all boxes with class "bf l"
        boxes = self.driver.find_elements(By.CSS_SELECTOR, ".bf.l")

        # Loop through each box
        for box in boxes:
            # Check if box contains text "Member-only"
            if "Member-only" in box.text:
                print('scanning')
            else:
                # Find the heading (h2 tag) in the box
                heading = box.find_element(By.TAG_NAME, "h2")
                if heading.is_displayed() and heading.is_enabled():
                    heading.click()
                    time.sleep(2)
                    break

    def soup(self):
        # Click on the heading
        url = self.driver.current_url

        response = requests.get(url)
        print(url)

        # Use response.text instead of response.content to get the HTML content as a string
        soup = BeautifulSoup(response.text, "html.parser")

        # tag = soup.title.get_text()
        art = soup.find('article')
        text = html.unescape(art.text)
        text = re.sub(r"http[s]?://\S+", "", text)
        text = re.sub(r"\s+", " ", text)

        # Make the text inside each code tag bold
        for code_tag in art.find_all('article'):
            code_tag.wrap(soup.new_tag('b'))

        art = soup.prettify()
        art = soup.get_text()
        art = str(art)
        print(textwrap.fill(art))
        return art

        # art = ' '.join(art.stripped_strings)

        # Create a string with HTML tags to format the article text
        # formatted_text = f"<h1>{tag}</h1>\n<p>{art}</p>"



    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        print("Test completed.")


is_flag_set = False

def set_flag():
    global is_flag_set
    is_flag_set = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/')
def search():
    query = request.args.get('query')
    if query:
        set_flag()  # Set the flag if a search query was submitted
        scraper = MediumScraper("chromedriver", query)
        scraper.start()
        scraper.scrape()
        article = scraper.soup()
        scraper.stop()
        return render_template('index.html', article=article)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')

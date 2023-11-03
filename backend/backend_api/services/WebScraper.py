from celery import Celery
from ...utils.databases import SQLDB
import os
from ..models import URL_table
import requests
from bs4 import BeautifulSoup
from sqlalchemy import text
import logging

celery = Celery('web_scraper', broker='pyamqp://guest@rabbitmq//', backend='rpc://')

logging.basicConfig(filename='web_scraper.log', level=logging.INFO)

class WebScraper:

    sqldb = SQLDB(
        user=os.getenv('SQLDB_USER'),
        password=os.getenv('SQLDB_PASS'),
        host="db",
        port="5432",
        dbname="web_scraper_db",
        models=[URL_table],
    )

    @celery.task(bind=True)
    def scrape_webpage(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            url_data = URL_table(
                id=self.request.id,
                title=soup.title.string,
                text=soup.get_text(),
                links=[link.get('href') for link in soup.find_all('a')],
                images=[img.get('src') for img in soup.find_all('img')],
            )

            WebScraper.sqldb.add_data([url_data])

            query = f"SELECT * FROM url_table WHERE id = '{self.request.id}'"
            response = WebScraper.sqldb.query(text(query))
            response =str(response)

        except Exception as e:
            response = f"Unable to scrape data and/or add to database. Error: {e}"

        return response
    
from threading import Thread
from bs4 import BeautifulSoup
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk import clean_html
from urllib.request import Request, urlopen

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        self.fdist = FreqDist()

        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
                req = Request(scraped_url)
                html_page = urlopen(req)
                soup = BeautifulSoup(html_page, 'html.parser')
                for data in soup(['style', 'script']):
                    data.decompose()
                self.addFdist(' '.join(soup.stripped_strings))
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        print(self.FreqDist.most_common([50]))

    def addFdist(self,page):
        tokenizer = RegexpTokenizer("^[a-z0-9'-]*$")
        for token in tokenizer.tokenize(page):
            self.fdist[token] += 1
import requests
from bs4 import BeautifulSoup

req = requests.get("https://www.ics.uci.edu/~cs224/")
soup = BeautifulSoup(req.content, "html.parser")


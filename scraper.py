import re
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import time 
import tokenize
from bs4 import BeautifulSoup


maxCount = 0 # keep track of the longest page in terms of the number of words
maxUrl = "" # keep track of the url of the longest page


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    #TODO: Fix crawler trap
    
    ret = set()
    

    if resp.status == 200:
        # code citation: https://pythonprogramminglanguage.com/get-links-from-webpage/
        req = Request(url)
        html_page = urlopen(req)
        soup = BeautifulSoup(html_page, "lxml")
        
################ added counter the longest page in terms of the number of words and related URL

        global maxCount
        global maxUrl
        if (maxCount < len(website_content)):
            maxCount = len(website_content)
            maxUrl = resp.url #??? url or resp.url????
            
        print(maxCount)
        print("\n\n\n")
        print(maxUrl)
###################

        for link in soup.findAll('a'):
            #eliminate the fragment of the url.
            url = link.get('href')
            if url:
                index = url.find("#")
                if index != -1:
                    url = url[:index]
                ret.add(url)
            #time.sleep(0.5)
    else:
        print(resp.error)
    return list(ret)


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # Requirements:
    # - filter out urls that do not point to webpages (add more in the pattern)
    # - pdf files that do not end in .pdf
    # https://stackoverflow.com/questions/312230/proper-mime-media-type-for-pdf-files
    # - low information?
    # - large files
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # make sure is in the domain of initial domains
        if parsed.netloc not in set(["www.ics.uci.edu","www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu"]):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

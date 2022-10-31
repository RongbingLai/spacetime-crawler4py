import re
from urllib.parse import urlparse 
import tokenize
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer


# keep track of the longest page in terms of the number of words
maxCount = 0 
# keep track of the url of the longest page
maxUrl = "" 
# store the subdomains under ics.uci.edu
ics_subdomains = defaultdict(int)
# record bad urls that we do not want to crawl
bad_urls = set()
# record the total unique_pages
unique_pages = 0
# record scraped urls
scraped_urls = set()

def scraper(url, resp):
    links = extract_next_links(url, resp)
    result = list()
    for link in links:
        if is_valid(link):
            # count unique pages
            unique_pages += 1
            result.append(link)
            
    return result

#2. find the longest page
def countMax(soup, url):
    #added counter the longest page in terms of the number of words and related URL
    content = soup.get_text()
    #print(content)
    website_content = re.split(r'[^0-9a-zA-Z]', content) #remove "\n"?

    global maxCount
    global maxUrl
    if maxCount < len(website_content):
        maxCount = len(website_content)
        maxUrl = url #??? url or resp.url????

    # print(maxCount)
    # print(maxUrl)
    return len(website_content)

# tokenize text from the page
def scrape_text(soup):
    '''
    Scrape the texts and strip them, forming a paragraph and store them into the txt
    '''
    content = soup.get_text(strip=True)
    f = open("tokens.txt", "w")
    f.write(content)
    f.close()

def top_50_tokens():
    '''
    Use the stopwords file to generate a stopwords set. Parse the token txt file and add lowercase
    of them into a freq dict only if they are not stopwords. Finally returns the top 50 elements
    '''
    g = open("stopwords.txt", "r")
    lines = g.readlines()
    g.close()
    stopwords = set()
    for line in lines:
        stopwords.add(line.strip())
    
    f = open("tokens.txt", "r")
    lines = f.readlines()
    f.close()
    fdist = FreqDist()#keep track of the token frequencies
    tokenizer = RegexpTokenizer("^[a-z0-9'-]*$")
    for line in lines:
        line = line.strip()
        for token in tokenizer.tokenize(line):
            if token.lower() not in stopwords:
                fdist[token.lower()] += 1

    print(fdist.most_common(50))
    return fdist.most_common(50)
    

    
def scraper(url, resp):
    links = extract_next_links(url, resp)
    result = list()
    for link in links:
        if is_valid(link):
            unique_pages += 1
            result.append(link)
            
    return result


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
    try:
        if resp.status == 200 and is_valid(resp.url):
            soup = BeautifulSoup(resp.raw_response, "html.parser")
            
            currentLength = countMax(soup, resp.url)

            #Low information: if the words in the url is fewer than 20, ignore the page.
            if currentLength < 20:
                return list()

            scrape_text(soup)
            
            for link in soup.findAll('a'):
                raw_url = link.get('href')

                #check if the url is a relative url not starting with http
                # raw_url = make_abs_url(url, raw_url)

                #eliminate the fragment of the url.
                if raw_url:
                    index = raw_url.find("#")
                    if index != -1:
                        raw_url = raw_url[:index]
                    ret.add(raw_url)
                
                #Detect and avoid crawler traps
                if raw_url in scraped_urls:
                    print("repeated")
                else:
                    scraped_urls.add(raw_url)
                    ret.add(raw_url)
        else:
            bad_urls.add(resp.url)
    except Exception as e:
        bad_urls.add(resp.url)
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
        #Url too short, not a valid url
        if len(url) < 6:
            return False

        if url in bad_urls:
            return False

        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False

        #record subdomains
        if re.match(r"(.+)\.ics\.uci\.edu(.*)", parsed.netloc.lower()):
            ics_subdomains[parsed.netloc] += 1

        # make sure is in the domain of initial domains
        if not re.match(
            r"(.*)\.ics\.uci\.edu(.*)"
            + r"|(.*)\.cs\.uci\.edu(.*)"
            + r"|(.*)\.informatics\.uci\.edu(.*)"
            + r"|(.*)\.stat\.uci\.edu(.*)"
            , parsed.netloc.lower()):
            return False

        # added odc, java, py, c, txt, ss, scm
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|txt|ss|scm"
            + r"|thmx|mso|arff|rtf|jar|csv|odc|py|java|c"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def output():
    print("unique_pages: ", unique_pages)
    print("longest page is " + maxUrl + "with " + str(maxCount) + "words")
    print(scraper.ics_subdomains)
    top_50_tokens()
    
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
bad_urls = set("https://wics.ics.uci.edu/events")
# record scraped urls
scraped_urls = set()

# open the stopwords file
with open("stopwords.txt", "r", encoding='utf8', errors='ignore') as openerS:
    # each stop word is separated by a new line character
    stopwords_list = openerS.read().split("\n")    

def scraper(url, resp):
    links = extract_next_links(url, resp)
    result = list()
    for link in links:
        if is_valid(link):
            result.append(link)
    return result

#2. find the longest page
def countMax(soup, url):
    #added counter the longest page in terms of the number of words and related URL
    
    
    content = soup.text
    #print(content)
    website_content = re.split(r'[^0-9a-zA-Z]', content) #remove "\n"?

    global maxCount
    global maxUrl
    count = 0
    
    for words in website_content:
        if words not in stopwords_list:
            count += 1
    
    if maxCount < count:
        maxCount = count
        maxUrl = url
        with open("longest_page.txt", "w", encoding='utf8', errors='ignore') as openerW:
            openerW.write("The longest page in terms of the number of words: \n")
            openerW.write(maxUrl)
            openerW.write("\nWords in that page: \n")
            openerW.write(str(maxCount))

    # print(maxCount)
    # print(maxUrl)
    return count

# tokenize text from the page
def scrape_text(soup):
    '''
    Scrape the texts and strip them, forming a paragraph and store them into the txt
    '''
    #content = soup.get_text(strip=True)
    content = soup.text.strip()
    f = open("tokens.txt", "a+", encoding="utf-8")
    f.write(content)
    f.write('\n')
    f.close()

def top_50_tokens():
    '''
    Use the stopwords file to generate a stopwords set. Parse the token txt file and add lowercase
    of them into a freq dict only if they are not stopwords. Finally returns the top 50 elements
    '''
    g = open("stopwords.txt", "r", encoding="utf-8")
    lines = g.readlines()
    g.close()
    stopwords = set()
    for line in lines:
        stopwords.add(line.strip())
    f = open("tokens.txt", "r", encoding="utf-8")
    lines = f.readlines()
    f.close()
    fdist = FreqDist()#keep track of the token frequencies
    
    tokenizer = RegexpTokenizer("^[A-Za-z]+['-]?[A-Za-z]+")
    for line in lines:
        line = line.strip()
        for token in tokenizer.tokenize(line):
            if token.lower() not in stopwords:
                fdist[token.lower()] += 1

    print(fdist.most_common(50))
    return fdist.most_common(50)
    
#Add URL to 'Good' list
def add_good_url(url):
    if url in scraped_urls:
        return False
    scraped_urls.add(url)
    try:
        file = open("scraped_url.txt", "a+", encoding="utf-8")
        file.write(url+"\n")
        file.close()
    except:
        pass
    # print("GOOD (",len(scraped_urls),"):", url)
    return True

#Add URL to 'Bad' set
def add_bad_url(url):
    bad_urls.add(url)
    try:
        file = open("bad_url.txt", "a+", encoding="utf-8")
        file.write(url+"\n")
        file.close()
    except:
        pass
    # print("BAD (",len(bad_urls),"):", url)
    return True

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

        #if the type of the Content of the page is pdf, make it invalid
        #DEBUG!
        #if resp.status == 200 and is_valid(resp.url):
        if resp.status == 200:
            if 'pdf' in resp.raw_response.headers['Content-Type']:
                add_bad_url(resp.url)
                return list()

            # web_type = resp.raw_response.headers['Link'].split(";")[3].split(",")[0]
            # if web_type != ' type="application/json"':
            #     raise
                
            soup = BeautifulSoup(resp.raw_response.content, "html.parser")
            
            currentLength = countMax(soup, resp.url)

            #Low information: if the words in the url is fewer than 50, ignore the page.
            if currentLength < 50:
                return list()
            else:
                scrape_text(soup)
            
            #Because 'url' was fetched successfully and it's a good page, add 'url' to a set now.
            add_good_url(url)

            for link in soup.findAll('a'):
                raw_url = link.get('href')

                #check if the url is a relative url not starting with http
                # raw_url = make_abs_url(url, raw_url)

                #eliminate the fragment of the url.
                if raw_url and is_valid(raw_url):
                    index = raw_url.find("#")
                    if index != -1:
                        raw_url = raw_url[:index]
                    #ret.add(raw_url)
                else:
                    add_bad_url(raw_url)
                
                #Detect and avoid crawler traps
                if raw_url not in scraped_urls:
                    ret.add(raw_url)
        else:
            add_bad_url(resp.url)
    except Exception as e:
        print(e)
        add_bad_url(resp.url)
    return list(ret)


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # DEAL WITH PDF?!

    parsed = urlparse(url)
    try:
        #Url too short, not a valid url
        if not url:
            return False
        
        if len(url) < 6 or url in bad_urls:
            return False

        if parsed.scheme not in set(["http", "https"]):
            return False

        #record subdomains
        if ".ics.uci.edu" in parsed.netloc.lower() and parsed.netloc.lower() != "www.ics.uci.edu":
            ics_subdomains[parsed.netloc.lower()] += 1

        # make sure is in the domain of initial domains
        if not re.match(
            r"(.*)\.ics\.uci\.edu(.*)"
            + r"|(.*)\.cs\.uci\.edu(.*)"
            + r"|(.*)\.informatics\.uci\.edu(.*)"
            + r"|(.*)\.stat\.uci\.edu(.*)"
            , parsed.netloc.lower()):
            return False

        # added odc, java, py, c, txt, ss, scm, ppsx
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv|odc|py|java|c"
            + r"|sql|apk|img|war|r|txt|ss|scm|ppsx|bib"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def output():
    print("unique_pages: ", len(scraped_urls))
    print("longest page is " + maxUrl + " with " + str(maxCount) + " words")

    f = open("result.txt", "a+", encoding="utf-8")
    f.write("unique_pages: " + str(len(scraped_urls)) + "\n")
    f.write("longest page is " + maxUrl + " with " + str(maxCount) + " words" + "\n")
    f.write("ICS Subdomains: \n")
    for key in sorted(ics_subdomains):
        print(key + ": " + str(ics_subdomains[key]))
        f.write(key + ": " + str(ics_subdomains[key]) + "\n")
    tokens = top_50_tokens()
    f.write(str(tokens))
    f.close()
    
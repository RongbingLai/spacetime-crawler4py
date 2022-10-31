import scraper
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
import nltk
if __name__ == "__main__":
    # nltk.download('punkt')
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
    tokenizer = RegexpTokenizer("\w+|\'\-[\d\.]+|\S+")
    for line in lines:
        line = line.strip()
        for token in tokenizer.tokenize(line):
            if token.lower() not in stopwords:
                fdist[token.lower()] += 1
    print(fdist.most_common(3))

# Web Crawler
# imports
import json
from http import client
import requests
from bs4 import BeautifulSoup
import pymongo

class Crawler():
    # connect to cloud mongo
    connect_uri = 'mongodb+srv://dbUser:dbUser2020@schwartzschwanengine.zbkl3.mongodb.net/search?retryWrites=true&w=majority'
    client = pymongo.MongoClient(connect_uri)

    # create db client
    db = client.search

    # search results storage
    search_results = []

    # crawl domain
    def crawl(self, url, depth):
        # try to perform HTTP GET request
        try:
            print('Crawling url: "%s" at depth: %d' % (url, depth))
            response = requests.get(url, headers={'user-agent': 'Schwarz-Schwan-Search'})

        # run again otherwise
        except:
            print('Failed to perform HTTP GET request on "%s"\n' % url)


        # parse content
        content = BeautifulSoup(response.text, 'lxml')

        # try to extract page title and description
        try:
            title = content.find('title').text
            description = ''

            for tag in content.findAll():
                if tag.name == 'p':
                    description += tag.text.strip().replace('\n', '')

        # return otherwise
        except:
            return

        # store the result structured
        result = {
            'url': url,
            'title': title,
            'description': description
        }

        search_results = self.db.search_results
        search_results.insert_one(result)
        search_results.create_index([
            ('url', pymongo.TEXT),
            ('title', pymongo.TEXT),
            ('description', pymongo.TEXT)
        ], name='search_results', default_language='english')

        # store the result
        #self.search_results.append(result)

        # return when depth is exhausted
        if depth == 0:
            return

            # extract all the available links on the page
        links = content.findAll('a')

        # loop over links
        for link in links:
            # try to crawl links recursively
            try:
                # use only links starting with 'http'
                if 'http' in link['href']:
                    self.crawl(link['href'], depth - 1)

            # ignore internal links
            except KeyError:
                pass
        # close connection
        client.close()

crawler = Crawler()
crawler.crawl('https://www.stackoverflow.com', 5)





import facebook
import requests
import re
import pprint
import pickle
from sets import Set
from requests.exceptions import ConnectionError
from urllib2 import URLError
from facebook import GraphAPIError

MEME_PAGE_LIKES_MINIMUM = 10000
MEME_PAGE_LIKES_MAXIMUM = 20000

def getLikes(meme_page_id, graph):
    likes = 0
    gotten = False
    while not gotten:
        try:
            likes = graph.get_object(id=meme_page_id)['likes']
            gotten = True
        except URLError:
            print "Trumped get page likes"
        except GraphAPIError:
            gotten = True
    return likes

def getPosts(nextPage):
    gotten = False
    posts = None
    while not gotten:
        try:
            posts = requests.get(nextPage).json()
            gotten = True
        except ConnectionError:
            print "Trumped getting another page of posts"
    return posts

def getLinksFromPosts(posts, graph):
    links = Set()
    if 'data' in posts:
        for post in posts['data']:
            if 'link' in post.keys():
                m = re.search('(?<=https://www.facebook.com/)[a-z-_A-Z0-9]+', post['link'])
                if m is not None:
                    meme_page_id = m.group(0)
                    meme_page_likes = getLikes(meme_page_id, graph)
                    if meme_page_id not in links and meme_page_id != 'photo':
                        if meme_page_likes > MEME_PAGE_LIKES_MINIMUM and meme_page_likes < MEME_PAGE_LIKES_MAXIMUM:
                            links.add(meme_page_id)
        print "Got " + str(len(links))
    else:
        print "No posts"
    return links

def getMemeRefs(meme_page, graph, depth, pages):
    if depth == 0: return
    gotten = False
    while not gotten:
        try:
            print meme_page
            posts = graph.get_connections(id=meme_page,connection_name='posts')
            gotten = True
        except URLError:
            print "Trumped getting first round of posts"
        except GraphAPIError:
            print "Error while getting posts for " + meme_page + " - may not exist bruh"
    page = 1
    links = Set()
    if 'data' in posts:
        while(posts['data']):
            print "On page: " + str(page)
            try:
                posts = getPosts(posts['paging']['next'])
                postLinks = getLinksFromPosts(posts, graph)
                if postLinks != None:
                    if len(postLinks) > 0:
                        links.update(postLinks)
            except KeyError:
                print "Key Error"
            page += 1
            if links != None:
                print "Got " + str(len(links)) + " from " +  meme_page + " so far."
    print "Got " + str(len(links)) + " from " +  meme_page
    for link in links:
        pages.add(link)
        getMemeRefs(link, graph, depth - 1, pages)



pp = pprint.PrettyPrinter(indent=4)
access_token='CAACEdEose0cBAGYA2OVsbSnjnQHrCRjSdo90xZBZCRMRGXRAa7he0LskpzsSFkOx8KJEhq4qEPuKT4zL9TkGMbK9EjwJHCMHXasp5wBPudgyIj8JediLdtp3vz2wXW9ihOZAyCwkUEX0iZAF5nVSy5LBlgZBYgSWJdjsZBzsBMrA4eAjzsc7DtAMHgCii6gcKi9ZCYP4LXwaorFYuZA0tEgu1KZBtSLhBQaboeIXsqZC6zYgZDZD'
version='2.3'
meme_page='500842393399164'

graph = facebook.GraphAPI(access_token, version)
graph.timeout = 30000


links = Set()

depth = 3
getMemeRefs(meme_page, graph, depth, links)

meme_pages = []

print "Got " + str(len(links)) + " meme paj."

for meme_page_id in links:
    meme_pages.append([str(meme_page_id), getLikes(meme_page_id, graph)])

pp.pprint(meme_pages)

with open(meme_page + "_" + str(depth), 'wb') as f:
    pickle.dump(meme_pages, f)

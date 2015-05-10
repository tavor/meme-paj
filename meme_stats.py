import pickle
import copy
import pprint

pp = pprint.PrettyPrinter(indent=4)
meme_page = 'humanity3suckdicks'

links = None
with open(meme_page, 'rb') as f:
    links = pickle.load(f)


sort = False
while sort == False:
    sort = True
    for page in range(len(links) - 1):
        if links[page][1] < links[page + 1][1]:
            temp = copy.deepcopy(links[page])

            links[page] = copy.deepcopy(links[page + 1])

            links[page + 1] = temp

            sort = False

for link in links:
    print link

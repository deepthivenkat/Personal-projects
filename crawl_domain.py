import urllib2
from urllib2 import HTTPError
from bs4 import BeautifulSoup as BS
from threading import Timer,Thread,Event

root = "http://www.cc.gatech.edu/"
DISALLOW = []
global Total_url_crawled, Total_url_count, No_of_Duplicates, time_now
Total_url_crawled = 0
No_of_Duplicates = 0
Total_url_count = 0
time_now = 0

HashMap = None


class HashMap:
    def __init__(self):
        self.size = 26
        self.map = [None] * self.size

    def get_hash(self, value):
        hash = 0
        for char in str(value):
            hash += ord(char)
        return [hash % self.size, hash]

    def add_to_hash(self, value):
        keys = self.get_hash(value)
        list_index = keys[0]
        hash_key = keys[1]

        hash_entry = [hash_key, value]

        if self.map[list_index] is None:
            self.map[list_index] = list([hash_entry])
            return True
        else:
            for entry in self.map[list_index]:
                if entry[0] == hash_key and entry[1] == value:
                    global No_of_Duplicates
                    No_of_Duplicates += 1
                    return False
                elif entry[0] == hash_key and entry[1] != value:
                    print 'Appending to existing key', entry, value
                    entry.append(value)
                    return True
            print 'Adding new entry to', list_index, hash_entry
            self.map[list_index].append(hash_entry)
            return True

    def lookup(self, value):
        key_list = self.get_hash(value)
        try:
            if self.map[key_list[0]]:
                for entry in self.map[key_list[0]]:
                    if entry[0] == key_list[1]:
                        return entry
            return None
        except IndexError:
            print 'Error in look up.'

    def print_hash(self):
        for item in self.map:
            if item is not None:
                print item


class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

def printer():
    global time_now
    time_now += 20
    print 'Total number of URLs : ', Total_url_count
    print 'No of Duplicates Avoided :', No_of_Duplicates
    print 'No of url crawled vs time : %s in %s seconds'%(Total_url_crawled, time_now)




def request_data(page_url):
    req = urllib2.Request(page_url)
    try:
        bzresponse = urllib2.urlopen(req, timeout=240)
    except HTTPError as e:
        print 'Ignoring %s since there is %s error' % (page_url, e)
        return False
    else:
        return bzresponse.read()


def get_links(curr_url, html):
    xml_page = BS(html, 'lxml')
    links = xml_page.find_all('a')
    urls = []
    global Total_url_count
    Total_url_count += len(links)
    for link in links:
        if link.has_attr('href'):
            urls.append(link['href'])
    urls.sort()


    for index, url in enumerate(urls):
        if url.startswith("http://") or url.startswith("https://") or url.startswith("www."):
            pass
        else:
            if '#' in curr_url and url.startswith('#'):
                urls[index] = curr_url.split('#')[0] + url
            elif '#' in curr_url and not url.startswith('#'):
                curr_url = curr_url.split('#')[0]
                print "hi"
                print curr_url
            if url.startswith('/'):
                urls[index] = root + url[1:]
            else:
                urls[index] = root + url
    keywords = ['student', 'professor', 'dean', 'academic', 'courses', 'class', 'bachelors', 'masters', 'phd']

    def find_keywords(url):
        match = []
        for keyword in keywords:
            if keyword in url:
                match.append(url)
        return match

    relevant_urls = filter(find_keywords, urls)
    for prohibited in DISALLOW:
        allowed_urls = [url for url in relevant_urls if prohibited not in url]


    print "exit"
    return allowed_urls



def crawl(url):
    url_added = h.add_to_hash(url)
    if url_added:
        page_html = request_data(url)
        if page_html:
            urls_from_page = get_links(url, page_html)
            urls_from_page.sort()
            urls_from_page = list(set(urls_from_page))

            global Total_url_crawled
            Total_url_crawled += 1
            print 'Currently crawling %s'%(url)
            with open("PageData.txt", "a") as text_file:
                text_file.write("URL:" + url + "/n" + page_html)
        try:
            urls_from_page = map(append_slash, urls_from_page)
            print urls_from_page
            for child_url in urls_from_page:
                crawl(child_url)
        except UnboundLocalError:
            pass
            print 'Html page of url not defined since base url is already in hash table'

def append_slash(item):
    if item.endswith('/'):
        return item
    else:
        return item + '/'

def main():
    t = perpetualTimer(20,printer)
    t.start()
    root = "http://www.cc.gatech.edu/"
    get_disallowed_links = request_data(root + 'robots.txt')
    uncrawl = [path.strip('\n').lstrip() for path in get_disallowed_links.split('Disallow:') if '\nAllow:' not in path]
    uncrawl.sort()
    global DISALLOW
    DISALLOW = uncrawl
    global h
    h = HashMap()
    crawl(root)


if __name__ == '__main__':
    main()

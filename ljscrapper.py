import requests
from bs4 import BeautifulSoup
import re
import jinja2
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Ignore lack of ssl
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Blog:
    def __init__(self, blogname=None):
        self.blogname = "" if blogname==None else blogname
        self.articles = dict()
        self.url_template = "https://{}.livejournal.com/{}.html"
        self.last_updated = None
        self.size = None
        
        # Non-LJ blogs dont support SSL
        self.ssl_enabled = False if "." in self.blogname else True
        
        # LJ service next/prev redirection
        self.url_prev_template = "https://www.livejournal.com/go.bml?journal={}&itemid={}&dir=prev"
        self.url_next_template = "https://www.livejournal.com/go.bml?journal={}&itemid={}&dir=next"
        
        # titles are "title: blogname - livejournal"
        self.shift = 16 + len(self.blogname)


    def parse(self, id):
        '''
        Parse a page
        '''
        cookies_jar = requests.cookies.RequestsCookieJar()
        
        # Enable default html via cookies
        cookies_jar.set('prop_opt_readability', '1', domain='.livejournal.com', path='/')
        #Parse adult pages too
        cookies_jar.set('adult_explicit', '1', domain='livejournal.com', path='/')
        
        the_url = self.url_template.format(self.blogname, id)
        page = requests.get(the_url, cookies=cookies_jar, verify=self.ssl_enabled)
        data = page.text
        soup = BeautifulSoup(data, features="html.parser")
        if page.status_code == 404:
            title = soup.title.string.strip()
            date = "NA"
            tags = ""
            self.articles[str(id)] = {"title": title, "date": date, "tags": tags}
            return "{} {} {}".format(id, date, title, tags)

        title = soup.title.string[:-self.shift].rstrip()
        date = soup.findAll("time", {"class": "b-singlepost-author-date published dt-published"})
        if not len(date):
            date = soup.findAll("p", {"class": "aentry-head__date"})[0].getText().strip()
            date = datetime.datetime.strptime(date, "%B %d %Y, %H:%M")
            date = date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date = date[0].getText()
        tags = soup.findAll("span", {"class": "b-singlepost-tags-items"})
        if len(tags):
            tags = list(map(str.strip, tags[0].getText().split(", ")))
        else:
            tags = []
        self.articles[str(id)] = {"title": title, "date": date, "tags": tags}
        return "{} {} {} {}".format(id,date,title,tags)

    def __get_some_id(self):
        '''
        Look for an article on home page
        '''
        if "." in self.blogname:
            url = "https://" + self.blogname
            pattern = self.blogname + "\/[0-9]+\.html"
        else:
            url = "https://" + self.blogname + ".livejournal.com"
            pattern = self.blogname + "\.livejournal\.com\/[0-9]+\.html"
        page = requests.get(url).text
        m = re.search(pattern, page).group()
        id = m.split("/")[-1][:-5]
        return id

    def __get_previous_id(self, id):
        requestUrl = self.url_prev_template.format(self.blogname, id)
        page = requests.get(requestUrl, verify=self.ssl_enabled)
        if page.url == requestUrl:
            return 0
        else:
            return page.url.split("/")[-1][:-5]

    def __get_next_id(self, id):
        requestUrl = self.url_next_template.format(self.blogname, id)
        page = requests.get(requestUrl, verify=self.ssl_enabled)
        if page.url == requestUrl:
            return 0
        else:
            return page.url.split("/")[-1][:-5]

    def __retrieve_down_from_id(self, id, how_many=-1):
        current_id = id
        prev_id = self.__get_previous_id(current_id)
        while current_id and how_many:
            page = self.parse(current_id)
            current_id, prev_id = prev_id, self.__get_previous_id(prev_id)
            print(page)
            how_many -= 1

    def __retrieve_up_from_id(self, id, how_many=-1):
        current_id = id
        next_id = self.__get_next_id(current_id)
        while current_id and how_many:
            page = self.parse(current_id)
            current_id, next_id = next_id, self.__get_next_id(next_id)
            print(page)
            how_many -= 1

    def get_size(self):
        return len(self.articles)

    def is_full(self):
        '''
        Do we have everything?
        '''
        return not self.__any_newer() and not self.__any_older()

    def __any_newer(self):
        # TODO what if blog has 0 posts???
        if len(self.articles) == 0:
            return True
        newest = max({key:content for  key,content in self.articles.items() if content["date"] != "NA"}, key=lambda i: self.articles[i]["date"])
        return bool(self.__get_next_id(newest))

    def __any_older(self):
        # TODO what if blog has 0 posts???
        if len(self.articles) == 0:
            return True
        oldest = min({key:content for  key,content in self.articles.items() if content["date"] != "NA"}, key=lambda i: self.articles[i]["date"])
        return bool(self.__get_previous_id(oldest))

    def retrieve_up(self, how_many=-1):  # takes the oldest article in self.articles and continues retrieving
        if len(self.articles):
            current_id = self.__get_next_id(max({key:content for  key,content in self.articles.items() if content["date"] != "NA"}, key=lambda i: self.articles[i]["date"]))
        else:
            current_id = self.__get_some_id()
        self.__retrieve_up_from_id(current_id, how_many)

    def retrieve_down(self, how_many=-1):  # takes the oldest article in self.articles and continues retrieving
        if len(self.articles):
            current_id = self.__get_previous_id(min({key:content for  key,content in self.articles.items() if content["date"] != "NA"}, key=lambda i: self.articles[i]["date"]))
        else:
            current_id = self.__get_some_id()
        self.__retrieve_down_from_id(current_id, how_many)

    def read_from_json(self, json):
        '''
        Reads from json, not from file
        '''
        data = json
        self.blogname, self.articles = data["blogname"], data["articles"]
        self.ssl_enabled = False if "." in self.blogname else True
        self.shift = 16 + len(self.blogname)

    def save(self):
        '''
        Returns json, doesnt write to a file
        '''
        return {"blogname": self.blogname, "articles": self.articles}


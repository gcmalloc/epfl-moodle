#!/usr/bin/env python2
import requests
import urlparse
import logging
from BeautifulSoup import BeautifulSoup
import os

class Ressource(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __str__(self):
        return  "Ressource:" + self.name +"\nLink :" + self.link

class Moodle(object):

    CHUNCK  = 1024 * 1024

    def __init__(self, username, password, caching=True):
        """This will create a new moodle handshake.
        """
        self.login(username, password)
        if caching:
            try:
                import requests_cache
                requests_cache.configure('.moodle_cache')
            except ImportError:
                logging.warning("requests_cache cannot be imported")
                logging.warning("Moodle will be requested without caching")

    def login(self, username, password):
        """Explicitly login into the moodle service, this will create
        a new moodle session as self.session
        """
        with requests.session() as self.session:
            resp = self.session.get("http://moodle.epfl.ch/login/index.php")
            parsed_url = urlparse.urlsplit(resp.url)
            dict_query = urlparse.parse_qs(parsed_url.query)
            self.sesskey = dict_query['requestkey'][0]
            payload = {'requestkey': self.sesskey, 'username': username, 'password': password}
            self.session.post("https://tequila.epfl.ch/cgi-bin/tequila/login", verify=True, data=payload)

    def __exit__(self):
        self.session.close()

    def get_courses(self):
        """return a dict with course id as key and course name as value
        """
        main_page = self.session.get("http://moodle.epfl.ch/my/")
        soup = BeautifulSoup(main_page.text)
        for course_head in soup('h3', 'main'):
            course_link = course_head.find('a')
            yield Ressource(course_link.string, course_link['href'])

    def get_documents(self, course):
        course_page = self.session.get(course.link)
        soup = BeautifulSoup(course_page.text)
        content = soup.find('div', 'course-content')

        #Week separation
        weeks = content.find('ul',recursive=False).findAll('li', recursive=False)
        divisions = list()
        for week in weeks:
            week_documents = week('a')
            week_doc = list()
            for i in week_documents:
                if 'resource' in i['href']:
                    week_doc.append(Ressource(i.text, i['href']))
            divisions.append(week_doc)
        return divisions

    def fetch_document(self, document, directory=""):
        content_page = self.session.get(document.link)
        if content_page.url != document.link:
            #we have a redirection
            content_url = content_page.url
        else:
            soup = BeautifulSoup(content_page.text)
            content_tag = soup.find('object', {'id':'resourceobject'})
            if content_tag:
                content_url = content_tag['data']
            else:
                #direct download
                parent_content_tag = soup.find('div', 'resourceworkaround')
                content_url = parent_content_tag.find('a')['href']

        file_name = os.path.basename(content_url)
        file_path = os.path.join(directory, file_name)
        file_in = self.session.get(content_url)

        if os.path.exists(file_path):
            logging.error(u"File {} already exist".format(file_path))
            logging.error("Remove it to redownload it")
            return

        with open(file_path, 'wb') as file_out:
            file_out.write(file_in.content)
        return

import requests
try:
    import urlparse
    from urllib import unquote
except ImportError:
    import urllib.parse as urlparse
    from urllib.parse import unquote
import logging
try:
    from bs4 import BeautifulSoup
except ImportError:
    #fallback from bs4
    from BeautifulSoup import BeautifulSoup
import os
import socket
import time

class Ressource(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __str__(self):
        return  "Ressource: {} Link: {}".format(self.name, self.link)

class ConnexionIssue(socket.error):
    pass

class TequilaError(ConnexionIssue):
    pass

class Moodle(object):

    TEQUILA_LOGIN = "http://moodle.epfl.ch/login/index.php"

    MAIN_PAGE = "http://moodle.epfl.ch/my"

    def __init__(self, username, password, caching=False):
        """This will create a new moodle handshake.
        """
        self.login(username, password)
        if caching:
            logging.info("caching enable")
            try:
                import requests_cache
                requests_cache.configure('.moodle_cache')
            except ImportError:
                logging.warning("requests_cache cannot be imported")
                logging.warning("Moodle will be requested without caching")

    def login(self, username, password):
        """Explicitly login into the moodle service, this will create
        a new moodle session as self.session

        :raise TequilaError:
        """
        with requests.session() as self.session:
            resp = self.session.get(Moodle.TEQUILA_LOGIN)
            if resp.status_code != 200:
                raise ConnexionIssue()
            parsed_url = urlparse.urlsplit(resp.url)
            dict_query = urlparse.parse_qs(parsed_url.query)
            self.sesskey = dict_query['requestkey'][0]
            payload = {'requestkey': self.sesskey, 'username': username, 'password': password}
            resp = self.session.post("https://tequila.epfl.ch/cgi-bin/tequila/login", verify=True, data=payload)
            error = BeautifulSoup(resp.text, 'html.parser') \
                    .find('font', color='red', size='+1')
            if error:
                logging.info("Tequila error")
                logging.debug(error.string)
                #grab the tequila error if any
                raise TequilaError(error.string)
            if resp.status_code != 200:
                logging.info("tequila didn't return a 200 code")
                logging.debug(resp.status_code)
                raise ConnexionIssue()

    def __exit__(self):
        """Close the session when the module is closed.
        """
        logging.info("closing the tequila session.")
        self.session.close()

    def get_courses(self):
        """return a dict with course id as key and course name as value
        """
        main_page = self.session.get(Moodle.MAIN_PAGE)
        if main_page.status_code != 200:
            logging.info("Issue with the listing of courses")
            logging.debug(main_page)
            raise ConnexionIssue()
        soup = BeautifulSoup(main_page.text, 'html.parser')
        logging.info("Soup created")
        for course_head in soup.find_all(class_='course_title'):
            logging.info("course found")
            logging.debug(course_head)
            course_link = course_head.find('a')
            logging.debug(course_link.string)
            logging.debug(course_link['href'])
            yield Ressource(course_link.string, course_link['href'])

    def get_documents(self, course):
        """Return a list of list of all the documents for a course
        every item represent a section, and every subitem represent a
        document in the course and in the section.
        """
        logging.info("get documents")
        logging.debug(course.link)
        course_page = self.session.get(course.link)
        if course_page.status_code != 200:
            logging.info("Issue with the fetching")
            logging.debug(course_page)
            raise ConnexionIssue()
        soup = BeautifulSoup(course_page.text, 'html.parser')
        logging.info("Soup created for the document")
        content = soup.find('div', {'class':'course-content'})
        logging.debug(content)
        #the student is not registered to the course anymore
        if not content:
            logging.error(u"You are not registered to the course {} anymore.".format(course))
            return list()
        #Week separation
        weeks = content.find('ul',recursive=False).findAll('li', recursive=False)
        logging.info("Fetching weeks")
        logging.debug(weeks)
        divisions = list()
        for week in weeks:
            logging.info("New week")
            logging.debug(week)
            #week_title = week.find({"class":"sectionname"})
            logging.info("Fetching document for the week")
            week_documents = week('a')
            logging.debug(week_documents)
            week_doc = list()
            for i in week_documents:
                logging.info("fetching document")
                logging.debug(i)
                #yes `a` tag without href exist
                if i.get('href') and 'resource' in i.get('href'):
                    logging.info("found a link and a ressource")
                    week_doc.append(Ressource(i.text, i['href']))
            divisions.append(week_doc)
        return divisions

    def fetch_document(self, document, directory=""):
        """Download document `document` into `directory`
        """
        content_page = self.session.get(document.link)
        if content_page.status_code != 200:
            raise ConnexionIssue()
        if content_page.url != document.link:
            #we have a redirection
            content_url = content_page.url
        else:
            soup = BeautifulSoup(content_page.text, 'html.parser')
            content_tag = soup.find('object', {'id':'resourceobject'})
            video_tag = soup.find('object', {'type':'video/mp4'})
            if content_tag:
                content_url = content_tag['data']
            elif video_tag:
                #seems like there is a video as a ressource
                content_url = video_tag['data']
            else:
                #direct download
                parent_content_tag = soup.find('div', 'resourceworkaround')
                if not parent_content_tag:
                    return
                content_url = parent_content_tag.find('a')
                if content_url.get('href'):
                    content_url = content_url['href']
                else:
                    return

        file_in = self.session.get(content_url)
        file_name = unquote(urlparse.urlparse(content_url)[2])
        file_name = os.path.basename(file_name)
        file_path = os.path.join(directory, file_name)

        if os.path.exists(file_path):
            logging.debug(u"File {} already exist, checking if the remote file is newer".format(file_path))
            try:
                remote_time = time.strptime(file_in.headers['last-modified'])
            except (KeyError, ValueError) as e:
                logging.debug("Couldn't parse the date.")
                return
            remote_timestamp = time.mktime(d.timetuple(remote_time))
            local_timestamp = os.path.getmtime()
            if  local_timestamp < remote_timestamp:
                logging.debug(u"The remote file {} is newer than the local one.".format(file_path))
                os.remove(file_path)
            else:
                logging.debug("the local file is the last remote file")
                return

        with open(file_path, 'wb') as file_out:
            file_out.write(file_in.content)


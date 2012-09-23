#!/usr/bin/env python2
import requests
import urlparse

class Moodle(object):
    def __init__(self, username, password):
        """This will
        """
        self.login(username, password)

    def with_moodle_session(self, func):
        """Decorator used with a moodle session. For example,

        """
        def wrapped(*args, **kwargs):
            with self.session as s:
                print "wrapped called"
                return func(s, *args, **kwargs)
        return wrapped

    def is_connected(self):
        with self.session as s:
            return s.get("http://moodle.epfl.ch/my").content

    def login(self, username, password):
        """Explicitly login into the moodle service, this will create
        a new moodle session as self.session
        """
        with requests.session() as self.session:
            #self.session.get("http://moodle.epfl.ch")
            resp = self.session.get("http://moodle.epfl.ch/login/index.php")
            parsed_url = urlparse.urlsplit(resp.url)
            dict_query = urlparse.parse_qs(parsed_url.query)
            self.sesskey = dict_query['requestkey'][0]
            payload = {'requestkey': self.sesskey, 'username': username, 'password': password}
            self.session.post("https://tequila.epfl.ch/cgi-bin/tequila/login", verify=True, data=payload)

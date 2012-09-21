#!/usr/bin/env python2
import requests
import urlparse

class Moodle(object):
    def __init__(self, username, password):
        """This will
        """
        self.login(username, password)

    def with_moodle_session(self, f):
        def wrapped(*args, **kwargs):
            with self.session as s:
                f(s, *args, **kwargs)
        return wrapped

    def login(self, username, password):
        """Explicitly login into the moodle service, this will create
        a new moodle session as self.session
        """
        with requests.session() as self.session:
            re = self.session.get("http://moodle.epfl.ch/login/index.php")
            parsed_url = urlparse.urlsplit(re.url)
            dict_query = urlparse.parse_qs(parsed_url.query)
            payload = {'requestkey': dict_query['requestkey'][0], 'username': username, 'password': password}
            self.session.post("https://tequila.epfl.ch/cgi-bin/tequila/login", verify=True, data=payload)


    def logout(self):
        """
        """
        raise NotImplemented()

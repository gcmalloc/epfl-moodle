#!/usr/bin/env python2
from BeautifulSoup import BeautifulSoup
from moodle import Moodle


@moodle.with_moodle_session
def get_course(session):
    """return a dict with course id as key and course name as value
    """
    main_page = session.get("http://moodle.epfl.ch/my/")
    print main_page.content
    soup = BeautifulSoup(main_page.content)
    return [subdom for subdom in soup.findAll()]

print get_course()

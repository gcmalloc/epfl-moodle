#!/usr/bin/env python2
from BeautifulSoup import BeautifulSoup
from moodle import Moodle
import os

USER = ''
PASS = ''
moodle = Moodle(USER, PASS, caching=False)

class Course(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def __str__(self):
        return  "Course :" + self.name +"\nLink :" + self.link

@moodle.with_moodle_session
def get_courses(session):
    """return a dict with course id as key and course name as value
    """
    main_page = session.get("http://moodle.epfl.ch/my/")
    soup = BeautifulSoup(main_page.text)
    for course_head in soup('h3', 'main'):
        course_link = course_head.find('a')
        yield Course(course_link.string, course_link['href'])

@moodle.with_moodle_session
def get_documents(session, course, directory=None):
    course_page = session.get(course)
    soup = BeautifulSoup(course_page.text)
    content = soup.find('div', 'course-content')

    #Week separation
    weeks = content.find('ul',recursive=False).findAll('li', recursive=False)
    for week in weeks:
        week_documents = week('a')
        print '-'*8
        for i in week_documents:
            print " || ".join([i.text, i['href']])

CHUNCK  = 1024 * 1024
@moodle.with_moodle_session
def get_document(session, url, directory=""):
    content_page = session.get(url)
    soup = BeautifulSoup(content_page.content)
    content_url = soup.find('object', {'id':'resourceobject'})['data']
    filename = os.path.basename(content_url)
    file_in = session.get(content_url).raw

    with open(os.path.join(directory, filename), 'wb') as file_out:
        while True:
            data = file_in.read(CHUNCK)
            if not data:
                break
            file_out.write(data)



get_document("http://moodle.epfl.ch/mod/resource/view.php?id=814037")

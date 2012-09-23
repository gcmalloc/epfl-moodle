#!/usr/bin/env python2
from BeautifulSoup import BeautifulSoup
from moodle import Moodle
USER = ''
PASS = ''
moodle = Moodle(USER, PASS)

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
    soup = BeautifulSoup(main_page.content)
    for course_head in soup.findAll('h3', 'main'):
        course_link = course_head.find('a')
        yield Course(course_link.string, course_link['href'])

@moodle.with_moodle_session
def get_pdf(session, course, directory=None):
    course_page = session.get(course)
    soup = BeautifulSoup(course_page.content)
    content = soup.find('div', 'course-content')

    #Week separation
    weeks = content.find('ul',recursive=False).findAll('li', recursive=False)
    for week in weeks:
        week_documents = week.findAll('a')
        print '-'*8
        for i in week_documents:
            print " || ".join([i.text, i['href']])


get_pdf("http://moodle.epfl.ch/course/view.php?id=7871")
get_pdf("http://moodle.epfl.ch/course/view.php?id=6831")


## Requirements
* `setuptools` for the installation (in the python package setuptools in debian)
* `python-2.7`
* `BeautifulSoup` (installed by the setup.py)
* `requests` (installed by the setup.py)
* `requests-cache` (optional)
* A moodle account subscribed to at least one course


## Installation
Type:

    git clone git://github.com/gcmalloc/epfl-moodle.git
    cd epfl-moodle
    python setup.py install

## Usage
Do, with $username as your gaspar username :
    
    moodle $username

This will initialise a moodle configuration file in the current directory. A menu will be then displayed, choose which course you would like to keep up to date in this directory. Then the script will download all the specified courses.


Then 

    moodle $username

will update all the course kept in this directory

You can also simply download a single course with 

    moodle $username $course

With $course, the id of the course you want to scrap.

the course must be a moodle url refering to a course in the form
http://moodle.epfl.ch/course/view.php?id=$id

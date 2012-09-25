
## Requirements

* `BeautifulSoup`
* `requests`
* `requests-cache` (optional)
* A moodle account subscribed to at least one course


## Installation
Type:
    git clone git@github.com:gcmalloc/epfl-moodle.git
    cd epfl-moodle
    python setup.py install

## Usage
Do, with $username as your gaspar username and $password as your moodle password:
    
    moodle $username $password

This will initialise a moodle directory in the actual one. A menu will be displayed, choose which course you would like to keep up to date in this directory.

Then 

    moodle $username $password

will update all the course kept in this directory

You can also simply download a single course with 

    moodle $username $password $cours
With $id, the id of the course you want to scrap.

the course must be a moodle url refering to a course in the form
http://moodle.epfl.ch/course/view.php?id=$id



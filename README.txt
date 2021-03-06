http://cardstories.org/

Copyright (C) 2010,2011 Xavier Antoviaque <xavier@antoviaque.org> (gameplay and specifications)
Copyright (C) 2010,2011 David Blanchard <david@blanchard.name> (gameplay and specifications)
Copyright (C) 2010,2011 tartarugafeliz <contact@tartarugafeliz.com> (artwork)
Copyright (C) 2011 Loic Dachary <loic@dachary.org> (software)

  A player (who we will call the author) creates a new game. 
  He chooses a card, picks a word or a sentence to describe it
  and invites players to participate.
  Each players is given seven cards and are required to pick
  one that best matches the author's sentence.
  Once enough players have chosen a card, the author displays all chosen
  cards and the players try to figure out which one is the author's.
  The author wins if at least one of the players guesses right, but not all
  of them do. The winners are the author and the players who guessed right. 
  If the author loses, all the other players win. 


####################################
Setting up a development environment
####################################

The following are instructions to set up a contained development environment
on a recent installation of Ubuntu or Debian.

First, install the following packages.

$ sudo apt-get install postfix python-twisted python-lxml \
  python-imaging python-simplejson python-httplib2 python-pip sqlite3

Now install the following with pip:

$ sudo pip install Django==1.2.5
$ sudo pip install South==0.7.3
$ sudo pip install mock==0.7.2
$ sudo pip install requests==0.8.6

Now, make sure you are at the root of the cardstories checkout.  At this point,
create the default database structure for the website, but first, create a
local configuration file containing the following:

$ vim website/local_settings.py
-------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/website.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
-------------------

Now, create the database:

$ website/manage.py syncdb
$ website/manage.py migrate

Note that for local Facebook development, you must also add an entry to
/etc/hosts that matches the domain name in your Django site configuration.  It
is recommended when running the above syncdb command to chose
"local.cardstories.org" as the domain name, and then to add a line in
/etc/hosts like the following:

127.0.0.1 local.cardstories.org

If for any reason you need to run the website dev server on a different host or
port, these files that must be modified accordingly (and the cardstories web
service restarted if it's already running):

   * tests/djangoauth/djangoauth.xml
   * tests/mail/mail.xml

Create the log folder: 

    $ mkdir log/

On one terminal window, run the cardstories web service.  Under default
configuration, the following command assumes you have postfix configured
properly for relaying emails sent to 'localhost' (otherwise invitations won't
be sent out):

$ PYTHONPATH=.:etc/cardstories twistd --nodaemon cardstories \
	--static $(pwd)/static --port 5000 --interface 0.0.0.0 \
	--db /tmp/cardstories.sqlite \
	--plugins-dir plugins \
	--plugins-libdir /tmp \
	--plugins-logdir log/ \
	--plugins-confdir tests \
	--plugins 'djangoauth chat activity table mail' \
	--plugins-pre-process 'djangoauth chat'
	--plugins-post-process 'table'

On a second terminal window, still from the root of the checkout, run the
website development server, which by default binds to localhost and port 8000.
However, for local Facebook redirection to work (which you set up above in
/etc/hosts), you must run the server on port 80 as root:

$ sudo website/manage.py runserver 0.0.0.0:80

Now simply access http://local.cardstories.org/, and code away!


###########################
Enabling Open Web Analytics
###########################

To use OWA, first you must get it up and running somewhere.  To do so, follow
the installation steps here:

http://wiki.openwebanalytics.com/index.php?title=Installation

Once it's configured and running, for example at http://localhost:8080/, log in
and obtain your Site ID.  With this information in hand, start by setting the
correct values in website/settings.py:

$ vim website/settings.py
----------
OWA_ENABLE = True
OWA_URL = 'http://localhost:8080/'
OWA_SITE_ID = '<your_site_id>'
----------

Once this is done, all relevant page views should be logged.  Game state
changes will be artificially logged as page views with URLs in the following
format, where <skin_name> refers to an existing skin in the game.

http://local.cardstories.org/?skin=<skin_name>

You can then proceed to set up goals in OWA accordingly.


#################################
Deploying cardstories with Apache
#################################

In order to deploy cardstories with Apache, the following additional packages
must be installed:

$ sudo apt-get install apache2 libapache2-mod-wsgi

From the root of your cardstories checkout, install cardstories to the default
locations with:

$ sudo python setup.py install

Then, from cardstories root, copy the apache configuration file to the proper
location on the file system, and enable it.  You may need to edit it depending
on your site characteristics (particularly the location of django's admin
media):

$ sudo cp website/apache/apache2.conf /etc/apache2/sites-available/cardstories
$ sudo a2ensite cardstories

Now enable the required apache mods, and restart the server:

$ a2enmod wsgi
$ a2enmod proxy_http
$ sudo /etc/init.d/apache2 restart

Don't forget to create the default database for the website and run the
cardstories web service as described in the previous section.

Finally, to future deployments, you can create a separate local_settings.py
containing just the stuff you want applied locally (such as Facebook app id,
OWA url, etc) in:

/usr/share/cardstories/website/local_settings.py

To disable specific email notifications, after deployment edit
/etc/cardstories/plugins/mail/mail.xml so that it contains only the "allow"
nodes you need (valid options are 'invite', 'pick', 'voting', 'vote',
'complete'):

<mail ...>
  <allow>invite</allow>
  <allow>vote</allow>
</mail>

If NO notifications are to be sent, create an empty allow node (for backward
compatibility, if there aren't any allow nodes, mail will be sent for all
events):

<mail ...>
  <allow></allow>
</mail>


##############
Usage examples
##############

To display the cardstories web service usage information:

$ PYTHONPATH=.:etc/cardstories twistd cardstories --help

To run the webservice without mail or djangoauth:

$ PYTHONPATH=.:etc/cardstories twistd --nodaemon cardstories \
	--static $(pwd)/static --port 5000 --interface 0.0.0.0 \
	--db /tmp/cardstories.sqlite \
	--plugins-dir plugins \
	--plugins-libdir /tmp \
	--plugins-confdir tests \
	--plugins-logdir log \
	--plugins 'auth chat' \
	--plugins-pre-process 'auth chat activity' \

To check if the webservice replies, run the following (requires curl). The
following must return the [{"games": [], "type": "tabs", "modified": 0}, {"type": "players_info}"]
string:

$ curl --silent 'http://localhost:5000/resource?action=state&type=tabs=player_id=0'


#############
Extra plugins
#############

* Bot plugin:
    - See ./plugins/bot/README.txt for installation instructions


#################
Running the tests
#################

First install the dependencies:

$ sudo apt-get install python-coverage jscoverage

Running the Python tests (Twisted and Django):

$ make -f maintain.mk clean
$ make -f maintain.mk check

Running the Javascript tests - using your browser, go to:

- http://local.cardstories.org:8000/static/test/index.html
- http://local.cardstories.org:8000/static/test/audio.html
- http://local.cardstories.org:8000/static/test/chat.html
- http://local.cardstories.org:8000/static/test/owa.html
- http://local.cardstories.org:8000/static/test/table.html
- http://local.cardstories.org:8000/static/test/tabs.html


######################
Packaging instructions
######################

To create a source distribution use:

$ v=2.0.0 ; python setup.py sdist --dist-dir .. ; mv ../cardstories-$v.tar.gz ../cardstories_$v.orig.tar.gz

To create the Debian GNU/Linux package use:

$ dpkg-buildpackage -S -uc -us


##########
Migrations
##########

A) Upgrading the webservice DB
==============================

When upgrading, if there has been alteration to the webservice database schema, 
migration files will be added to the migrations/ folder. Just run them, in numerical 
order, using a command like:

    $ sqlite3 /tmp/cardstories.org.sqlite < migrations/001_add_tabs_table.sql


B) Upgrading Django's DB (v2.2+)
================================

You will also need to make sure there hasn't been any DB alteration in django - run
the following commands to ensure you're up to date:

    $ ./website/manage.py syncdb
    $ ./website/manage.py migrate

B') Upgrading Django's DB (from before v2.2)
============================================

Prior to version 2.2, django wasn't using south to handle migrations. So if you have 
a database from before 2.2, run the following commands to avoid having south trying
to recreate the database from scratch (if you ran syncdb on the 2.1 version, make 
sure you drop the cardstories_usercard table, as the migration will attempt to 
create it)

    $ ./website/manage.py syncdb
    $ ./website/manage.py migrate cardstories 0001 --fake


B) Developers - Automatically generating Django migrations
==========================================================

For the webservice, you will have to create the SQL migration files manually in the
migrations/ folder, but for django south will take care of it automatically for you,
based on alterations you make to the models.py file. Simply run the following
command:

    $ ./website/manage.py schemamigration cardstories --auto 
    $ ./website/manage.py migrate cardstories


######################
Additional information
######################

As of Apr, 26th 2011 there are 321 LOC of JavaScript, 687 LOC of Python = 1008 LOC
As of Jun, 19th 2011 there are 473 LOC of JavaScript, 896 LOC of Python = 1369 LOC

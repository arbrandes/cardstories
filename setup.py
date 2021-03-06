#!/usr/bin/env python
#
# Copyright (C) 2011 Loic Dachary <loic@dachary.org>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#

import os, re
from distutils.core import setup

data_files = []
for dirpath, dirnames, filenames in os.walk('static'):
	    # Ignore dirnames that start with '.'
	    for i, dirname in enumerate(dirnames):
	        if dirname.startswith('.'): del dirnames[i]
                if dirname == 'mockups':
                    del dirnames[i]
	    if filenames:
                filenames = filter(lambda f: re.match('.*.(html|css|js|png|jpg|gif|eot|woff|ttf|svg|swf|mp4|ogv|webm|zip|mp3)$', f), filenames)
	        data_files.append(['/usr/share/cardstories/' + dirpath, [os.path.join(dirpath, f) for f in filenames]])

for dirpath, dirnames, filenames in os.walk('website'):
	    # Ignore dirnames that start with '.'
	    for i, dirname in enumerate(dirnames):
	        if dirname.startswith('.'): del dirnames[i]
	    if filenames:
                filenames = filter(lambda f: re.match('.*.(py|html)$', f), filenames)
	        data_files.append(['/usr/share/cardstories/' + dirpath, [os.path.join(dirpath, f) for f in filenames]])

for dirpath, dirnames, filenames in os.walk('migrations'):
	    # Ignore dirnames that start with '.'
	    for i, dirname in enumerate(dirnames):
	        if dirname.startswith('.'): del dirnames[i]
	    if filenames:
                filenames = filter(lambda f: re.match('.*.(sql)$', f), filenames)
	        data_files.append(['/usr/share/cardstories/' + dirpath, [os.path.join(dirpath, f) for f in filenames]])

data_files.append(['/etc/default', ['etc/default/cardstories']])
data_files.append(['/etc/cardstories/twisted/plugins', ['etc/cardstories/twisted/plugins/twisted_cardstories.py']])
data_files.append(['/usr/share/cardstories/conf', [ 'conf/nginx.conf' ]])
data_files.append(['/usr/share/cardstories/conf', [ 'conf/apache2.conf' ]])
data_files.append(['/usr/share/cardstories/website/apache', [ 'website/apache/apache2.conf' ]])
data_files.append(['/usr/share/cardstories/website/apache', [ 'website/apache/django.wsgi' ]])

# Plugins
data_files.append(['/usr/share/cardstories/plugins/auth', [ 'plugins/auth/auth.py' ]])
data_files.append(['/usr/share/cardstories/plugins/djangoauth', [ 'plugins/djangoauth/djangoauth.py' ]])
data_files.append(['/usr/share/cardstories/plugins/mail', [ 'plugins/mail/mail.py' ]])
data_files.append(['/usr/share/cardstories/plugins/chat', [ 'plugins/chat/chat.py' ]])
data_files.append(['/usr/share/cardstories/plugins/table', [ 'plugins/table/table.py' ]])
data_files.append(['/usr/share/cardstories/plugins/activity', [ 'plugins/activity/activity.py' ]])

for dirpath, dirnames, filenames in os.walk('plugins/mail/templates'):
	    # Ignore dirnames that start with '.'
	    for i, dirname in enumerate(dirnames):
	        if dirname.startswith('.'): del dirnames[i]
	    if filenames:
                filenames = filter(lambda f: re.match('.*.(html|png|jpg|gif)$', f), filenames)
	        data_files.append(['/usr/share/cardstories/' + dirpath, [os.path.join(dirpath, f) for f in filenames]])

# Plugin configuration files
data_files.append(['/etc/cardstories/plugins/mail', [ 'plugins/mail/mail.xml' ]])
data_files.append(['/etc/cardstories/plugins/djangoauth', [ 'plugins/djangoauth/djangoauth.xml' ]])

setup(name='cardstories',
      version='2.0.0',
      requires=['twisted (>=10.1.0)'],
      description='Find out a card using a sentence made up by another player',
      author='Loic Dachary',
      author_email='loic@dachary.org',
      url='http://cardstories.org/',
      license='GNU AGPLv3+',
      data_files=data_files,
      packages=['cardstories'])

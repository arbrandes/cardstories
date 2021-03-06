# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Loic Dachary <loic@dachary.org>
#
# Authors:
#          Loic Dachary <loic@dachary.org>
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
import os
import imp

from cardstories import poll, auth

class CardstoriesPlugins:

    def __init__(self, settings):
        self.settings = settings
        self.plugins = []

    def load(self, service):
        for plugin in self.settings.get('plugins', '').split():
            module = imp.load_source("cardstories_plugin", self.path(plugin))
            o = getattr(module, 'Plugin')(service, self.plugins)
            self.plugins.append(o)
            if isinstance(o, poll.Pollable):
                service.pollable_plugins.append(o)
            if isinstance(o, auth.Auth):
                service.auth = o

    def path(self, plugin):
        if os.path.exists(plugin):
            return plugin
        path = os.path.join(self.settings['plugins-dir'], plugin, plugin + '.py')
        if os.path.exists(path):
            return path
        raise UserWarning, plugin + ' and ' + path + ' are not file paths'

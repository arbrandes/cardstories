#
# Copyright (C) 2011 Dachary <loic@dachary.org>
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
import sys
sys.path.insert(0, "..") # so that for M-x pdb works
import os

from twisted.trial import unittest, runner, reporter
from twisted.internet import defer
from twisted.web import server, resource
from twisted.python import filepath

from twisted.web.test.test_web import DummyRequest
from twisted.web.test._util import _render

from cardstories.site import CardstoriesResource, CardstoriesTree

class CardstoriesServiceMockup:
    def __init__(self):
        self.settings = {'static': os.getcwd() }

    def get(self): return 'get'

    def submit(self, args): return 'submit'

class CardstoriesSiteTest(unittest.TestCase):

    class Transport:
        def getPeer(self):
            return None
        def getHost(self):
            return None

    class Channel:
        def __init__(self, site):
            self.transport = CardstoriesSiteTest.Transport()
            self.site = site

        def requestDone(self, request):
            pass

    def setUp(self):
        self.service = CardstoriesServiceMockup()

    def tearDown(self):
        if hasattr(self, 'site'):
            self.site.stopFactory()

    def test00_render(self):
        self.site = server.Site(CardstoriesTree(self.service))
        r = server.Request(self.Channel(self.site), True)
        r.site = r.channel.site
        input = ''
        r.gotLength(len(input))
        r.handleContentChunk(input)
        r.queued = 0
        d = r.notifyFinish()
        def finish(result):
            self.assertSubstring('\r\n\r\n"get"', r.transport.getvalue())
        d.addCallback(finish)
        r.requestReceived('GET', '/resource', '')
        return d

    def test00_render_static(self):
        file = "file"
        fd = open(file, "w")
        fd.write('CONTENT')
        fd.close()

        tree = CardstoriesTree(self.service)
        request = DummyRequest(['static', 'file'])
        child = resource.getChildForRequest(tree, request)

        self.assertTrue(isinstance(child, filepath.FilePath))
        d = _render(child, request)
        def finish(result):
            self.assertEquals(['CONTENT'], request.written)
        d.addCallback(finish)
        return d

    def test01_wrap_http(self):
        resource = CardstoriesResource(self.service)
        self.site = server.Site(resource)
        request = server.Request(self.Channel(self.site), True)
        request.method = 'GET'
        d = resource.wrap_http(request)
        def finish(result):
            self.assertSubstring('\r\n\r\n"get"', request.transport.getvalue())
        d.addCallback(finish)
        return d

    def test02_wrap_http_fail(self):
        resource = CardstoriesResource(self.service)
        fail_string = 'FAIL STRING'
        def fail(result, request):
            raise Exception(fail_string)
        resource.handle = fail
        self.site = server.Site(resource)
        request = server.Request(self.Channel(self.site), True)
        d = resource.wrap_http(request)
        def finish(result):
            self.assertSubstring(fail_string, request.transport.getvalue())
        d.addCallback(finish)
        return d

    def test03_handle(self):
        resource = CardstoriesResource(self.service)
        self.site = server.Site(resource)
        request = server.Request(self.Channel(self.site), True)

        # get
        request.method = 'GET'
        self.assertEquals('get', resource.handle(True, request))

        # unknown method
        caught = False
        try:
            request.method = 'PUT'
            resource.handle(True, request)
        except Exception, e:
            caught = True
            self.assertSubstring('PUT', e.args[0])
        self.assertTrue(caught)

        # unknown post argument
        request.method = 'POST'
        request.args = {}
        caught = False
        try:
            resource.handle(True, request)
        except Exception, e:
            caught = True
            self.assertSubstring('Unknown POST', e.args[0])
        self.assertTrue(caught)

        # submit
        request.method = 'POST'
        request.args = {'submit': True}
        self.assertEquals('submit', resource.handle(True, request))

def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test_trynow"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(CardstoriesSiteTest))

    return runner.TrialRunner(
        reporter.VerboseTextReporter,
        tracebackFormat='default',
        ).run(suite)

if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "python-coverage -e ; PYTHONPATH=.. python-coverage -x test-site.py ; python-coverage -m -a -r ../cardstories/site.py"
# End:

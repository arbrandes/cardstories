# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Farsides <contact@farsides.com>
#
# Authors:
#          Matjaz Gregoric <mtyaka@gmail.com>
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

# Imports ##################################################################

import sys, os
sys.path.insert(0, os.path.abspath("..")) # so that for M-x pdb works
import sqlite3
from datetime import datetime, timedelta

from twisted.trial import unittest, runner, reporter
from cardstories.service import CardstoriesService
from cardstories import event_log
from mailing import send, loop


# Classes ##################################################################

class LoopTest(unittest.TestCase):

    def setUp(self):
        self.database = 'test.sqlite'
        if os.path.exists(self.database):
            os.unlink(self.database)
        self.service = CardstoriesService({'db': self.database})
        self.service.startService()
        self.db = sqlite3.connect(self.database)
        # Fake out the django table in our test db.
        c = self.db.cursor()
        c.execute(
            "CREATE TABLE auth_user ( "
            "  id INTEGER PRIMARY KEY, "
            "  username VARCHAR(255), "
            "  first_name VARCHAR(255) "
            "); ")
        c.close()

    def tearDown(self):
        self.db.close()
        os.unlink(self.database)
        return self.service.stopService()

    def test01_loop(self):
        player1 = 1
        player2 = 2
        player3 = 88
        game1 = 111
        game2 = 122
        game3 = 133

        now = datetime.now()
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        three_days_ago = now - timedelta(days=3)
        sec = timedelta(seconds=1)

        c = self.db.cursor()

        # Prepopulate the tables with fixture data.
        # ------------------------------------------------------------
        # 1. auth_user
        auth_user_fixtures = [
            (player1, 'john@johnson.com', 'John Johnson'),
            (player2, 'bill@billson.com', 'Bill Billson'),
            (player3, 'bigjoe99@gmail.com', None)
        ]
        for player in auth_user_fixtures:
            c.execute('INSERT INTO auth_user (id, username, first_name) VALUES (?, ?, ?)', player)

        # 2. games
        games_fixtures = [
            (game1, player1, 'Sentence 1', 'invitation', three_days_ago),
            (game2, player1, 'Sentence 2', 'complete', three_days_ago),
            (game3, player2, 'Sentence 3', 'invitation', now)
        ]
        for game in games_fixtures:
            c.execute('INSERT INTO games (id, owner_id, sentence, state, created) VALUES (?, ?, ?, ?, ?)', game)

        # 3. player2game
        player2game_fixtures =[
            (player1, game1),
            (player1, game2),
            (player2, game1),
            (player2, game2),
            (player2, game3),
            (player3, game2)
        ]
        for player_id, game_id in player2game_fixtures:
            c.execute('insert into player2game (player_id, game_id) values (?, ?)', [player_id, game_id])

        # 4. event_logs
        event_logs_fixtures = [
            # Game 1
            [game1, two_days_ago, event_log.GAME_CREATED,         player1, ''],
            [game1, two_days_ago, event_log.OWNER_CHOSE_CARD,     player1, 22],
            [game1, two_days_ago, event_log.OWNER_WROTE_STORY,    player1, 'Sentence 1'],
            [game1, yesterday,    event_log.PLAYER_JOINED,        player2, ''],
            [game1, yesterday,    event_log.PLAYER_VOTED,         player2, 33],
            # Game 2
            [game2, two_days_ago, event_log.GAME_CREATED,         player1, ''],
            [game2, two_days_ago, event_log.OWNER_CHOSE_CARD,     player1, 34],
            [game2, two_days_ago, event_log.OWNER_WROTE_STORY,    player1, 'Sentence 2'],
            [game2, two_days_ago, event_log.PLAYER_INVITED,       player1, player3],
            [game2, two_days_ago, event_log.PLAYER_JOINED,        player3, ''],
            [game2, two_days_ago, event_log.PLAYER_PICKED_CARD,   player3, 23],
            [game2, two_days_ago, event_log.PLAYER_JOINED,        player2, ''],
            [game2, two_days_ago, event_log.PLAYER_PICKED_CARD,   player2, 24],
            [game2, two_days_ago, event_log.GAME_MOVED_TO_VOTING, player1, ''],
            [game2, two_days_ago, event_log.PLAYER_VOTED,         player2, 44],
            [game2, two_days_ago, event_log.PLAYER_VOTED,         player3, 45],
            [game2, two_days_ago, event_log.GAME_COMPLETED,       player1, ''],
            # Game 3
            [game3, now,          event_log.GAME_CREATED,         player2, ''],
            [game3, now,          event_log.OWNER_CHOSE_CARD,     player2, 34],
            [game3, now,          event_log.OWNER_WROTE_STORY,    player2, 'Sentence 3']
        ]
        for event in event_logs_fixtures:
            c.execute('INSERT INTO event_logs (game_id, timestamp, event_type, player_id, data) VALUES (?, ?, ?, ?, ?)', event)

        # ------------------------------------------------------------
        self.db.commit()
        c.close()

        # Mock out send.send_mail to collect arguments it's been called with.
        calls = []
        def mock_send_mail(email, name, context):
            calls.append([email, name, context])
        send.send_mail = mock_send_mail

        count = loop.loop(self.database, self.database)
        # Should send out three emails (for each of the three players in the db).
        self.assertEquals(count, 3)

        # Let's see what send_mail has been called with.
        self.assertEquals(len(calls), 3)

        # For player1:
        self.assertEquals(calls[0][0], 'john@johnson.com')
        self.assertEquals(calls[0][1], 'John Johnson')
        # No completed games:
        self.assertEquals(len(calls[0][2]['completed_games']), 0)
        # One available game (game3 by player2):
        self.assertEquals(len(calls[0][2]['available_games']), 1)
        game = calls[0][2]['available_games'][0]
        self.assertEquals(game['game_id'], game3)
        self.assertEquals(game['owner_name'], 'Bill Billson')
        self.assertEquals(game['sentence'], 'Sentence 3')
        # Player1 was last active two_days ago.
        # Since then (yesterday), two events happened on one of his games (game1).
        self.assertEquals(len(calls[0][2]['game_activities']), 1)
        activity = calls[0][2]['game_activities'][0]
        self.assertEquals(activity['game_id'], game1)
        self.assertEquals(activity['state'], 'invitation')
        self.assertEquals(activity['owner_name'], 'You')
        self.assertEquals(activity['sentence'], 'Sentence 1')
        self.assertEquals(len(activity['events']), 2)
        self.assertEquals(activity['events'][0], 'Bill Billson joined the game')
        self.assertEquals(activity['events'][1], 'Bill Billson voted')

        # For player2:
        self.assertEquals(calls[1][0], 'bill@billson.com')
        self.assertEquals(calls[1][1], 'Bill Billson')
        # Player2 has last been active 'now', not much has happened since 'now', obviously.
        # No completed games:
        self.assertEquals(len(calls[1][2]['completed_games']), 0)
        # No available games:
        self.assertEquals(len(calls[1][2]['available_games']), 0)
        # No game acitvities:
        self.assertEquals(len(calls[1][2]['game_activities']), 0)

        # For player3:
        self.assertEquals(calls[2][0], 'bigjoe99@gmail.com')
        self.assertEquals(calls[2][1], 'bigjoe99')
        # No completed games:
        self.assertEquals(len(calls[2][2]['completed_games']), 0)
        # One available game (game3 by player2):
        self.assertEquals(len(calls[2][2]['available_games']), 1)
        self.assertEquals(game['game_id'], game3)
        self.assertEquals(game['owner_name'], 'Bill Billson')
        self.assertEquals(game['sentence'], 'Sentence 3')
        # No game acitvities - player3 has less been active two days ago, but he has only
        # participated in game2 which hasn't seen any activity since then:
        self.assertEquals(len(calls[2][2]['game_activities']), 0)

# Main #####################################################################

def Run():
    loader = runner.TestLoader()
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(LoopTest))

    return runner.TrialRunner(
        reporter.VerboseTextReporter,
        tracebackFormat='default',
        ).run(suite)

if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


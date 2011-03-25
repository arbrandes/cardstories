//
//     Copyright (C) 2011 Loic Dachary <loic@dachary.org>
//
//     This program is free software: you can redistribute it and/or modify
//     it under the terms of the GNU General Public License as published by
//     the Free Software Foundation, either version 3 of the License, or
//     (at your option) any later version.
//
//     This program is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU General Public License for more details.
//
//     You should have received a copy of the GNU General Public License
//     along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
module("cardstories");

function setup() {
    $.cardstories.setTimeout = function(cb, delay) { return window.setTimeout(cb, delay); };
    $.cardstories.ajax = function(o) { return jQuery.ajax(o); };
}

test("send get", function() {
    setup();
    expect(5);
    stop();

    var player_id = 15;
    var game_id = 101;

    var game = $.cardstories.game;
    $.cardstories.game = function(arg_player_id, arg_game_id, root) {
	equal(arg_player_id, player_id);
	equal(arg_game_id, game_id);
	ok($(root).hasClass('cardstories_root'), 'cardstories_root');
	$.cardstories.game = game;
	start();
    };
    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?QUERY');
	options.success({}, 'status');
    };

    $('#qunit-fixture .cardstories').addClass('cardstories_root');
    $.cardstories.send(player_id, game_id, $('#qunit-fixture .cardstories_create'), 'QUERY');
});

test("send post", function() {
    setup();
    expect(6);
    stop();

    var player_id = 15;
    var game_id = 101;

    var game = $.cardstories.game;
    $.cardstories.game = function(arg_player_id, arg_game_id, root) {
	equal(arg_player_id, player_id);
	equal(arg_game_id, game_id);
	ok($(root).hasClass('cardstories_root'), 'cardstories_root');
	$.cardstories.game = game;
	start();
    };
    $.cardstories.ajax = function(options) {
        equal(options.type, 'POST');
        equal(options.url, $.cardstories.url + '?QUERY');
        equal(options.data, 'DATA');
	options.success({}, 'status');
    };

    $('#qunit-fixture .cardstories').addClass('cardstories_root');
    $.cardstories.send(player_id, game_id, $('#qunit-fixture .cardstories_create'), 'QUERY', 'DATA');
});

test("create", function() {
    setup();
    expect(3);

    var player_id = 15;
    var card = 1;
    var sentence = 'SENTENCE';

    $.cardstories.ajax = function(options) {
        equal(options.type, 'POST');
        equal(options.url, $.cardstories.url + '?action=create&owner_id=' + player_id + '&card=' + card);
	equal(options.data, 'sentence=' + sentence);
    };

    $.cardstories.create(player_id, $('#qunit-fixture .cardstories_create'));
    $('#qunit-fixture .cardstories_create .cardstories_sentence').val(sentence);
    $('#qunit-fixture .cardstories_create .cardstories_submit').click();
});

test("widget create", function() {
    setup();
    expect(5);

    var player_id = 15;
    var card = 1;
    var sentence = 'SENTENCE';

    $.cardstories.ajax = function(options) {
        equal(options.type, 'POST');
        equal(options.url, $.cardstories.url + '?action=create&owner_id=' + player_id + '&card=' + card);
	equal(options.data, 'sentence=' + sentence);
    };

    ok(!$('#qunit-fixture .cardstories').hasClass('cardstories_root'), 'no cardstories_root');
    $('#qunit-fixture .cardstories').cardstories(player_id);
    ok($('#qunit-fixture .cardstories').hasClass('cardstories_root'), 'cardstories_root');
    $('#qunit-fixture .cardstories_create .cardstories_sentence').val(sentence);
    $('#qunit-fixture .cardstories_create .cardstories_submit').click();
});

test("game", function() {
    setup();
    expect(4);

    var player_id = 15;
    var game_id = 101;
    var card = 1;
    var sentence = 'SENTENCE';

    $.cardstories.fake_state = function(inner_player_id, game, element) {
	equal(inner_player_id, player_id);
	equal(game.id, game_id);
    };

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?action=game&game_id=' + game_id + '&player_id=' + player_id);
	var game = {
	    'id': game_id,
	    'state': 'fake_state'
	};
	options.success(game);
    };

    $.cardstories.game(player_id, game_id, $('#qunit-fixture .cardstories'));
});

test("invitation_owner", function() {
    setup();
    expect(4);

    var player_id = 15;
    var game_id = 101;

    var game = {
	'id': game_id,
	'owner': true,
	'ready': true
    };

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?action=voting&owner_id=' + player_id + '&game_id=' + game_id);
    };

    $.cardstories.invitation(player_id, game, $('#qunit-fixture .cardstories_invitation'));
    equal($('#qunit-fixture .cardstories_owner .cardstories_invite').attr('href'), '?game_id=' + game.id);
    equal($('#qunit-fixture .cardstories_owner .cardstories_refresh').attr('href'), '?player_id=' + player_id + '&game_id=' + game.id);
    $('#qunit-fixture .cardstories_owner .cardstories_voting').click();
});

test("invitation_pick", function() {
    setup();
    expect(3);

    var player_id = 15;
    var game_id = 101;
    var picked_before = 3;
    var picked_after = 5;
    var cards = [1,2,picked_before,4,picked_after,7];
    var sentence = 'SENTENCE';

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?action=pick&player_id=' + player_id + '&game_id=' + game_id + '&card=' + picked_after);
    };

    var game = {
	'id': game_id,
	'self': [picked_before, null, cards],
	'sentence': sentence
    };
    $.cardstories.invitation(player_id, game, $('#qunit-fixture .cardstories_invitation'));
    equal($('#qunit-fixture .cardstories_pick .cardstories_sentence').text(), sentence);
    equal($('#qunit-fixture .cardstories_pick .cardstories_card1').metadata().card, 1);
    equal($('#qunit-fixture .cardstories_pick .cardstories_card7').metadata().card, 7);
    $('#qunit-fixture .cardstories_participate .cardstories_card' + picked_after).click();
});

test("invitation_participate", function() {
    setup();
    expect(3);

    var player_id = 15;
    var game_id = 101;
    var card = 1;
    var sentence = 'SENTENCE';

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?action=participate&player_id=' + player_id + '&game_id=' + game_id);
    };

    var game = {
	'id': game_id,
	'self': null,
	'sentence': sentence
    };
    $.cardstories.invitation(player_id, game, $('#qunit-fixture .cardstories_invitation'));
    equal($('#qunit-fixture .cardstories_participate .cardstories_sentence').text(), sentence);
    $('#qunit-fixture .cardstories_participate .cardstories_submit').click();
});

test("widget invitation", function() {
    setup();
    expect(3);

    var player_id = 15;
    var game_id = 101;
    var sentence = 'SENTENCE';

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?action=game&game_id=' + game_id + '&player_id=' + player_id);
	var game = {
	    'id': game_id,
	    'state': 'invitation',
	    'sentence': sentence
	};
	options.success(game);
	equal($('#qunit-fixture .cardstories_participate .cardstories_sentence').text(), sentence);
    };

    $('#qunit-fixture .cardstories').cardstories(player_id, game_id);
});

test("vote_voter", function() {
    setup();
    expect(7);

    var player_id = 15;
    var game_id = 101;
    var picked = 2;
    var voted_before = 3;
    var voted_after = 5;
    var board = [1,picked,voted_before,4,voted_after,7];
    var sentence = 'SENTENCE';

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?action=vote&player_id=' + player_id + '&game_id=' + game_id + '&vote=' + voted_after);
    };

    var game = {
	'id': game_id,
	'board': board,
	'self': [picked, voted_before, [11,12,13,14,15,16,17]],
	'sentence': sentence
    };
    $.cardstories.vote(player_id, game, $('#qunit-fixture .cardstories_vote'));
    equal($('#qunit-fixture .cardstories_voter .cardstories_sentence').text(), sentence);
    equal($('#qunit-fixture .cardstories_voter .cardstories_card1').metadata().card, 1);
    equal($('#qunit-fixture .cardstories_voter .cardstories_card7').metadata().card, 7);
    ok($('#qunit-fixture .cardstories_voter .cardstories_card' + voted_before).hasClass('cardstories_voted'), 'cardstories_voted');
    ok($('#qunit-fixture .cardstories_voter .cardstories_card' + picked).hasClass('cardstories_picked'), 'cardstories_picked');
    $('#qunit-fixture .cardstories_voter .cardstories_picked').click(); // must do nothing
    $('#qunit-fixture .cardstories_voter .cardstories_card' + voted_after).click();
});

test("vote_viewer", function() {
    setup();
    expect(3);

    var player_id = 15;
    var game_id = 101;
    var board = [1,2,3,4,5,6,7];
    var sentence = 'SENTENCE';

    var game = {
	'id': game_id,
	'board': board,
	'self': null,
	'sentence': sentence
    };
    $.cardstories.vote(player_id, game, $('#qunit-fixture .cardstories_vote'));
    equal($('#qunit-fixture .cardstories_viewer .cardstories_sentence').text(), sentence);
    equal($('#qunit-fixture .cardstories_viewer .cardstories_card1').metadata().card, 1);
    equal($('#qunit-fixture .cardstories_viewer .cardstories_card7').metadata().card, 7);
});

test("vote_owner", function() {
    setup();
    expect(7);

    var player_id = 15;
    var game_id = 101;

    var voter11 = 11;
    var voter12 = 12;
    var voter21 = 21;

    var board1 = 30;
    var board2 = 31;
    var board = [ board1, board2 ];

    var sentence = 'SENTENCE';

    var game = {
	'id': game_id,
	'owner': true,
        'sentence': sentence,
        'board': board,
        'players': [ [ voter11, board1, 'n', [ ] ],
                     [ voter12, board2, 'n', [ ] ],
                     [ voter21, board1, 'n', [ ] ]
                   ],
	'ready': true
    };

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        equal(options.url, $.cardstories.url + '?action=complete&owner_id=' + player_id + '&game_id=' + game_id);
    };

    $.cardstories.vote(player_id, game, $('#qunit-fixture .cardstories_vote'));
    var vote = $('#qunit-fixture .cardstories_vote .cardstories_owner');
    equal($('.cardstories_sentence', vote).text(), sentence);
    ok($('.cardstories_complete', vote).hasClass('cardstories_ready'), 'cardstories_ready');
    var first = $('.cardstories_card:nth(0)', vote);
    equal($('.cardstories_votes:nth(0) .cardstories_voter:nth(0)', vote).text(), voter11.toString());
    equal($('.cardstories_votes:nth(0) .cardstories_voter:nth(1)', vote).text(), voter21.toString());
    equal($('.cardstories_votes:nth(1) .cardstories_voter:nth(0)', vote).text(), voter12.toString());
    
    $('.cardstories_complete', vote).click();
});


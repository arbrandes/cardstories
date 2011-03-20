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

test("cardstories", function() {
    setup();
    expect(0);

    $.cardstories.ajax = function(options) {
        equal(options.type, 'GET');
        options.success({}, true);
    };

    $('#qunit-fixture').cardstories();
});



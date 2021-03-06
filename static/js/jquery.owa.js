//
//     Copyright (C) 2011 Farsides <contact@farsides.com>
//
//     Author: Adolfo R. Brandes <arbrandes@gmail.com>
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
(function($) {

    $.owa = {

        location: location,

        // Where OWA is hosted
        url: '',

        // The site id generated by OWA
        site_id: '',

        init: function(url, site_id, page_view) {
            var $this = this;

            this.url = url;
            this.site_id = site_id;

            // These must be global for OWA to work.
            window["owa_baseUrl"] = this.url;
            window["owa_cmds"] = [];

            // Initialize site id.
            owa_cmds.push(['setSiteId', this.site_id]);

            // Set click and DOM tracking
            owa_cmds.push(['trackClicks']);
            owa_cmds.push(['trackDomStream']);

            // Track this page view canonically, if requested.
            if (page_view) {
                owa_cmds.push(['setPageType', 'normal']);
                owa_cmds.push(['trackPageView']); 
            }

            // Create the OWA script element on the page.  Does not use jQuery
            // selectors or methods because currently none of them support
            // setting the HTML5 "async" attribute.
            (function() {
                var _owa = document.createElement('script');
                _owa.type = 'text/javascript';
                _owa.async = true;
                _owa.src = $this.url + 'modules/base/js/owa.tracker-combined-min.js';
                var _owa_s = document.getElementsByTagName('script')[0];
                _owa_s.parentNode.insertBefore(_owa, _owa_s);
            }());
        },

        subscribe: function(root, stream, path) {
            var $this = this;

            // Override everything from the URI except the protocol and host.
            base_url = this.location.protocol + '//' + this.location.host;
            base_url += '/' + path;

            $(root).bind(stream, function (e, state) {
                url = base_url + state;
                owa_cmds.push(['setPageType', 'state']);
                owa_cmds.push(['setPageTitle', state]);
                owa_cmds.push(['trackPageView', url]);
            });
        }

    };

    // Initialize OWA.  An URL to OWA and a site ID must be provided.  If
    // page_view is true, a page view will be immediately tracked.
    $.fn.owa = function(url, site_id, page_view) {
        return this.each(function() {
            $.owa.init(url, site_id, page_view);
            return this;
        });
    };

    // Subscribes to a stream of events at the element.  A path must be
    // specified, to which a suffix will be added by the event.  This will
    // replace the actual path in the URI completely.
    $.fn.owa_subscribe = function(stream, path) {
        return this.each(function() {
            $.owa.subscribe(this, stream, path);
            return this;
        });
    };

})(jQuery);

odoo.define('glossary.search_terms', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SearchTerms = publicWidget.Widget.extend({
        selector: '.search-bar input',
        events: {
            'keyup': '_onKeyUp',
        },
        _onKeyUp: function (ev) {
            var query = ev.currentTarget.value.toLowerCase();
            $('.alphabet-table tbody tr').each(function () {
                var $row = $(this);
                var term = $row.find('td:nth-child(2)').text().toLowerCase();
                if (term.includes(query)) {
                    $row.show();
                } else {
                    $row.hide();
                }
            });
        },
    });
});

odoo.define('glossary.glossary', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.Glossary = publicWidget.Widget.extend({
        selector: '.glossary-container',

        start: function() {
            this._setupAccordion();
            this._setupLetterNavigation();
            return this._super.apply(this, arguments);
        },

        _setupAccordion: function() {
            var $headers = this.$el.find('.glossary-term-header');
            
            $headers.on('click', function() {
                var $term = $(this).closest('.glossary-term');
                var $content = $term.find('.glossary-term-content');
                
                // Cerrar todos los términos
                $term.siblings('.glossary-term').removeClass('active')
                    .find('.glossary-term-content').css('max-height', 0);
                
                // Alternar el término actual
                $term.toggleClass('active');
                $content.css('max-height', $term.hasClass('active') ? $content[0].scrollHeight + 'px' : 0);
            });
        },

        _setupLetterNavigation: function() {
            var self = this;
            
            this.$el.find('.glossary-nav-letter').on('click', function(e) {
                e.preventDefault();
                var letter = $(this).data('letter');
                var $targetSection = self.$el.find('#' + letter);
                
                if ($targetSection.length) {
                    $('html, body').animate({
                        scrollTop: $targetSection.offset().top - 100
                    }, 500);
                }
            });
        }
    });

    return {
        Glossary: publicWidget.registry.Glossary
    };
});
odoo.define("pos_credit.GobCreditTerms", function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');

    var CreditTermsPosPopup = PopupWidget.extend({
        template: 'CreditTermsPosPopup',
        show: function (options) {
            var self = this;
            self._super(options);
        }
    });

    gui.define_popup({
        name: 'credit_terms_pos_popup',
        widget: CreditTermsPosPopup
    });
    
});
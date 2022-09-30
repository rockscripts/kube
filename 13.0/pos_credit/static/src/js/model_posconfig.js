odoo.define("pos_credit.GobCreditTermsPosConfig", function (require) {
    "use strict";
    var models = require("point_of_sale.models");

    models.load_fields('pos.config', 'payment_terms_cuotes_range');
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        initialize: function (attr, options) {
            models.load_models({
                model: 'pos.config',
                fields: ['payment_terms_cuotes_range'],
                loaded: function (self) {
                    console.log(self);
                },
            });
            _super_order.initialize.call(this, attr, options);
        },
        set_payment_terms_cuotes_range: function (payment_terms_cuotes_range) {
            this.payment_terms_cuotes_range = payment_terms_cuotes_range;
            this.trigger('change', this);
        },
        get_payment_terms_cuotes_range: function () {
            return this.payment_terms_cuotes_range;
        },
    });
});
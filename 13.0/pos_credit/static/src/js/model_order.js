odoo.define("pos_credit.GobCreditTermsOrderModels", function (require) {
    "use strict";
    var models = require("point_of_sale.models");
    // values [without_credit, full_credit, parcial_credit]
    models.load_fields('pos.order', 'business_transaction_type');
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        initialize: function (attr, options) {
            models.load_models({
                model: 'pos.order',
                fields: ['business_transaction_type'],
                loaded: function (self) {},
            });

            _super_order.initialize.call(this, attr, options);

            this.business_transaction_type = this.business_transaction_type || 'without_credit';
        },
        set_business_transaction_type: function (business_transaction_type) {
            this.business_transaction_type = business_transaction_type;
            this.trigger('change', this);
        },
        get_business_transaction_type: function () {
            return this.business_transaction_type;
        }, 
        saveChanges: function () {
            this.business_transaction_type = this.get_business_transaction_type();
            _super_order.saveChanges.call(this, arguments);
        },
        clone: function () {
            var order = _super_order.clone.call(this);
            order.business_transaction_type = this.business_transaction_type;
            return order;
        },
        export_as_JSON: function () {
            var order = _super_order.export_as_JSON.call(this);
            order.business_transaction_type = this.business_transaction_type;
            return order;
        },
        export_for_printing: function () {
            var order = _super_order.export_for_printing.apply(this, arguments);
            order.business_transaction_type = this.get_business_transaction_type();
            return order;
        },
        init_from_JSON: function (json) {
            this.business_transaction_type = json.business_transaction_type;
            return _super_order.init_from_JSON.call(this, json);
        }      
    });
});
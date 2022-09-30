odoo.define("pos_credit.GobCreditTermsPaymentLine", function (require) {
    "use strict";
    var models = require("point_of_sale.models");

    models.load_fields('account.bank.statement.line', 'is_credit');
    models.load_fields('account.bank.statement.line', 'fixed_period');
    models.load_fields('account.bank.statement.line', 'payment_terms');
    models.load_fields('account.bank.statement.line', 'payment_terms_cuotes');
    models.load_fields('account.bank.statement.line', 'payment_terms_period');
    
    var _super_payment_line = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({

        initialize: function (attr, options) {
            models.load_models({
                model: 'account.bank.statement.line',
                fields: [
                    'is_credit',
                    'fixed_period',
                    'payment_terms',                    
                    'payment_terms_cuotes',
                    'payment_terms_period'
                ],
                loaded: function (self) { },
            });

            _super_payment_line.initialize.call(this, attr, options);

            this.is_credit = this.is_credit || false;
            this.fixed_period = this.fixed_period || true;
            this.payment_terms = this.payment_terms || null;
            this.payment_terms_cuotes = this.payment_terms_cuotes || 0;
            this.payment_terms_period = this.payment_terms_period || null;

        },
        set_is_credit: function (is_credit) {
            this.is_credit = is_credit;
            this.trigger('change', this);
        },
        get_is_credit: function () {
            return this.is_credit;
        },
        set_fixed_period: function (fixed_period) {
            this.fixed_period = fixed_period;
            this.trigger('change', this);
        },
        get_fixed_period: function () {
            return this.fixed_period;
        },
        set_payment_terms: function (payment_terms) {
            this.payment_terms = payment_terms;
            this.trigger('change', this);
        },
        get_payment_terms: function () {
            return this.payment_terms;
        },
        set_payment_terms_cuotes: function (payment_terms_cuotes) {
            this.payment_terms_cuotes = payment_terms_cuotes;
            this.trigger('change', this);
        },
        get_payment_terms_cuotes: function () {
            return this.payment_terms_cuotes;
        },
        set_payment_terms_period: function (payment_terms_period) {
            this.payment_terms_period = payment_terms_period;
            this.trigger('change', this);
        },
        get_payment_terms_period: function () {
            return this.payment_terms_period;
        },
        can_be_merged_with: function (order) {
            if (order.get_is_credit() !== this.get_is_credit()) {
                return false;
            }
            else if (order.get_fixed_period() !== this.get_fixed_period()) {
                return false;
            }
            else if (order.get_payment_terms() !== this.get_payment_terms()) {
                return false;
            }
            else if (order.get_payment_terms_cuotes() !== this.get_payment_terms_cuotes()) {
                return false;
            }
            else if (order.get_payment_terms_period() !== this.get_payment_terms_period()) {
                return false;
            }
            else {
                return _super_payment_line.can_be_merged_with.apply(this, arguments);
            }
        },
        saveChanges: function () {
            this.is_credit = this.get_is_credit();
            this.fixed_period = this.get_fixed_period();
            this.payment_terms = this.get_payment_terms();
            this.payment_terms_cuotes = this.get_payment_terms_cuotes();
            this.payment_terms_period = this.get_payment_terms_period();
            this.credit_percent_charge = this.get_credit_percent_charge();
            this.credit_initial_total_amount = this.get_credit_initial_total_amount();
            _super_payment_line.saveChanges.call(this, arguments);
        },
        clone: function () {
            var payment_line = _super_payment_line.clone.call(this);
            payment_line.is_credit = this.is_credit;
            payment_line.fixed_period = this.fixed_period;
            payment_line.payment_terms = this.payment_terms;
            payment_line.payment_terms_cuotes = this.payment_terms_cuotes;
            payment_line.payment_terms_period = this.payment_terms_period;            
            return payment_line;
        },
        export_as_JSON: function () {
            var payment_line = _super_payment_line.export_as_JSON.call(this);
            payment_line.is_credit = this.is_credit;
            payment_line.fixed_period = this.fixed_period;
            payment_line.payment_terms = this.payment_terms;
            payment_line.payment_terms_cuotes = this.payment_terms_cuotes;
            payment_line.payment_terms_period = this.payment_terms_period;
            return payment_line;
        },
        export_for_printing: function () {
            var payment_line = _super_payment_line.export_for_printing.apply(this, arguments);
            payment_line.is_credit = this.get_is_credit();
            payment_line.fixed_period = this.get_fixed_period();
            payment_line.payment_terms = this.get_payment_terms();
            payment_line.payment_terms_cuotes = this.get_payment_terms_cuotes();
            payment_line.payment_terms_period = this.get_payment_terms_period();
            return payment_line;
        },
        init_from_JSON: function (json) {
            this.is_credit = json.is_credit;
            this.fixed_period = json.fixed_period;
            this.payment_terms = json.payment_terms;
            this.payment_terms_cuotes = json.payment_terms_cuotes;
            this.payment_terms_period = json.payment_terms_period;
            return _super_payment_line.init_from_JSON.call(this, json);
        }
    });
});
odoo.define("pos_credit.GobCreditTermsPaymentScreen", function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');    

    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog');    
    
    screens.PaymentScreenWidget.include({
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
        },
        click_paymentmethods: function () {
            this._super.apply(this, arguments);
        },
        renderElement: function () {
            var self = this;
            this._super();
            this.$('div.paymentmethod').click(function () {
                self.init_credit_payment(self.$(this).attr("data-id"));
            });
        },
        init_credit_payment: function (id) {
            var self = this;

            console.log('init_credit_payment id');
            console.log(id);

            rpc.query({
                model: 'account.journal',
                method: 'get_journal_payment',
                args: [id],
            }, {
                timeout: 7500,
            }).then(function (journal) {
                var order = self.pos.get_order();
                var _name = String($('.paymentmethod[data-id=' + String(id) + ']').text()).trim();
                var due = String($('table.paymentlines').find('tr.paymentline').last().find('td').first().text()).trim();
                var tendered = parseFloat(self.text_to_float(due));
                // set tendered value as line due
                $('table.paymentlines').find('tr.paymentline').last().find('.col-tendered').text(due);
                order.selected_paymentline.set_amount(tendered);
                console.log('init_credit_payment');
                console.log(tendered);
                if (parseFloat(tendered) > 0) {
                    console.log(journal);
                    console.log(journal[0].for_credit);
                    console.log(Boolean(journal[0].for_credit));
                    if (journal) {                        
                        if (journal[0].for_credit == "True" || Boolean(journal[0].for_credit)) {                                
                            self.pos.gui.show_popup('credit_terms_pos_popup', {
                                title: _name,
                                confirm: function (value) {
                                    self.build_payment_information();
                                    $('#credit_initial_total_amount').val(parseFloat(tendered));
                                }
                            });
                            self.populate_credit_form();
                            self.set_popup_events();
                            self.set_credit_total_amount(self.format_currency(tendered));
                        }
                    }
                }
                else {}
            });
        },
        build_payment_information: function () {
            var self = this;

            self.credit_form_validation();

            var pos_order = self.pos.get_order();
            var fixed_period = $("#fixed_period").prop("checked");
            var payment_terms_cuotes = $("#payment_terms_cuotes").val();
            var payment_terms_period = $("#payment_terms_period").val();
            
            var static_terms = {};

            static_terms['is_credit'] = true;
            pos_order.selected_paymentline.set_is_credit(static_terms['is_credit']);

            static_terms['fixed_period'] = fixed_period;
            pos_order.selected_paymentline.set_fixed_period(static_terms['fixed_period']);

            static_terms['payment_terms_cuotes'] = payment_terms_cuotes;
            pos_order.selected_paymentline.set_payment_terms_cuotes(static_terms['payment_terms_cuotes']);

            static_terms['payment_terms_period'] = payment_terms_period;
            pos_order.selected_paymentline.set_payment_terms_period(static_terms['payment_terms_period']);

            if (String(fixed_period) == String("false")) {
                var dynamic_terms = [];
                $(".container_dinamic_terms .row_custom_term").each(function () {
                    var term = {
                        custom_term_reazon: $(this).find('.custom_term_reazon').val(),
                        custom_term_date: $(this).find('.custom_term_date').val(),
                        custom_term_amount: $(this).find('.custom_term_amount').val(),
                    };
                    dynamic_terms.push(term);
                });
                pos_order.set_payment_terms(dynamic_terms);
            }

            pos_order = self.pos.get_order();
        },
        remove_payment_line: function (_id, paymentLines) {
            if (paymentLines) {
                paymentLines.forEach(function (line, index) {
                    if (String(line.cid).trim() == String(_id).trim()) {
                        self.pos.get_order().remove_paymentline(line);
                    }
                });
                $("tr.paymentline").last().remove();
            }
        },
        populate_credit_form: function () {
            var self = this;
            var params = {};
            rpc.query({
                model: 'pos.order',
                method: 'populate_credit_form',
                args: [null, self.pos.config.id],
            }, {
                timeout: 7500,
            }).then(function (data) {
                if (data) {
                    var range = data.period_max_range;
                    var options = String();
                    for (var i = 1; i <= range; i++) {
                        options = String(options) + String("<option value='") + String(i) + "'>" + String(i) + String("</option>");
                    }
                    $("#payment_terms_cuotes").html(options);
                    var payment_terms_list = data.account_payment_terms_list;
                    var options = String();
                    if (payment_terms_list) {
                        payment_terms_list.forEach(function (term, index) {
                            if (parseInt(term.days)) {
                                options = String(options) + String("<option value='") + String(term.id) + "' days='" + String(term.days) + "' option='" + String(term.option) + "' >" + String(term.name) + String("</option>");
                            }
                        });
                        $("#payment_terms_period").html(options);
                    }
                    $("#fixed_period").prop('checked', true);
                }
            });
        },
        set_popup_events: function()
        {
            var self = this;
            var order = self.pos.get_order();

            $('#is_credit').on('click', function (event) {
                var _property = $(this).prop('checked');
                if(String(_property)==String("true"))
                {
                    $("#is_credit").prop('checked', true);
                    order.selected_paymentline.set_is_credit(true);
                }
                else
                {
                    $("#is_credit").prop('checked', false);
                    order.selected_paymentline.set_is_credit(false);
                }
                
            });

            $('#fixed_period').on('click', function (event) {
                var _property = $(this).prop('checked');
                if(String(_property)==String("true"))
                {
                    $("#fixed_period").prop('checked', true);
                    order.selected_paymentline.set_is_credit(true);
                    $("tr.tr_credit_total_amount_left").fadeOut();
                }
                else
                {
                    $("#fixed_period").prop('checked', false);
                    order.selected_paymentline.set_is_credit(false);
                    $("tr.tr_credit_total_amount_left").fadeIn();
                }
                
            });            

            $(document).on('blur', 'input.custom_term_amount', function (event) {
                event.preventDefault();
                var credit_total_custom_term_amount = $(this).val();
                var lines_total_amount = self.get_total_lines();
                if(parseFloat(credit_total_custom_term_amount) < parseFloat(lines_total_amount))
                {

                }
                else if(parseFloat(credit_total_custom_term_amount) > parseFloat(lines_total_amount))
                {
                    $(this).val(0);
                }
                self.set_credit_amount_left();                
            });                        
        },
        set_credit_total_amount: function(tendered)
        {
            var credit_total_amount = window.setInterval(function(){
                if($("b.credit_total_amount").length > 0)
                {                                        
                    $("b.credit_total_amount").text(tendered);
                    clearInterval(credit_total_amount);
                }
            }, 5);
        },
        init_date: function (_element) {
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0');
            var yyyy = today.getFullYear();
            today = yyyy + '-' + mm + '-' + dd;

            _element.datepicker({
                dateFormat: 'yy-mm-dd',
                changeYear: true,
                minDate: new Date(1950, 10 - 1, 25),
                maxDate: new Date(2030, 1, 1),
                yearRange: '1950:' + String(yyyy),
            }).val(today);
        },
        credit_form_validation: function () {

        },
        // allow just one credit term line by method
        check_payment_line: function (payment_method_name) {
            var check_payment_line = false;
            $('table.paymentlines td.col-name').each(function (index, element) {
                if (String(payment_method_name).trim() == String($(element).text().trim())) {
                    if (index < ($('table.paymentlines td.col-name').length - 1)) {
                        Dialog.alert(null, "No es posible agregar un nuevo término de pago para créditos.", { "title": "Pago a crédito" });
                        check_payment_line = true;
                        return check_payment_line;
                    }
                }
            });
            return check_payment_line;
        },        
        check_totals: function () {
            var self = this;
            var can_add = true;
            var total_amount = self.get_total_terms_amount();
            var lines_total_amount = self.get_total_lines();

            if (parseFloat(total_amount) == parseFloat(lines_total_amount)) {
                can_add = false;
            }
            else if (parseFloat(total_amount) < parseFloat(lines_total_amount)) {
                can_add = true;
            }
            else if (parseFloat(total_amount) > parseFloat(lines_total_amount)) {
                can_add = false;
            }
            else {
                can_add = false;
            }
            return can_add;
        },
        get_total_lines: function () {
            var self = this;
            var total_amount = 0;
            var order = self.pos.get_order();
            var order_lines = order.get_orderlines();
            order_lines.forEach(function (line, index) {
                total_amount = parseFloat(total_amount) + parseFloat(line.price);
            });
            return total_amount;
        },
        get_total_terms_amount: function () {
            var total_amount = 0;
            if ($('.container_dinamic_terms .custom_term_amount').length >= 1) {
                $('.container_dinamic_terms .custom_term_amount').each(function () {

                    var _amount = $(this).val();
                    total_amount = parseFloat(total_amount) + parseFloat(_amount);
                });
            }
            return total_amount;
        },
        set_credit_amount_left: function () {
            var self = this;
            var total_lines_amount = self.get_total_lines();
            var total_terms_amount = self.get_total_terms_amount();

            var difference = parseFloat(total_lines_amount) - parseFloat(total_terms_amount);
            if (difference <= 0) {
                $(".credit_total_amount_left").text(0.0);
                var _custom_term_amount_element = $(".container_dinamic_terms").find('.row_custom_term').last().find('input.custom_term_amount');
                var last_amount = _custom_term_amount_element.val();
                last_amount = last_amount - (difference * (-1));
                _custom_term_amount_element.val(last_amount);
            }
            else {
                $(".credit_total_amount_left").text(difference);
            }

            return difference;
        },
        text_to_float: function (float) {
            if (!float) {
                return '';
            };

            //Index of first comma
            const posC = float.indexOf(',');

            if (posC === -1) {
                //No commas found, treat as float
                return float;
            };

            //Index of first full stop
            const posFS = float.indexOf('.');

            if (posFS === -1) {
                //Uses commas and not full stops - swap them (e.g. 1,23 --> 1.23)
                return float.replace(/\,/g, '.');
            };

            //Uses both commas and full stops - ensure correct order and remove 1000s separators
            return ((posC < posFS) ? (float.replace(/\,/g, '')) : (float.replace(/\./g, '').replace(',', '.')));
        },
        key_interacion: function (_key, _element) {
            var _current_value = _element.val();
            var _new_value = String(_current_value) + String(_key);
            if (_key == "Backspace") {
                var _input_length = String(_current_value).length;
                if (_input_length > 0) {
                    var _new_value = String(_current_value).substr(0, _input_length - 1);
                    _element.val(parseInt(_new_value));
                    if (parseInt(_new_value) > 0) {
                        _element.val(parseInt(_new_value));
                    }
                    else {
                        _element.val(0);
                    }
                }
            } else {
                if (parseInt(_new_value) > 0) {
                    _element.val(parseInt(_new_value));
                }
                else {
                    _element.val(0);
                }
            }
        },
        key_interacion_characters: function (_key, _element) {
            var _current_value = _element.val();
            var _new_value = String(_current_value) + String(_key);
            if (_key == "Backspace") {
                var _input_length = String(_current_value).length;
                if (_input_length > 0) {
                    var _new_value = String(_current_value).substr(0, _input_length - 1);
                    _element.val(String(_new_value));
                }
            } else {
                _element.val(String(_new_value));
            }
        },
        key_interacion_money: function (_key, _element) {
            var _current_value = _element.val();
            var _new_value = String(_current_value) + String(_key);
            if (_key == "Backspace") {
                var _input_length = String(_current_value).length;
                if (_input_length > 0) {
                    var _new_value = String(_current_value).substr(0, _input_length - 1);
                    if (parseFloat(_new_value) > 0) {
                        _element.val(parseFloat(_new_value));
                    }
                    else {
                        _element.val(0);
                    }
                }
            } else {
                if (parseFloat(_new_value) > 0) {
                    _element.val(parseFloat(_new_value));
                }
                else {
                    _element.val(0);
                }
            }
        },        
    });
});
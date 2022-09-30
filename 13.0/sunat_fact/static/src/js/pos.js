odoo.define('sunat_fact.SunatPOS', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var models = require("point_of_sale.models");
    var rpc = require('web.rpc');
    var Dialog = require('web.Dialog'); 

    models.load_fields('pos.config', 'sunat_total_letters');
    models.load_fields('pos.config', 'qr_image');

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend(
        {
            initialize: function (session, attributes) {
                var self = this;
                var POS_MODEL = PosModelSuper.prototype.initialize.apply(this, arguments);
                return POS_MODEL;
            },

        });

    screens.ReceiptScreenWidget.include({
        get_receipt_render_env: function () {
            this.pos.last_receipt_render_env = this._super();
            var _data = this.electronic_invoice_order_receipt_data();
            this.pos.last_receipt_render_env['electronic_invoice'] = _data;
            console.log("get_receipt_render_env");
            console.log(this.pos.last_receipt_render_env['electronic_invoice']);
            return this.pos.last_receipt_render_env;
        },
        electronic_invoice_order_receipt_data: function () {
            var order = this.pos.get_order();
            var orderID = order.name;
            if (orderID != "") {

                var data = { 'params': { 'orderID': orderID } };
                var result = [];
                $.ajax({
                    type: 'POST',
                    url: '/sunatefact/get_invoice_ordered',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: 'application/json',
                    async: false,
                    success: function (response) {
                        if (response.result) {
                            result = response.result;
                        }
                        return result;
                    }
                });
                return result
            } else {}
        },
    });

    screens.ClientListScreenWidget.include({
        init: function (parent, options) {
            var self = this;
            self._super(parent, options);
            $(document).ready(function () {
                self.event_handle();
                self.execute_location();
            });
        },
        event_handle: function () {
            var self = this;
            
            $(document).on('click', 'div.edit-buttons div.edit', function () {
                self.set_partner_default();
            });
            $('body').on('change', 'select[name="country_id"]', function () {
                self.execute_location();
            });
            $('body').on('change', 'select[name="state_id"]', function () {
                self.execute_location();
            });
            $('body').on('change', 'select[name="province_id"]', function () {
                self.execute_location();
            });
            $('body').on('change', 'select[name="district_id"]', function () {
                self.execute_location();
            });
            $('body').on("blur", "input.vat", function () {
                self.set_country_identification();
            });

            $('body').on("change", "select.sunat_tipo_documento", function () {
                var vat = $("input.vat").val();
                if (vat != "") {
                    self.set_country_identification();
                }
            });
        },
        set_partner_default() {
            var self = this;
            var partner_id = $('input[name="id"]').val();
            rpc.query({
                model: 'res.partner',
                method: 'search_partner_default',
                args: [partner_id],
            }).then(function (partner) {
                if (partner) {
                    var _partner_id = partner[0];

                    $("select[name='sunat_tipo_documento']").val(_partner_id['sunat_tipo_documento']);

                    self.execute_location();

                    $("select[name='state_id']").val(_partner_id['state_id']);

                    self.execute_location();

                    $("select[name='province_id']").val(_partner_id['province_id']);

                    self.execute_location();

                    $("select[name='district_id']").val(_partner_id['district_id']);

                    self.execute_location();
                }
            });
        },
        set_country_identification() {
            var self = this;
            var documentinvoice_sequence_number_next = $("input.vat").val();
            var documentType = $("select.pos_sunat_tipo_documento").val();
            var data = { "params": { "doc_num": documentinvoice_sequence_number_next, "doc_type": documentType } }
            $.ajax({
                type: "POST",
                url: '/sunatefact/get_ruc',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function (response) {
                    if (response.result.status == "OK") {
                        var name = String();
                        if (response.result.nombre_comercial === '-') {
                            name = response.result.name;
                        }
                        else {
                            name = response.result.nombre_comercial;
                        }

                        name = String(name).replace('"', '').replace('"', '').replace('"', '').replace('"', '');

                        if (parseInt(documentType) == 6) {
                            $("input[name='name']").val(name);
                            $("input[name='street']").val(response.result.address);
                            $("select[name='province_id']").val(response.result.provincia);
                            $("input[name='ubigeo']").val(response.result.ubigeo);
                            $("input[name='is_company']").val('TRUE');
                        } else if (parseInt(documentType) == 1) {
                            $("input[name='name']").val(response.result.name);
                            $("input[name='is_company']").val('FALSE');
                        }
                        self.set_location(response.result.departamento, response.result.provincia, response.result.distrito, response.result.ubigeo)
                    } else {
                        Dialog.alert(null, "Sin registros.", { "title": "Consulta de usuario" });
                    }
                }
            });
        },
        execute_location: function () {
            var self = this;
            var country_id = $("select[name='country_id']").val();
            var state_id = ($("select[name='state_id']").val() != null) ? $("select[name='state_id']").val() : 0
            var province_id = ($("select[name='province_id']").val() != null) ? $("select[name='province_id']").val() : 0
            var district_id = ($("select[name='district_id']").val() != null) ? $("select[name='district_id']").val() : 0
            self.populate_location(country_id, state_id, province_id, district_id);
        },
        set_location: function (state, province, district, ubigeo) {
            var self = this;
            const capitalize = (s) => {
                if (typeof s !== 'string') return ''
                return s.charAt(0).toUpperCase() + s.slice(1)
            }
            var country_id = $("select[name='country_id']").val();
            var data = { "params": { "country_id": country_id, "state": state, "province": province, "district": district, "ubigeo": ubigeo } }
            $.ajax({
                type: "POST",
                url: '/sunatefact/set_location',
                data: JSON.stringify(data),
                dataType: 'json',
                contentType: "application/json",
                async: false,
                success: function (response) {
                    if (response.result) {
                        var state = response.result.state
                        var province = response.result.province
                        var district = response.result.district

                        self.execute_location();

                        $("select[name='state_id']").val(state.id);

                        self.execute_location();

                        $("select[name='province_id']").val(province.id);

                        self.execute_location();

                        $("select[name='district_id']").val(district.id);

                        self.execute_location();

                    }
                }
            });
        },
        populate_location: function (country_id, state_id, province_id, district_id) {
            try {
                if (country_id == '' || country_id == null || country_id == NaN)
                    country_id = 0;
                if (state_id == '' || state_id == null || state_id == NaN)
                    state_id = 0;
                if (province_id == '' || province_id == null || province_id == NaN)
                    province_id = 0;
                if (district_id == '' || district_id == null || district_id == NaN)
                    district_id = 0;

                const capitalize = (s) => {
                    if (typeof s !== 'string') return ''
                    return s.charAt(0).toUpperCase() + s.slice(1)
                };
                var data = { "params": { "country_id": country_id, "state_id": state_id, "province_id": province_id, "district_id": district_id } }
                $.ajax({
                    type: "POST",
                    url: '/sunatefact/populate_location',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: "application/json",
                    async: false,
                    success: function (response) {
                        console.log('populate_location')
                        console.log(response)
                        if (response.result.country_id > 0) {
                            var state_options = "<option value='0'>seleccionar</option>";
                            var province_options = "<option value='0'>seleccionar</option>";
                            var district_options = "<option value='0'>seleccionar</option>";
                            if (response.result.states) {
                                try {
                                    var states = response.result.states
                                    states.forEach(function (state, index) {
                                        state_options += "<option value='" + state.id + "' code='" + state.code + "'>" + capitalize(String(state.name)) + "</option>";
                                    });
                                    $("select[name='state_id']").html("");
                                    $("select[name='state_id']").append(state_options);
                                }
                                catch (error) {
                                }

                                try {
                                    var provinces = response.result.provinces
                                    provinces.forEach(function (province, index) {
                                        province_options += "<option value='" + province.id + "' code='" + province.code + "'>" + capitalize(String(province.name)) + "</option>";
                                    });
                                    $("select[name='province_id']").html("");
                                    $("select[name='province_id']").append(province_options);
                                }
                                catch (error) {
                                }

                                try {
                                    var districts = response.result.districts
                                    districts.forEach(function (district, index) {
                                        district_options += "<option value='" + district.id + "' code='" + district.code + "'>" + capitalize(String(district.name)) + "</option>";
                                    });

                                    $("select[name='district_id']").html("");
                                    $("select[name='district_id']").append($(district_options)).val(district_id);

                                }
                                catch (error) { }

                            }

                            $("select[name='state_id']").val(state_id);
                            $("select[name='province_id']").val(province_id);
                            $("select[name='district_id']").val(district_id);
                            var _code = $("select[name='district_id'] option:selected").attr('code');
                            $("input[name='ubigeo']").val(_code);
                            $("input[name='zip']").val(_code);

                        }
                    }
                });
            }
            catch (error) { console.log(error); }
        },

    });

});
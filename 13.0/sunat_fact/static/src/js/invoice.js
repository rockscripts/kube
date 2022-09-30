odoo.define('module.Sunat', function (require) {
    "use strict";

    console.log("HOLA MUNDO")
    var rpc = require('web.rpc');

    $(document).ready(function () {
        var flagLoaded = false;
        var index_Exc = 0;
        var ubigeoInterval = setInterval(function () {
            if($("select[name='district_id']").length>0)
            {
                $(document).on("click", ".new-customer", function () {
                    $(".pos_sunat_tipo_documento").val(6) // RUC by default
                    var country_id = $("select.client-address-country").val();
                    populate_location(country_id, 0, 0, 0);
                });
        
                $(document).on("change", "select[name='state_id']", function () {
                    var country_id = $("select[name='country_id']").val();
                    var state_id = ($("select[name='state_id']").val() != null) ? $("select[name='state_id']").val() : 0
                    var province_id = ($("select[name='province_id']").val() != null) ? $("select[name='province_id']").val() : 0
                    var district_id = ($("select[name='district_id']").val() != null) ? $("select[name='district_id']").val() : 0
                    populate_location(country_id, state_id, province_id, district_id);
                });
                $(document).on("change", "select[name='province_id']", function () {
                    var country_id = $("select[name='country_id']").val();
                    var state_id = ($("select[name='state_id']").val() != null) ? $("select[name='state_id']").val() : 0
                    var province_id = ($("select[name='province_id']").val() != null) ? $("select[name='province_id']").val() : 0
                    var district_id = ($("select[name='district_id']").val() != null) ? $("select[name='district_id']").val() : 0
                    populate_location(country_id, state_id, province_id, district_id);
                });
                $(document).on("change", "select[name='district_id']", function () {
                    var country_id = $("select[name='country_id']").val();
                    var state_id = ($("select[name='state_id']").val() != null) ? $("select[name='state_id']").val() : 0
                    var province_id = ($("select[name='province_id']").val() != null) ? $("select[name='province_id']").val() : 0
                    var district_id = ($("select[name='district_id']").val() != null) ? $("select[name='district_id']").val() : 0
                    populate_location(country_id, state_id, province_id, district_id);
                });
                $(document).on("change", "select[name='country_id']", function () {
                    var country_id = $("select[name='country_id']").val();
                    var state_id = ($("select[name='state_id']").val() != null) ? $("select[name='state_id']").val() : 0
                    var province_id = ($("select[name='province_id']").val() != null) ? $("select[name='province_id']").val() : 0
                    var district_id = ($("select[name='district_id']").val() != null) ? $("select[name='district_id']").val() : 0
                    populate_location(country_id, state_id, province_id, district_id);
                });
                $(document).on("change", "select[name='district_id']", function () {
                    var district_id = $("select[name='district_id']").val()
                    var district_code = $('option:selected', $("select[name='district_id']")).attr('code');
                    //alert(district_id+" -- "+district_code)
                    $("input[name='zip']").val(district_code);
                    $("input[name='ubigeo']").val(district_code);
                });
                $(document).on("click", ".client-details div.edit", function () {
                    var partner_id = $("input[name='partner_id']").val()
                    set_partner_location(partner_id)
                });
                
                clearInterval(ubigeoInterval);
            }
        
        },100 );

        setInterval(function () {

            
                if ($(".o_invoice_form").length > 0) 
                {
                    if($('.invoice-cancelled').hasClass('o_invisible_modifier') == false)
                    {
                        $("button[name=action_reverse]").fadeOut();
                        $("button[name=454]").fadeOut();
                        $(".o_statusbar_buttons button").each(function () 
                        {
                            var textButton = $(this).text();
                            if (textButton.toLowerCase() == String("+ Nota Débito").toLowerCase() || textButton.toLowerCase() == String("Add Debit Note").toLowerCase())
                                $(this).fadeOut();
                        });
                    } 
                }

            var nif_pos = $("span.label:contains('ID de Impuesto')");
            if(nif_pos)
            {
                nif_pos.text('NIF / RUC')
            }

            var invoice_invoice_sequence_number_next = $("span[name=name]").first().text();
            var firstPart = invoice_invoice_sequence_number_next.substring(0, 2);
            if (firstPart == "fd" || firstPart == "fc") {
                $("button[name=202]").fadeOut();
                $("button[name=202]").find("span").text("Agregar Nota");
                $("button[name=202]").text("Agregar Nota");
                $(".o_statusbar_buttons button").each(function () {
                    var textButton = $(this).text();
                    if (textButton.toLowerCase() == "emitir rectificativa" || textButton.toLowerCase() == "emitir nota")
                        $(this).fadeOut();
                });
            }
            if (firstPart == "BF") 
            {
                if ($(".o_invoice_form").length > 0) 
                {
                    $("button[name=action_reverse]").fadeOut();
                    $("button[name=454]").fadeOut();
                    $(".o_statusbar_buttons button").each(function () 
                    {
                        var textButton = $(this).text();
                        if (textButton.toLowerCase() == String("+ Nota Débito").toLowerCase() || textButton.toLowerCase() == String("Add Debit Note").toLowerCase())
                            $(this).fadeOut();
                    });
                }
            }

            if (firstPart == "F0") {
                if ($(".o_invoice_form").length > 0) {
                    if (index_Exc == 0) {
                        var intervalIdFV = setInterval(function () {
                            var invoice_invoice_sequence_number_next = $("span[name=name]").first().text();
                            var data = { "params": { 'invoice_invoice_sequence_number_next': invoice_invoice_sequence_number_next } }
                            $.ajax({
                                type: "POST",
                                url: '/sunatefact/can_create_notes',
                                data: JSON.stringify(data),
                                dataType: 'json',
                                contentType: "application/json",
                                async: false,
                                success: function (response) {

                                    if (response.result.found == true) {
                                        $("span[name=name]").first().css("color", "red")
                                        $("span[name=name]").first().css("opacity", "0.8")
                                        $("span[name=name]").first().append("<div class='invoice-cancelled'>Factura anulada con nota - " + response.result.name + "</div>");
                                        $("button[name=202]").fadeOut();
                                        $("button[name=action_reverse]").fadeOut();
                                        $("button[name=454]").fadeOut();
                                        $(".o_statusbar_buttons button").each(function () 
                                        {
                                            var textButton = $(this).text();
                                            if (textButton.toLowerCase() == "+ Nota Débito" || textButton.toLowerCase() == "Add Debit Note")
                                                $(this).fadeOut();
                                        });
                                    }

                                    // prevent second ajax call
                                    index_Exc++;
                                }
                            });
                        }, 500);
                    }
                }

            }

            var invoice_invoice_sequence_number_next = $("span[name=invoice_sequence_number_next]").text();
            var firstPart = invoice_invoice_sequence_number_next.substring(0, 2);

            if (firstPart == "FC" || firstPart == "FD") {
                $("button[name=202]").fadeOut();
                $(".o_statusbar_buttons button").each(function () {
                    var textButton = $(this).text();
                    if (textButton.toLowerCase() == "emitir rectificativa" || textButton.toLowerCase() == "emitir nota")
                        $(this).fadeOut();
                });
            }

            if (!flagLoaded) {
                $(document).on("blur", "input.vat", function () {
                    setClientDetailsByDocument();
                });
                $(document).on("change", "select.sunat_tipo_documento", function () {
                    var vat = $("input.vat").val();
                    if (vat != "")
                        setClientDetailsByDocument();
                });

                flagLoaded = true;
                $(document).on("click", ".payment-screen .button", function () {
                    if ($(this).hasClass("next")) {
                        // set_invoice_details_einvoicing();
                    }
                });

                $(document).on("click", ".new-customer", function () {
                    $(".pos_sunat_tipo_documento").val(6) // RUC by default
                    var country_id = $("select.client-address-country").val();
                    populate_location(country_id, 0, 0, 0);
                });

                $(document).on("click", ".js_invoice", function () {
                    if ($(this).hasClass("button")) {
                        var intervalIdInvoice = setInterval(function () {
                            var js_invoice = $(".js_invoice");
                            if (js_invoice.hasClass("highlight")) {
                                if ($(".journal-container-custom").length == 0) {
                                    $.ajax({
                                        type: "POST",
                                        url: '/sunatefact/get_invoice_ticket_journal',
                                        data: JSON.stringify({}),
                                        dataType: 'json',
                                        contentType: "application/json",
                                        async: false,
                                        success: function (response) {
                                            if (response.result.journals != null && response.result.journals != '') {
                                                var journals = response.result.journals;
                                                var pos_config = response.result.pos_config;
                                                var option = '';
                                                journals.forEach(function (journal, index) {
                                                    if (journal.id > 0)
                                                        option += '<option value="' + journal.id + '">' + journal.name + '</option>';
                                                });
                                                $(".payment-buttons").append("<div class='journal-container-custom'><label>Documento: </label><select id='journal_id' pos_id='" + pos_config.id + "' class='journal-pos-custom'>" + option + "</select><br><spam id='tipodocumentosec' class='popup popup-error'></spam></div>");
                                                //can't read classes from this addon default template definition, adding it on fire with jquery
                                                $(".journal-pos-custom").css("height", "38px");
                                                $(".journal-pos-custom").css("font-size", "16px");
                                                $(".journal-pos-custom").css("padding", "5px");
                                                $(".journal-pos-custom").css("margin-left", "0px");
                                                $(".journal-pos-custom").css("margin", "5px");
                                                $(".journal-container-custom").css("font-size", "18px");
                                                $("#journal_id").val(pos_config.invoice_journal_id);
                                                //if(pos_config.id=="1"){
                                                //                        var text="CREAR FACTURA";
                                                //                            document.getElementById('tipodocumentosec').innerText=text;
                                                //                                                }else{
                                                //                        var text="CREAR BOLETA";
                                                //                            document.getElementById('tipodocumentosec').innerText=text;
                                                //                }
                                            }

                                        }
                                    });
                                }
                                clearInterval(intervalIdInvoice);
                            }
                            clearInterval(intervalIdInvoice);
                        }, 100000);
                    }
                })

                $(document).on("change", "#journal_id", function () {
                    var intervalJournalSelect = setInterval(function () {
                        var pos_id = $("#journal_id").attr("pos_id");
                        var journal_new_id = $("#journal_id").val();
                        console.log(journal_new_id)
                        if (journal_new_id == "1") {
                            document.getElementById('tipodocumentosec').innerText = "CREAR FACTURA";
                        } else {
                            document.getElementById('tipodocumentosec').innerText = "CREAR BOLETA";
                        }
                        var data = { "params": { 'posID': pos_id, 'journalID': journal_new_id } }
                        //console.log(data)
                        $.ajax({
                            type: "POST",
                            url: '/sunatefact/update_current_pos_conf',
                            data: JSON.stringify(data),
                            dataType: 'json',
                            contentType: "application/json",
                            async: false,
                            success: function (qrImage64) {
                                clearInterval(intervalJournalSelect);
                            }
                        });
                    }, 1000);
                })

            }
            if ($('.pos-content').length > 0) {
                if ($('.modal').length > 0) {
                    if ($(".modal-body:contains('ESTADO: FAIL')"))
                        $(".modal").fadeOut();

                    var popUpDisplayed = $(".popups").find('.modal-dialog:not(.oe_hidden)');
                    var titleText = popUpDisplayed.find(".title").html();
                    popUpDisplayed.find(".title").hide();
                    popUpDisplayed.find(".body").html(titleText)
                }
            }
        }, 2500);



    })

    function setClientDetailsByDocument() {
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
                    var name = response.result.name;
                    if (response.result.nombre_comercial != '') {
                        name = response.result.nombre_comercial;
                    }
                    if (parseInt(documentType) == 6) {
                        $(".client-name").val(name);
                        $(".client-address-street").val(response.result.address);
                        $(".client-address-city").val(response.result.provincia);
                        $(".client-address-zip").val(response.result.ubigeo);
                        $("input[name='is_company']").val('TRUE');

                    } else if (parseInt(documentType) == 1) {
                        $(".client-name").val(response.result.name);
                        $("input[name='is_company']").val('FALSE');
                    }

                    set_location(response.result.departamento, response.result.provincia, response.result.distrito, response.result.ubigeo)
                } else {                    
                        swal({
                            title: "Consulta de usuario",
                            text: "Sin registros",
                            type: "warning",
                            showCancelButton: true,
                            cancelButtonText: "OK",
                            closeOnCancel: true
                        });
                }
            }
        });
    }

    function set_partner_location(id) {
        var data = { "params": { "id": id } }

        $.ajax({
            type: "POST",
            url: '/sunatefact/set_partner_location',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: "application/json",
            async: false,
            success: function (response) {
                if (response.result) {
                    var partner = response.result.partner;
                    console.log(partner)
                    var state_id = partner.state_id
                    var province_id = partner.province_id
                    var district_id = partner.district_id

                    var country_id = $("select[name='country_id']").val();

                    populate_location(country_id, state_id, province_id, district_id);
                }
            }
        });
    }

    function set_location(state, province, district, ubigeo) {
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

                    populate_location(country_id, 0, 0, 0);

                    $("select[name='state_id']").val(state.id);

                    var province_option_selected = "<option value='" + province.id + "' code='" + province.code + "'>" + capitalize(String(province.name)) + "</option>";
                    $("select[name='province_id']").html(province_option_selected)

                    var district_option_selected = "<option value='" + district.id + "' code='" + district.code + "'>" + capitalize(String(district.name)) + "</option>";
                    $("select[name='district_id']").html(district_option_selected);
                }
            }
        });
    }

    function populate_location(country_id, state_id, province_id, district_id) {
        const capitalize = (s) => {
            if (typeof s !== 'string') return ''
            return s.charAt(0).toUpperCase() + s.slice(1)
        }
        var data = { "params": { "country_id": country_id, "state_id": state_id, "province_id": province_id, "district_id": district_id } }
        $.ajax({
            type: "POST",
            url: '/sunatefact/populate_location',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: "application/json",
            async: false,
            success: function (response) {
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
                            $("select[name='district_id']").append(district_options);
                        }
                        catch (error) {
                        }

                    }
                    $("select[name='state_id']").val(state_id)
                    $("select[name='province_id']").val(province_id)
                    $("select[name='district_id']").val(district_id)
                }
            }
        });
    }
});
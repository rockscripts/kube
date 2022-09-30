# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo import http
from pprint import pprint
import time
from datetime import datetime
import hmac
import hashlib
import requests 
import json
import os
from odoo.http import request
from decimal import Decimal
import qrcode
import base64
import random
import sys
from io import BytesIO
import logging
_logger = logging.getLogger(__name__)

from sunatservice.sunatservice import Service

class account_move_pos(models.Model):

    _inherit = 'account.move'

    def post(self):
        urlPath = http.request.httprequest.full_path
        if 'payment/process' in urlPath:
            return super(account_move_pos, self).post()

        invoice_items = []       

        for invoice in self: 
            if invoice.partner_id.vat=="" or invoice.partner_id.vat==False:
               raise Warning(_("Por favor, establecer el documento del receptor"))

        eDocumentType = self.journal_id.code
        index = 0
        sunat_items = [] 
        totalVentaPedido = 0
        totalVenta = 0
        subTotalPedido = 0
        #impuestos
        tributos_globales = {}
        tributos = {}                

        processInvoiceAction = "fill_only"  

        res_config_settings = request.env['res.config.settings'].sudo().search([])        
        
        if(eDocumentType=="FAC" or eDocumentType=="INV"): 
            for invoice in self:
                sunat_request_type = invoice.company_id.sunat_request_type 

                if(sunat_request_type=="automatic"):
                    sunat_request_type = "Automatizada"
                    processInvoiceAction = "fill_only"
                else:
                    sunat_request_type = "Documento Validado"
                    processInvoiceAction = "fill_submit"

                self.env.cr.commit()
                self.env.cr.rollback()

                items = invoice.sudo().invoice_line_ids                
                
                for item in items:
                    item_tributos = []
                    subTotalVenta = ((item.price_unit * item.quantity))
                    
                    for tax in item.tax_ids:   

                        if(tax.amount_type=="fixed"):
                            impuesto = tax.amount * item.quantity                                                
                            monto_afectacion_tributo = ((impuesto))
                            if(bool(tax.price_include)==True):
                                monto_afectacion_tributo = subTotalVenta - ((subTotalVenta / ((float(impuesto)/100) + 1)))

                        if(tax.amount_type=="percent"):
                            impuesto = tax.amount                                      
                            monto_afectacion_tributo = ((subTotalVenta * (float(impuesto)/100)))

                            if(bool(tax.price_include)==True):
                                monto_afectacion_tributo = subTotalVenta - ((subTotalVenta / ((float(impuesto)/100) + 1)))

                        if(bool(tax.price_include)==True):
                            subTotalVenta -= monto_afectacion_tributo

                        totalVenta = subTotalVenta
                        totalVenta +=  monto_afectacion_tributo

                        item_tributo = {
                                            "codigo":tax.sunat_tributo,
                                            "porcentaje":tax.amount,
                                            "tipo_calculo":tax.amount_type, # percent:IGV... and fixed:plastic bags supported
                                            "montoAfectacionTributo":monto_afectacion_tributo,
                                            "total_venta":subTotalVenta,
                                            'tipoAfectacionTributoIGV': tax.sunat_tributo_afectacion_igv, # pendiente si es igv - catalogo 7. 
                                            'sistemaCalculoISC':tax.sunat_tributo_calculo_isc
                                                     #pendiente si es isc - catalogo 8 para codigo = 2000 ISC
                                       }

                        item_tributos.append(item_tributo) 

                    tributos_globales = self.add_global_tributes(item_tributos,tributos_globales)
                    price_unit = float(item.price_subtotal) / float(item.quantity)
                    sunat_item = {
                                    'id':str(item.product_id.id),
                                    'cantidad':str(item.quantity),
                                    "medidaCantidad":str(item.product_id.uom_id.sunat_unit_code),
                                    'descripcion':item.name,
                                    "precioUnidad":price_unit,
                                    'tipoPrecioVentaUnitario':self.get_sunat_product_type_price( item.product_id.id),  #instalar en ficha de producto catalogo 16    01 Precio unitario (incluye el IGV), 02 Valor referencial unitario en operaciones no onerosas                                        
                                    'clasificacionProductoServicioCodigo':self.get_sunat_product_code_classification( item.product_id.id),
                                    "subTotalVenta":subTotalVenta,
                                    'totalVenta':totalVenta, 
                                    "tributos":item_tributos,
                                    "descuento":[],

                                 }
                    sunat_items.append(sunat_item)
                    totalVentaPedido += float(totalVenta)
                    subTotalPedido += float(subTotalVenta)

            currentDateTime = datetime.now()
            currentTime = currentDateTime.strftime("%H:%M:%S")

            if(str(invoice.name) == '/'):
                next_sequence = invoice.journal_id.sequence_id._get_current_sequence()
                secuencia = str( str(next_sequence.prefix) + str(next_sequence.number_next_actual) ).split("-")
                secuencia_serie = secuencia[0]
                secuencia_consecutivo = secuencia[1]
            else:
                secuencia = str(invoice.name).split("-")
                secuencia_serie = secuencia[0]
                secuencia_consecutivo = secuencia[1]

            # Start data validation
            Vcompany_address = self.validate_address(invoice.company_id)
            if(bool(Vcompany_address["errors"])==True):
                raise Warning (str("Compañia emisora")+Vcompany_address["msn"])

            Vcompany_certificate = self.validate_certificate(invoice.company_id)
            if(bool(Vcompany_certificate["errors"])==True):
                raise Warning (str("Compañia emisora")+Vcompany_certificate["msn"])

            Vpartner_address = self.validate_address(invoice.partner_id)
            if(bool(Vpartner_address["errors"])==True):
                raise Warning (str("Cliente / Socio")+Vpartner_address["msn"])

            

            sunat_data = {
                                "serie": str(secuencia_serie),
                                "numero":str(secuencia_consecutivo),
                                "emisor":{
                                            "tipo_documento":invoice.company_id.sunat_tipo_documento,
                                            "nro":invoice.company_id.vat,
                                            "nombre":str(invoice.company_id.name).capitalize(),
                                            "direccion":str(invoice.company_id.street).capitalize(),
                                            "ciudad":str(Vcompany_address["address"]["province"]["name"]),
                                            "ciudad_sector":str(Vcompany_address["address"]["district"]["name"]),
                                            "departamento":str(invoice.company_id.state_id.name).capitalize(),
                                            "codigoPostal":invoice.company_id.zip,
                                            "codigoPais":invoice.company_id.country_id.code,
                                            "ubigeo":(str(invoice.company_id.ubigeo) if(invoice.company_id.ubigeo!=None) else str(invoice.company_id.zip))
                                         },
                                "receptor": {
                                                "tipo_documento":invoice.partner_id.sunat_tipo_documento,
                                                "nro":invoice.partner_id.vat,
                                                "nombre":str(invoice.partner_id.name).capitalize(),
                                                "direccion":str(invoice.partner_id.street).capitalize(),
                                                "ciudad":str(Vpartner_address["address"]["province"]["name"]),
                                                "ciudad_sector":str(Vpartner_address["address"]["district"]["name"]),
                                                "departamento":str(invoice.partner_id.state_id.name),
                                                "codigoPostal":invoice.partner_id.zip,
                                                "codigoPais":invoice.partner_id.country_id.code,
                                                "ubigeo":(str(invoice.partner_id.ubigeo) if(str(invoice.partner_id.ubigeo)!=None) else str(invoice.partner_id.zip))
                                            },
                                "fechaEmision":str(invoice.invoice_date).replace("/","-",3),
                                "fechaVencimiento":str(invoice.invoice_date_due).replace("/","-",3),
                                "horaEmision":currentTime,
                                "subTotalVenta":subTotalPedido,
                                "totalVentaGravada":totalVentaPedido,
                                "tipoMoneda":invoice.currency_id.name,
                                "items": sunat_items,
                                "tributos":tributos_globales,
                                "descuentos": {"globales": []},
                                "pagos":self.env['sunat.catalog'].sudo().get_payment(self),
                                "terminos_pagos": self.get_payment_terms(),
                                "sunat_sol": {
                                            "ruc":invoice.company_id.sol_ruc,
                                            'usuario':invoice.company_id.sol_username,
                                            'clave':invoice.company_id.sol_password,
                                            'certificado':{
                                                            'crt':invoice.company_id.cert_pem_filename,
                                                            'key':invoice.company_id.key_pem_filename,
                                                            'pass':invoice.company_id.key_pass,
                                                          }
                                         },
                                "accion": processInvoiceAction,
                                'licencia':"081OHTGAVHJZ4GOZJGJV"
                            } 

            _logger.warning('sunat_data')
            _logger.warning(sunat_data)
            
            serieConsecutivoString = secuencia_serie
            serieConsecutivo = secuencia_consecutivo
            currentDateTime = datetime.now()
            currentTime = currentDateTime.strftime("%H:%M:%S")

            xmlPath = os.path.dirname(os.path.abspath(__file__))+'/xml'
            
            SunatService = Service()
            SunatService.setXMLPath(xmlPath)
            SunatService.fileName = str(invoice.company_id.vat)+"-01-"+str(serieConsecutivoString)+"-"+str(serieConsecutivo)
            SunatService.initSunatAPI(invoice.company_id.api_mode, "sendBill")
            SunatResponse = SunatService.processInvoice(sunat_data)

            if 'xml_response' in SunatResponse:
                self.response_document = SunatResponse["xml_response"]
                self.response_document_filename = str("R_")+str(serieConsecutivoString)+"-"+str(serieConsecutivo)+str(".XML")

            if 'xml_signed' in SunatResponse:
                self.signed_document = SunatResponse["xml_signed"]
                self.signed_document_filename = str("F_")+str(serieConsecutivoString)+"-"+str(serieConsecutivo)+str(".XML")

            if 'xml_unsigned' in SunatResponse:
                self.unsigned_document = SunatResponse["xml_unsigned"]
                self.unsigned_document_filename = str("NF_")+str(serieConsecutivoString)+"-"+str(serieConsecutivo)+str(".XML")
            
            # generate qr for invoices and tickets in pos
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            qr = qrcode.QRCode(
                                version=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L,
                                box_size=20,
                                border=4,
                              )
            total_tributo_igv = self.get_sumatoria_tributo_igv(tributos_globales)            
            qr_code_text = str(sunat_data["emisor"]["nro"]) + str("|") + str(sunat_data["emisor"]["tipo_documento"]) + str("|") + str(sunat_data["serie"]) + str("|") + str(sunat_data["numero"]) + str("|") + str(total_tributo_igv) + str("|") + str(format(float(sunat_data["totalVentaGravada"]),'.2f')) + str("|") + str(sunat_data["fechaEmision"]) + str("|") + str(sunat_data["receptor"]["tipo_documento"]) + str("|") + str(sunat_data["receptor"]["nro"])
            qr.add_data(qr_code_text)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            self.qr_image = base64.b64encode(temp.getvalue())
            self.qr_in_report = True

            self.sunat_request_type = sunat_request_type
            self.sunat_total_letters = self.literal_price(totalVentaPedido)

            if 'status' in SunatResponse:
                if(SunatResponse["status"] == "OK"):                                                                                    
                    self.api_message = "ESTADO: "+str(SunatResponse["status"])+"\n"+"REFERENCIA: "+str(SunatResponse["body"]["referencia"]).replace("'",'"')+"\n"+" "+str(SunatResponse["body"]["description"]).replace("'",'"')
                    self.sunat_request_status = 'OK'
                    return super(account_move_pos, self).post()
                else:
                    self.sunat_request_status = 'FAIL'
                    self.api_message = "ESTADO: "+str(SunatResponse["status"])+"\n"+" "+str(SunatResponse["body"])+"\n"+"CÓDIGO ERROR: "+str(SunatResponse["code"])
                    #raise Warning("Generated")
                    return super(account_move_pos, self).post()
            else:
                return super(account_move_pos, self).post()

################################################################################################
# Para boleta
################################################################################################
        elif(eDocumentType=="BOL"):
            for invoice in self:      
                sunat_request_type = invoice.company_id.sunat_request_type 

                if(sunat_request_type=="automatic"):
                    sunat_request_type = "Automatizada"  
                    processInvoiceAction = "fill_only"    
                else:
                    sunat_request_type = "Documento Validado"
                    processInvoiceAction = "fill_submit"

                if(self.isPosOrder(invoice.invoice_origin)):
                    processInvoiceAction = "fill_submit"

                self.env.cr.commit()
                self.env.cr.rollback()

                items = invoice.invoice_line_ids

                for item in items:
                    item_tributos = []
                    subTotalVenta = ((item.price_unit * item.quantity))

                    for tax in item.tax_ids:   

                        if(tax.amount_type=="fixed"):
                            impuesto = tax.amount * item.quantity                                                
                            monto_afectacion_tributo = ((impuesto))
                            if(bool(tax.price_include)==True):
                                monto_afectacion_tributo = subTotalVenta - ((subTotalVenta / ((float(impuesto)/100) + 1)))

                        if(tax.amount_type=="percent"):
                            impuesto = tax.amount                                      
                            monto_afectacion_tributo = ((subTotalVenta * (float(impuesto)/100)))

                            if(bool(tax.price_include)==True):
                                monto_afectacion_tributo = subTotalVenta - ((subTotalVenta / ((float(impuesto)/100) + 1)))

                        if(bool(tax.price_include)==True):
                            subTotalVenta -= monto_afectacion_tributo

                        totalVenta = subTotalVenta
                        totalVenta +=  monto_afectacion_tributo

                        item_tributo = {
                                            "codigo":tax.sunat_tributo,
                                            "porcentaje":tax.amount,
                                            "tipo_calculo":tax.amount_type, # percent:IGV... and fixed:plastic bags supported
                                            "montoAfectacionTributo":monto_afectacion_tributo,
                                            "total_venta":subTotalVenta,
                                            'tipoAfectacionTributoIGV': tax.sunat_tributo_afectacion_igv, # pendiente si es igv - catalogo 7. 
                                            'sistemaCalculoISC':tax.sunat_tributo_calculo_isc
                                                     #pendiente si es isc - catalogo 8 para codigo = 2000 ISC
                                       }

                        item_tributos.append(item_tributo) 

                    tributos_globales = self.add_global_tributes(item_tributos,tributos_globales)
                    price_unit = float(item.price_subtotal) / float(item.quantity)
                        
                    sunat_item = {
                                    'id':str(item.product_id.id),
                                    'cantidad':str(item.quantity),
                                    "medidaCantidad":str(item.product_id.uom_id.sunat_unit_code),
                                    'descripcion':item.name,
                                    "precioUnidad":price_unit,
                                    'tipoPrecioVentaUnitario':self.get_sunat_product_type_price( item.product_id.id),  #instalar en ficha de producto catalogo 16    01 Precio unitario (incluye el IGV), 02 Valor referencial unitario en operaciones no onerosas                                        
                                    'clasificacionProductoServicioCodigo':self.get_sunat_product_code_classification( item.product_id.id),
                                    "subTotalVenta":subTotalVenta,
                                    'totalVenta':totalVenta, 
                                    "tributos":item_tributos,
                                    "descuento": [],
                                }
                    sunat_items.append(sunat_item)
                    totalVentaPedido += float(totalVenta)
                    subTotalPedido += float(subTotalVenta)

            currentDateTime = datetime.now()
            currentTime = currentDateTime.strftime("%H:%M:%S")                

            if(str(invoice.name) == '/'):
                next_sequence = invoice.journal_id.sequence_id._get_current_sequence()
                secuencia = str( str(next_sequence.prefix) + str(next_sequence.number_next_actual) ).split("-")
                secuencia_serie = secuencia[0]
                secuencia_consecutivo = secuencia[1]
            else:
                secuencia = str(invoice.name).split("-")
                secuencia_serie = secuencia[0]
                secuencia_consecutivo = secuencia[1]

            # Start data validation
            Vcompany_address = self.validate_address(invoice.company_id)
            Vpartner_address = self.validate_address(invoice.partner_id)

            # Start data validation
            Vcompany_address = self.validate_address(invoice.company_id)
            if(bool(Vcompany_address["errors"])):
                raise Warning (str("Cliente / Socio")+Vcompany_address["msn"])

            Vcompany_certificate = self.validate_certificate(invoice.company_id)
            if(bool(Vcompany_certificate["errors"])==True):
                raise Warning (str("Compañia emisora")+Vcompany_certificate["msn"])

            Vpartner_address = self.validate_address(invoice.partner_id)
            if(bool(Vpartner_address["errors"])):
                raise Warning (str("Compañia emisora")+Vpartner_address["msn"])

            sunat_data = {
                                "serie": str(secuencia_serie),
                                "numero":str(secuencia_consecutivo),
                                "emisor":{
                                            "tipo_documento":invoice.company_id.sunat_tipo_documento,
                                            "nro":invoice.company_id.vat,
                                            "nombre":str(invoice.company_id.name).capitalize(),
                                            "direccion":str(invoice.company_id.street).capitalize(),
                                            "ciudad":str(Vcompany_address["address"]["province"]["name"]),
                                            "ciudad_sector":str(Vcompany_address["address"]["district"]["name"]),
                                            "departamento":str(invoice.company_id.state_id.name).capitalize(),
                                            "codigoPostal":invoice.company_id.zip,
                                            "codigoPais":invoice.company_id.country_id.code,
                                            "ubigeo":(str(invoice.company_id.ubigeo) if(invoice.company_id.ubigeo!=None) else str(invoice.company_id.zip))
                                        },
                                "receptor": {
                                                "tipo_documento":invoice.partner_id.sunat_tipo_documento,
                                                "nro":invoice.partner_id.vat,
                                                "nombre":str(invoice.partner_id.name).capitalize(),
                                                "direccion":str(invoice.partner_id.street).capitalize(),
                                                "ciudad":str(Vpartner_address["address"]["province"]["name"]),
                                                "ciudad_sector":str(Vpartner_address["address"]["district"]["name"]),
                                                "departamento":str(invoice.partner_id.state_id.name),
                                                "codigoPostal":invoice.partner_id.zip,
                                                "codigoPais":invoice.partner_id.country_id.code,
                                                "ubigeo":(str(invoice.partner_id.ubigeo) if(invoice.partner_id.ubigeo!=None) else str(invoice.partner_id.zip))
                                            },
                                "fechaEmision":str(invoice.invoice_date).replace("/","-",3),
                                "fechaVencimiento":str(invoice.invoice_date_due).replace("/","-",3),
                                "horaEmision":currentTime,
                                "subTotalVenta":subTotalPedido,
                                "totalVentaGravada":totalVentaPedido,
                                "tipoMoneda":invoice.currency_id.name,
                                "items": sunat_items,
                                "tributos":tributos_globales,
                                "descuentos": {"globales": []},
                                "pagos":self.env['sunat.catalog'].sudo().get_payment(self),
                                "terminos_pagos": self.get_payment_terms(),
                                "sunat_sol": {
                                            "ruc":invoice.company_id.sol_ruc,
                                            'usuario':invoice.company_id.sol_username,
                                            'clave':invoice.company_id.sol_password,
                                            'certificado':{
                                                                'crt':invoice.company_id.cert_pem_filename,
                                                                'key':invoice.company_id.key_pem_filename,
                                                                'pass':invoice.company_id.key_pass,
                                                              }
                                        },
                                "accion": processInvoiceAction,
                                'licencia':"081OHTGAVHJZ4GOZJGJV"
                            }

            _logger.warning("sunat_data")
            _logger.warning(sunat_data)

            serieConsecutivoString = secuencia_serie
            serieConsecutivo = secuencia_consecutivo
            currentDateTime = datetime.now()
            currentTime = currentDateTime.strftime("%H:%M:%S")

            xmlPath = os.path.dirname(os.path.abspath(__file__))+'/xml'
            
            SunatService = Service()
            SunatService.setXMLPath(xmlPath)
            SunatService.fileName = str(invoice.company_id.vat)+"-03-"+str(serieConsecutivoString)+"-"+str(serieConsecutivo)
            SunatService.initSunatAPI(invoice.company_id.api_mode, "sendBill")
            SunatResponse = SunatService.processTicket(sunat_data)

            # save xml documents steps for reference in edocs
            if 'xml_response' in SunatResponse:
                self.response_document = SunatResponse["xml_response"]
                self.response_document_filename = str("R_")+str(serieConsecutivoString)+"-"+str(serieConsecutivo)+str(".XML")

            if 'xml_signed' in SunatResponse:
                self.signed_document = SunatResponse["xml_signed"]
                self.signed_document_filename = str("F_")+str(serieConsecutivoString)+"-"+str(serieConsecutivo)+str(".XML")

            if 'xml_unsigned' in SunatResponse:
                self.unsigned_document = SunatResponse["xml_unsigned"]
                self.unsigned_document_filename = str("NF_")+str(serieConsecutivoString)+"-"+str(serieConsecutivo)+str(".XML")
            
            # generate qr for invoices and tickets in pos
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
            qr = qrcode.QRCode(
                                version=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L,
                                box_size=20,
                                border=4,
                            )

            total_tributo_igv = self.get_sumatoria_tributo_igv(tributos_globales)            
            qr_code_text = str(sunat_data["emisor"]["nro"]) + str("|") + str(sunat_data["emisor"]["tipo_documento"]) + str("|") + str(sunat_data["serie"]) + str("|") + str(sunat_data["numero"]) + str("|") + str(total_tributo_igv) + str("|") + str(format(float(sunat_data["totalVentaGravada"]),'.2f')) + str("|") + str(sunat_data["fechaEmision"]) + str("|") + str(sunat_data["receptor"]["tipo_documento"]) + str("|") + str(sunat_data["receptor"]["nro"])
            qr.add_data(qr_code_text)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            self.qr_image = base64.b64encode(temp.getvalue())
            self.qr_in_report = True

            self.sunat_request_type = sunat_request_type
            self.sunat_total_letters = self.literal_price(totalVentaPedido)
            #raise Warning(SunatResponse["body"]["description"])
            #with open('/home/rockscripts/Documents/data.json', 'w') as outfile:
            #    json.dump(SunatResponse["body"], outfile) 
            if 'status' in SunatResponse:
                if(SunatResponse["status"] == "OK"):                                                                                    
                    self.api_message = "ESTADO: "+str(SunatResponse["status"])+"\n"+"REFERENCIA: "+str(SunatResponse["body"]["referencia"]).replace("'",'"')+"\n"+" "+str(SunatResponse["body"]["description"]).replace("'",'"')
                    self.sunat_request_status = 'OK'
                    # raise Warning("OK")
                    return super(account_move_pos, self).post()
                else:
                    self.sunat_request_status = 'FAIL'
                    self.api_message = "ESTADO: "+str(SunatResponse["status"])+"\n"+" "+str(SunatResponse["body"])+"\n"+"CÓDIGO ERROR: "+str(SunatResponse["code"])
                    return super(account_move_pos, self).post()
            else:
                return super(account_move_pos, self).post()    

        return super(account_move_pos, self).post()
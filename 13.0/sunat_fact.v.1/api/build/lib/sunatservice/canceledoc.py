from lxml import etree
import json, sys
from xml.dom import minidom

class Canceldoc:

    def fillDocument(self, XMLpath, fileName,  data):
        try:
            tree = etree.parse(XMLpath+"/XMLdocuments/1_unfilled/UNFILLED-cancel-edoc.XML")
            XMLFileContents = etree.tostring(tree.getroot(), pretty_print = True, xml_declaration = True, encoding='UTF-8', standalone="yes")

            #fill xml with data
            data  = json.dumps(data , indent=4)
            data = json.loads(data)
            VoidedDocuments = tree.getroot()
            documentID = str(data['document_id'])
            
            #DOCUMENT ID
            ID = VoidedDocuments.find(self.getInvoiceNameSpace("cbc")+"ID")
            ID.text = documentID

            #ISSUE DATE
            IssueDate = VoidedDocuments.find(self.getInvoiceNameSpace("cbc")+"IssueDate")
            IssueDate.text = data["fecha_comunicacion"]

            #ISSUE DATE EDOC
            ReferenceDate = VoidedDocuments.find(self.getInvoiceNameSpace("cbc")+"ReferenceDate")
            ReferenceDate.text = data["reference"]["fecha_emision"]

            #SIGNATURE
            for Signature in VoidedDocuments.iter(self.getInvoiceNameSpace("cac")+"Signature"):
                ID = Signature.find(self.getInvoiceNameSpace("cbc")+"ID")
                ID.text = documentID

                SignatoryParty = Signature.find(self.getInvoiceNameSpace("cac")+"SignatoryParty")
                PartyIdentification = SignatoryParty.find(self.getInvoiceNameSpace("cac")+"PartyIdentification")
                ID = PartyIdentification.find(self.getInvoiceNameSpace("cbc")+"ID")
                ID.text = data["emisor"]["nro"] 

                PartyName = SignatoryParty.find(self.getInvoiceNameSpace("cac")+"PartyName")
                Name = PartyName.find(self.getInvoiceNameSpace("cbc")+"Name")
                Name.text = etree.CDATA(data["emisor"]["nombre"])

                DigitalSignatureAttachment = Signature.find(self.getInvoiceNameSpace("cac")+"DigitalSignatureAttachment")
                ExternalReference = DigitalSignatureAttachment.find(self.getInvoiceNameSpace("cac")+"ExternalReference")
                URI = ExternalReference.find(self.getInvoiceNameSpace("cbc")+"URI")
                URI.text = "#S"+documentID
            
            #AccountingSupplierParty -> PartyName
            for AccountingSupplierParty in VoidedDocuments.findall(self.getInvoiceNameSpace("cac")+"AccountingSupplierParty"):
                CustomerAssignedAccountID = AccountingSupplierParty.find(self.getInvoiceNameSpace("cbc")+"CustomerAssignedAccountID")
                CustomerAssignedAccountID.text = data["emisor"]["nro"]
                AdditionalAccountID = AccountingSupplierParty.find(self.getInvoiceNameSpace("cbc")+"AdditionalAccountID")
                AdditionalAccountID.text = str(data["emisor"]["tipo_documento"])
                Party =  AccountingSupplierParty.find(self.getInvoiceNameSpace("cac")+"Party")
                PartyLegalEntity = Party.find(self.getInvoiceNameSpace("cac")+"PartyLegalEntity")
                RegistrationName = PartyLegalEntity.find(self.getInvoiceNameSpace("cbc")+"RegistrationName")
                RegistrationName.text = etree.CDATA(data["emisor"]["nombre"])
                

            for VoidedDocumentsLine in VoidedDocuments.findall(self.getInvoiceNameSpace("sac")+"VoidedDocumentsLine"):
                LineID =  VoidedDocumentsLine.find(self.getInvoiceNameSpace("cbc")+"LineID")
                LineID.text = str('1')
                DocumentTypeCode =  VoidedDocumentsLine.find(self.getInvoiceNameSpace("cbc")+"DocumentTypeCode")
                DocumentTypeCode.text = str(data["reference"]['tipo_edoc'])
                DocumentSerialID =  VoidedDocumentsLine.find(self.getInvoiceNameSpace("sac")+"DocumentSerialID")
                DocumentSerialID.text = str(data["reference"]['serie'])
                DocumentNumberID =  VoidedDocumentsLine.find(self.getInvoiceNameSpace("sac")+"DocumentNumberID")
                DocumentNumberID.text = str(data["reference"]['numero'])
                VoidReasonDescription =  VoidedDocumentsLine.find(self.getInvoiceNameSpace("sac")+"VoidReasonDescription")
                VoidReasonDescription.text = str(data["reference"]['motivo'])                    

            tree.write(XMLpath+"/XMLdocuments/2_unsigned/"+fileName+".XML")
            self.prettyXMLSave(XMLpath+"/XMLdocuments/2_unsigned/"+fileName+".XML")
            return XMLpath+"/XMLdocuments/2_unsigned/"+fileName+".XML"
        except Exception as e:
           exc_traceback = sys.exc_info()
           #with open('/odoo_sunatperu/custom/addons/sunat_fact/models/log.json', 'w') as outfile:
           #    json.dump(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno), outfile)

    def getInvoiceNameSpace(self, namespace):
        if(namespace=="sac"):
           return "{urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1}"
        if(namespace=="cbc"):
           return "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}"
        if(namespace=="ext"):
           return "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}"
        if(namespace=="cac"):
           return "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}"

    def prettyXMLSave(self, pathFile):
        tree = etree.parse(pathFile)  
        xmlstr = minidom.parseString(etree.tostring(tree.getroot())).toprettyxml(indent="   ")
        with open(pathFile, "w") as f:
            f.write(xmlstr)
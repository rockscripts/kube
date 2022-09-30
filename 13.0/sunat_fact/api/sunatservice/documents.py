import base64, json, sys
from zipfile import ZipFile
from lxml import etree
import os
from . certificate import XMLSigner
from . certificate import XMLVerifier
from . invoices import Invoices
from . tickets import Tickets
from . creditnote import Creditnote
from . debitnote import Debitnote
from . guide import Guide
from . canceledoc import Canceldoc

class Documents:

    xmlPath = False
    documentName = False
    def fillDocument(self, whichDocument, data):

        fileFilled = False
        if(whichDocument=="invoice"):
           invoice = Invoices()
           fileFilled = invoice.fillDocument(self.xmlPath, self.documentName, data)

        if(whichDocument=="ticket"):
           ticket = Tickets()
           fileFilled = ticket.fillDocument(self.xmlPath, self.documentName, data)
        
        if(whichDocument=="creditNote"):
           creditNote = Creditnote()
           fileFilled = creditNote.fillDocument(self.xmlPath, self.documentName, data)

        if(whichDocument=="debitNote"):
           debitNote = Debitnote()
           fileFilled = debitNote.fillDocument(self.xmlPath, self.documentName, data)

        if(whichDocument=="deliveryGuide"):
           deliveryGuide = Guide()
           fileFilled = deliveryGuide.fillDocument(self.xmlPath, self.documentName, data)
        
        if(whichDocument=="eDocCancel"):
           cancelDoc = Canceldoc()
           fileFilled = cancelDoc.fillDocument(self.xmlPath, self.documentName, data)

        return fileFilled

    def signDocument(self, key, cert, passw=None):
        signed_root = XMLSigner().sign(self.xmlPath+"/XMLdocuments/2_unsigned/"+self.documentName+".XML", key_data=key, cert_data=cert, password=passw)
        signed_doc_str = etree.tostring(signed_root, xml_declaration=True, encoding='ISO-8859-1', pretty_print=True)
        self.saveSignedDocument(self.xmlPath+"/XMLdocuments/3_signed/"+self.documentName+".XML", signed_doc_str)
        return True

    def saveSignedDocument(self, newDocument, XMLcontents):
        f = open(newDocument, "wb")
        f.write(XMLcontents)
        f.close()

    def verifyDocument(self, key):
        verified = XMLVerifier().verify(self.xmlPath+"/XMLdocuments/3_signed/"+self.documentName+".XML", key_data=key)
        return verified

    def zipDocument(self, sourcePath, targetPath, fileName):
        try:           
            xmlSource = str(self.xmlPath+'/XMLdocuments/3_signed/')+str(self.documentName)+str(".XML")
            zipTarget = str(self.xmlPath+'/XMLdocuments/4_compressed/')+str(self.documentName)+".zip"
            ZipFile(zipTarget, 'w').write(xmlSource,self.documentName+str(".XML"))
            return True
        except:
            return False

    def Base64EncodeDocument(self):
        try: 
            fileContents = open(self.xmlPath+'/XMLdocuments/4_compressed/'+str(self.documentName)+".zip", "rb").read()
            encoded = base64.b64encode(fileContents)
            return encoded
        except Exception as e:
            exc_traceback = sys.exc_info()
            #with open('/odoo_peru_sunat/custom/addons/sunat_fact/data.json', 'w') as outfile:
            #    json.dump(self.xmlPath+'/XMLdocuments/4_compressed/'+str(self.documentName)+".zip", outfile)
            return None

    def getXMLUnsignedDocument(self):
        try:  
            fileContents = open(self.xmlPath+'/XMLdocuments/2_unsigned/'+str(self.documentName)+".XML", "rb").read()
            encoded = base64.b64encode(fileContents)
            return encoded
        except:
            return None

    def getXMLSignedDocument(self):
        try:
            fileContents = open(self.xmlPath+'/XMLdocuments/3_signed/'+str(self.documentName)+".XML", "rb").read()
            encoded = base64.b64encode(fileContents)
            return encoded
        except:
            return None

    

    def setXMLPath(self,xmlPath):
        self.xmlPath = xmlPath
    
    def resetDocumentProcess(self):
        self.documentName = False
        self.xmlPath = False
    
    def fillSenBill(self, data):
        tree = etree.parse(data['sendBillFile'])
        EnvelopeNode = tree.getroot()
        sol = data['sunat_sol']
        for item in EnvelopeNode.iter('fileName'):
            item.text = data['fileName']

        for item in EnvelopeNode.iter('contentFile'):
            item.text = data['contentFile']        
        
        for Username in EnvelopeNode.iter(self.getSenBillNameSpace("wsse")+"Username"):
            Username.text = sol["usuario"]     

        for Password in EnvelopeNode.iter(self.getSenBillNameSpace("wsse")+"Password"):
            Password.text = sol["clave"]    

        tree.write(data['sendBillFile'])
    
    def fillGetCDR(self, data):
        tree = etree.parse(data['getCDRFile'])
        EnvelopeNode = tree.getroot()

        for getStatusCdr in EnvelopeNode.iter(self.getSenBillNameSpace("ser")+"getStatusCdr"):

            for rucComprobante in getStatusCdr.iter("rucComprobante"):
                rucComprobante.text = data["rucComprobante"]     

            for tipoComprobante in getStatusCdr.iter("tipoComprobante"):
                tipoComprobante.text = data["tipoComprobante"]  

            for serieComprobante in getStatusCdr.iter("serieComprobante"):
                serieComprobante.text = data["serieComprobante"]
            
            for numeroComprobante in getStatusCdr.iter("numeroComprobante"):
                numeroComprobante.text = data["numeroComprobante"]
                
            sol = data['sunat_sol']
            for Username in EnvelopeNode.iter(self.getSenBillNameSpace("wsse")+"Username"):
                Username.text = sol["usuario"]     

            for Password in EnvelopeNode.iter(self.getSenBillNameSpace("wsse")+"Password"):
                Password.text = sol["clave"] 

        tree.write(data['getCDRFile'])
    
    def fillGetStatus(self, data):
        tree = etree.parse(data['getStatusFile'])
        EnvelopeNode = tree.getroot()

        for getStatus in EnvelopeNode.iter(self.getSenBillNameSpace("ser")+"getStatus"):

            for ticket in getStatus.iter("ticket"):
                ticket.text = data["ticket"]     
                
            sol = data['sunat_sol']
            for Username in EnvelopeNode.iter(self.getSenBillNameSpace("wsse")+"Username"):
                Username.text = sol["usuario"]     

            for Password in EnvelopeNode.iter(self.getSenBillNameSpace("wsse")+"Password"):
                Password.text = sol["clave"] 

        tree.write(data['getStatusFile'])

    def getSenBillNameSpace(self, namespace):
        if(namespace=="wsse"):
           return "{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}"
        if(namespace=="soapenv"):
           return "{http://schemas.xmlsoap.org/soap/envelope/}"
        if(namespace=="ser"):
           return "{http://service.sunat.gob.pe}"
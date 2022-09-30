import base64
import requests
from lxml import etree
from zipfile import ZipFile
import sys, json
import time, os

class SunatApi:

    apiMode = "SANDBOX"

    endPointType = False #INVOICE , GUIDE

    endPointSandBox    = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService"
    endPointProduction = "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService" 

    # WS de consulta de CDR y estado de envío
    endPointCRD = "https://e-factura.sunat.gob.pe/ol-it-wsconscpegem/billConsultService"
    

    endPointSandBoxGuide    = "https://e-beta.sunat.gob.pe/ol-ti-itemision-guia-gem-beta/billService"
    endPointProductionGuide = "https://e-guiaremision.sunat.gob.pe/ol-ti-itemision-guia-gem/billService" 
                               
    
    call = False

    xmlPath = False
    fileName = False
    
       
    def __init__(self, apiMode, call, xmlPath, fileName):
        self.apiMode = apiMode
        self.call = call
        self.xmlPath = xmlPath
        self.fileName = fileName 

    def doResquest(self):
        headers = {'Content-Type': 'text/xml',"Accept":"text/xml"}             
        req = requests.Request('POST',self.getEndPoint(),headers=headers, data=self.getXMLrequest())
        prepared = req.prepare()
        s = requests.Session()
        try:
            response = s.send(prepared,verify=False)                                  
            self.saveSenBillResponse(base64.b64encode(response.content))           
            response = self.getXMLresponse(response)
            response["xml_response"] = self.getXMLResponseDocument()
            
        except Exception as e:
            exc_traceback = sys.exc_info()
            response = {}
            
            if(self.call=="sendSummary"):
                response["statusCode"] = "FAIL"
                response["code"] = "SUNAT - Error interno"
            else:
                response["status"] = "FAIL"
                response["code"] = "SUNAT - Servidor Ocupado"
                response["body"] = "Servidor no disponible temporalmente, vuelve a intentar."

        return response
    
    def getXMLrequestCDR(self):
        tree = False
        tree = etree.parse(self.xmlPath+"/XMLrequests/getCDR.XML")
        XMLFileContents = etree.tostring(tree.getroot())
        return XMLFileContents

    def getXMLrequestStatus(self):
        tree = False
        tree = etree.parse(self.xmlPath+"/XMLrequests/getStatus.XML")
        XMLFileContents = etree.tostring(tree.getroot())
        return XMLFileContents
    
    def getCDR(self):
        time.sleep( 7 )
        headers = {'Content-Type': 'text/xml',"Accept":"text/xml"}
        req = requests.Request('POST',self.endPointCRD,headers=headers, data=self.getXMLrequestCDR())
        prepared = req.prepare()
        s = requests.Session()
        
        try:
            response = s.send(prepared,verify=False)
            self.saveCDRResponse(base64.b64encode(response.content))
            response = self.getXMLresponseCDR(response)
            return response
            
        except Exception as e:
            exc_traceback = sys.exc_info()
    
    def getStatus(self):
        time.sleep( 7 )
        headers = {'Content-Type': 'text/xml',"Accept":"text/xml"}
        req = requests.Request('POST',self.getEndPoint(),headers=headers, data=self.getXMLrequestStatus())
        prepared = req.prepare()
        s = requests.Session()

        try:
            response = s.send(prepared,verify=False)
            self.saveStatusResponse(base64.b64encode(response.content))
            response = self.getXMLresponseStatus(response)
            return response
            
        except Exception as e:
            exc_traceback = sys.exc_info()
    
    def getXMLrequest(self):
        tree = False
        
        if(self.call=="sendBill"):
           tree = etree.parse(self.xmlPath+"/XMLrequests/sendBill.XML")
        if(self.call=="sendSummary"):
            tree = etree.parse(self.xmlPath+"/XMLrequests/sendSummary.XML")
        if(self.call=="getStatus"):
            tree = etree.parse(self.xmlPath+"/XMLrequests/getStatus.XML")

        XMLFileContents = etree.tostring(tree.getroot())
        return XMLFileContents
    
    def getXMLresponse(self, response):
        niceResponse = {}
        try:
            objecResponse = etree.fromstring(response.content)
            if(self.call=="sendBill"):
                for child in objecResponse.iter('applicationResponse'):
                    if child.text != "":
                        niceResponse["status"] = "OK"
                        niceResponse["body"] = self.handleSendBillResponse(child.text)
                
                if not niceResponse:
                    
                    for child in objecResponse.iter('faultcode'):
                        niceResponse["status"] = "FAIL"
                        niceResponse["code"] = child.text

                    for child in objecResponse.iter('faultstring'):
                        niceResponse["body"] = child.text

                    for child in objecResponse.iter('message'):
                        niceResponse["body"] = str(niceResponse["body"]) + str(" \n") + str(child.text)   

            if(self.call=="sendSummary"):
                for Envelope in objecResponse.iter('{http://schemas.xmlsoap.org/soap/envelope/}Envelope'):
                    for Body in Envelope.iter('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
                        for sendSummaryResponse in Body.iter('{http://service.sunat.gob.pe}sendSummaryResponse'):
                            ticket = sendSummaryResponse.find('ticket')
                            niceResponse ['ticket_number'] = ticket.text
                            niceResponse ['statusCode'] = str("OK")
                
                for Envelope in objecResponse.iter('{http://schemas.xmlsoap.org/soap/envelope/}Envelope'):
                    for Body in Envelope.iter('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
                        for Fault in Body.iter('{http://schemas.xmlsoap.org/soap/envelope/}Fault'):                        
                            statusCode = Fault.find('faultcode')
                            niceResponse ['statusCode'] = statusCode.text
                            statusMessage = Fault.find('faultstring')
                            niceResponse ['statusMessage'] = statusMessage.text                                                    

            #self.saveSenBillResponse(response.content)
            niceResponse["debug"] = response.content
        except Exception as e:
            exc_traceback = sys.exc_info()

        return niceResponse

    def getXMLresponseStatus(self, response):
        niceResponse = {}
        try:
            objecResponse = etree.fromstring(response.content)
            for Envelope in objecResponse.iter('{http://schemas.xmlsoap.org/soap/envelope/}Envelope'):
                for Body in Envelope.iter('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
                    for getStatusResponse in Body.iter('{http://service.sunat.gob.pe}getStatusResponse'):
                        for status in getStatusResponse.iter('status'):
                            content = status.find('content')
                            if(len(content.text)>20):
                                zipped = content.text
                                zipTarget = str(self.xmlPath+'/XMLresponses/')+ str("Status-Zipped") + str(self.fileName)+".zip"
                                responseZipFile = open(zipTarget, 'wb')
                                responseZipFile.write(base64.b64decode(zipped.encode()))
                                responseZipFile.close()
        except Exception as e:
            exc_traceback = sys.exc_info()

        return niceResponse    

    def getXMLresponseCDR(self, response):
        niceResponse = {}
        try:
            objecResponse = etree.fromstring(response.content)
        
            for Envelope in objecResponse.iter('{http://schemas.xmlsoap.org/soap/envelope/}Envelope'):
                for Body in Envelope.iter('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
                    for getStatusCdrResponse in Body.iter('{http://service.sunat.gob.pe}getStatusCdrResponse'):
                        for statusCdr in Body.iter('statusCdr'):
                            statusCode = statusCdr.find('statusCode')
                            niceResponse ['statusCode'] = statusCode.text
                            statusMessage = statusCdr.find('statusMessage')
                            niceResponse ['statusMessage'] = statusMessage.text
            
            for Envelope in objecResponse.iter('{http://schemas.xmlsoap.org/soap/envelope/}Envelope'):
                for Body in Envelope.iter('{http://schemas.xmlsoap.org/soap/envelope/}Body'):
                    for Fault in Body.iter('{http://schemas.xmlsoap.org/soap/envelope/}Fault'):                        
                        statusCode = Fault.find('faultcode')
                        niceResponse ['statusCode'] = statusCode.text
                        statusMessage = Fault.find('faultstring')
                        niceResponse ['statusMessage'] = statusMessage.text


        except Exception as e:
            exc_traceback = sys.exc_info()

        return niceResponse
    
    def getEndPoint(self):
        if(self.endPointType=="INVOICE"):
            if(self.apiMode=="PRODUCTION"):
                return self.endPointProduction
            else:
                return self.endPointSandBox

        if(self.endPointType=="GUIDE"):
            if(self.apiMode=="PRODUCTION"):
                return self.endPointProductionGuide
            else:
                return self.endPointSandBoxGuide
    
    def setEndPointType(self,typeEndPoint):
        self.endPointType = typeEndPoint
    
    def handleSendBillResponse(self, base64encodedContent):
        try:
            zipTarget = str(self.xmlPath+'/XMLresponses/')+str(self.fileName)+".zip"
            responseZipFile = open(zipTarget, 'wb')
            responseZipFile.write(base64.b64decode(base64encodedContent.encode()))
            responseZipFile.close()

            responseZipFile = ZipFile(zipTarget, 'r')
            xmlResponse = None

            try:
                xmlResponse = responseZipFile.open(str("R-")+self.fileName+str(".xml")).read()
            except:
                xmlResponse = responseZipFile.open(str("R-")+self.fileName+str(".XML")).read()

            tree = etree.ElementTree(etree.fromstring(xmlResponse))
            ApplicationResponse = tree.getroot()
            niceResponse = {}          

            for Description in ApplicationResponse.iter(tag='{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Description'):
                niceResponse["description"] = Description.text

            for ReferenceID in ApplicationResponse.iter(tag='{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ReferenceID'):
                niceResponse["referencia"] = ReferenceID.text              

            return niceResponse
        except Exception as e:
            exc = str(getattr(e, 'message', repr(e))+" ON LINE "+format(sys.exc_info()[-1].tb_lineno))          
    
    def saveSenBillResponse(self, xmlResponse):
        xmlTarget = str(self.xmlPath+'/XMLresponses/')+str(self.fileName)+".XML"
        with open(xmlTarget, 'w') as outfile:
            json.dump(xmlTarget, outfile)
        responseXMLFile = open(xmlTarget, 'wb')
        responseXMLFile.write(base64.b64decode(xmlResponse))
        responseXMLFile.close()
    
    def saveCDRResponse(self, xmlResponse):
        xmlTarget = str(self.xmlPath+'/XMLresponses/CDR-')+str(self.fileName)+".XML"
        with open(xmlTarget, 'w') as outfile:
            json.dump(xmlTarget, outfile)
        responseXMLFile = open(xmlTarget, 'wb')
        responseXMLFile.write(base64.b64decode(xmlResponse))
        responseXMLFile.close()
    
    def saveStatusResponse(self, xmlResponse):
        xmlTarget = str(self.xmlPath+'/XMLresponses/Status-')+str(self.fileName)+".XML"
        with open(xmlTarget, 'w') as outfile:
            json.dump(xmlTarget, outfile)
        responseXMLFile = open(xmlTarget, 'wb')
        responseXMLFile.write(base64.b64decode(xmlResponse))
        responseXMLFile.close()

    def getXMLResponseDocument(self):
        try:
            fileContents = open(self.xmlPath+'/XMLresponses/'+str(self.fileName)+".zip", "rb").read()
            encoded = base64.b64encode(fileContents)
            return encoded
        except:
            return None
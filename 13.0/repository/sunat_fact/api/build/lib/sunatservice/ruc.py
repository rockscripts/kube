import requests
import os, re, json, sys

class Ruc:
   dni1_ws = "http://api.grupoyacck.com/dni/"
   ruc1_ws = "http://api.grupoyacck.com/ruc/"

   def consultDNI(self,numero_doc):
      url = self.dni1_ws + str(numero_doc)
      res = {'error': True, 'message': None, 'data': {}}
      try:
         response = requests.get(url)
      except requests.exceptions.ConnectionError as e:
         res['message'] = 'Error en la conexion'
         return res
      try:   
         response = response.json()
         person = response #['DatosPerson'][0]
         if str(person['name']) != '':
            res['error'] = False
            res['data']['nombres'] = person['name']
            res['data']['ape_paterno'] = person['paternal_surname']
            res['data']['ape_materno'] = person['maternal_surname']
            res['data']['fecha_nacimiento'] = None #person['FechaNacimiento']
            res['data']['sexo'] = None #person['Sexo']
         else:
            try:
                  res['message'] = str("No encontrado.")
            except Exception as e:
                  res['error'] = True
         res['url'] = url
         return res         
      except Exception as e:
         exc_traceback = sys.exc_info()
         res['error'] = True
         return res
      return res
   
   def consultRUC(self,ruc):
      res = {'error': False, 'message': None, 'data': {}}
      try:
         response = requests.get(self.ruc1_ws + str(ruc))
         society = response.json()
         res['error'] = False
         res['data']['ruc'] = ruc
         res['data']['tipo_contribuyente'] = society.get('type_taxpayer')
         res['data']['nombre_comercial'] = society.get('commercial_name')
         res['data']['nombre'] = society.get('name')
         res['data']['domicilio_fiscal'] = society.get('street')
         res['data']['departamento'] = self.getDepartment(society.get('region'))
         res['data']['provincia'] = society.get('province')
         res['data']['distrito'] = society.get('district')
         res['data']['ubigeo'] = society.get('ubigeo')
         res['data']['sistema_emision_comprobante'] = society.get('emission_system')
         res['data']['sistema_contabilidad'] = society.get('accounting_system')
         res['data']['estado_contribuyente'] = society.get('state')
         res['data']['condicion_contribuyente'] = society.get('condition')
         res['data']['actividad_economica'] = society.get('activities')
         res['data']['representantes_legales'] = society.get('representatives')
      except Exception as e:            
         res['error'] = True
         return res
      return res     
   
   def setXMLPath(self, xmlPath):
       self.xmlPath = xmlPath
   
   def getDepartment(self, department):
      if(str(department)==str("DIOS")):
         department = str("MADRE DE DIOS")
      if(str(department)==str("MARTIN")):
         department = str("SAN MARTIN")
      if(str(department)==str("LIBERTAD")):
         department = str("LA LIBERTAD")
      if(str(department)==str("111)  LIMA")):
         department = str("LIMA")
      if(str(department)==str("(SSA")):
         department = str("LIMA")         
      return department

qRuc = Ruc()
qRuc.xmlPath = "/var/lib/odoo/addons/12.0/sunatservice/sunatservice"
response = qRuc.consultDNI('42729029')
print(response)
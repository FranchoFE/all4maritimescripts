/**
 * Copyright 2017 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the 'License');
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an 'AS IS' BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
'use strict';

// [START all]
// [START import]
// The Cloud Functions for Firebase SDK to create Cloud Functions and set up triggers.
const functions = require('firebase-functions');

// The Firebase Admin SDK to access Firestore.
const admin = require('firebase-admin');
admin.initializeApp();


const sgMail = require('@sendgrid/mail'); 
sgMail.setApiKey(functions.config().sendgrid.key);

// [END import]

/*exports.changeEta = functions.https.onRequest(async (req, res) => {

        const original = req.query.text;

        // Comprobar si se cumplen las condiciones para que se pueda cambiar
        // 1) Que no tenga ATA
        // 2) Que todos los servicios estén Requested o Planned

        // En caso que se cumplan las condiciones
        // Calcular nuevo ETD (segundos trasncurridos entre ETA - ETD antiguo)
        // Sumarlo al nuevo ETD
        // Cambiar en la base de datos el visit
        // Cambiar en la base de datos los servicios del visit

        // La funcion de updated_eta_visit se dispara tras el cambio del visits en la base de datos

        // Devolvemos si el cambio se realizó correctamente

      });*/


exports.updated_eta_visit= functions.firestore.document('/visits/{documentId}')
    .onUpdate(async (change, context) => {

      const template_id_pcs = 'd-ff7a8957a26544f1be2a83a4240ab4b2';
      const template_id_supplier = 'd-ff7a8957a26544f1be2a83a4240ab4b2';
      const sender_mail = 'fjcc81@gmail.com';
      const receiver_pcs_mail = 'fjcc81@hotmail.com';

      // Se genera un nuevo mensaje en mail_message con destino PCS (con el EDI XMl adjunto en Base64 y haciendo uso de plantilla SendGrid: 
      //    -> email destino email hardcodeado 
      // Se generan N mensajes en mail_message uno por cada servicio vinculado al visit (haciendo uso de plantilla SendGrid):
      //    -> email destino valor de contact de la tabla company
      // La funcion notify_new_mail_message se dispara tras la inclusión de un nuevo mail_message en la base de datos

      // Get an object representing the document
      const newValue = change.after.data();

      // Previous value before this update
      const previousValue = change.before.data();

      var etaPrevious = previousValue.eta;
      var etaNew = newValue.eta;
      
      functions.logger.log('Valor previo de ETA', etaPrevious.toDate());
      functions.logger.log('Valor nuevo de ETA', etaNew.toDate());

      if(etaPrevious.toDate().toString() != etaNew.toDate().toString())
      {
        functions.logger.log('Detectado cambio en el valor del ETA');

        // Inicio de generación del XML
        var xml = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>";
        xml = xml + "<Berman>";
        xml = xml + "    <CabeceraMensaje>";
        xml = xml + "        <Emisor>ALL4MARIME</Emisor>";	
        xml = xml + "        <Receptor>BER0040</Receptor>";
        xml = xml + "        <NumIntercambio>ALL4MO00000001</NumIntercambio>";
        xml = xml + "        <Version>PE1041</Version>";	
        xml = xml + "        <NomDocumento>21</NomDocumento>";
        xml = xml + "        <NumDocumento>ALL4MO00000001</NumDocumento>";
        xml = xml + "        <Funcion>54</Funcion>";
        xml = xml + "        <Fecha>" + new Date(Date.now()).toISOString() + "</Fecha>";
        xml = xml + "    </CabeceraMensaje>";
        xml = xml + "    <CifConsignatario>11112222N</CifConsignatario>";
        xml = xml + "    <consignatario>ALL4MARITIME</consignatario>";
        xml = xml + "    <puertoesc>ESALG</puertoesc>";  
        xml = xml + "    <numescala>" + newValue.visit_number + "</numescala>";
        xml = xml + "    <CallSign>" + newValue.call_sign + "</CallSign>";
        xml = xml + "    <eta>" + newValue.eta.toDate().toISOString() + "</eta>";
        xml = xml + "    <etd>" + newValue.etd.toDate().toISOString() + "</etd>";
        xml = xml + "    <puertoant>" + newValue.port_previous + "</puertoant>";
        xml = xml + "    <puertopos>" + newValue.port_next + "</puertopos>";
        xml = xml + "    <Buque>" + newValue.vessel_name + "</Buque>";
        xml = xml + "    <Estancia>";
        xml = xml + "        <numestancia>A01</numestancia>";
        xml = xml + "        <fecinisol>" + newValue.eta.toDate().toISOString() + "</fecinisol>";
        xml = xml + "        <fecfinsol>" + newValue.etd.toDate().toISOString() + "</fecfinsol>";
        xml = xml + "        <feciniope>" + newValue.eta.toDate().toISOString() + "</feciniope>";
        xml = xml + "        <fecfinope>" + newValue.etd.toDate().toISOString() + "</fecfinope>";
        xml = xml + "        <caladoent>1</caladoent>"; 
        xml = xml + "        <caladosal>1</caladosal>"; 
        xml = xml + "        <codtipoatraquesol>AXM</codtipoatraquesol>"; 
        xml = xml + "        <codactividad>ZOT</codactividad>"; 
        xml = xml + "        <areaoperacion>" + newValue.code_zone_operation + "</areaoperacion>";
        xml = xml + "        <exentoprc>N</exentoprc>";
        xml = xml + "        <estanciaprl>S</estanciaprl>";
        xml = xml + "        <Averias>N</Averias>";
        xml = xml + "        <EmpresaAmarre>ZZN</EmpresaAmarre>";
        xml = xml + "    </Estancia>";
        xml = xml + "</Berman>";        
        // Fin generación del XML

        functions.logger.log('XML Generado', xml);

        functions.logger.log(Buffer.from(xml).toString('base64'));
        var xmlBase64 = Buffer.from(xml).toString('base64');
        
        // Mensaje para el PCS
        var title = 'Cambio de datos en la escala';
        var subject = 'Cambio del tiempo estimado de llegada en la escala ' + newValue.visit_number;
        var body = 'Le informamos del cambio producido en el tiempo estimado (ETA) de llegada en la escala ' + newValue.visit_number;
        body = body + ' del buque ' + newValue.vessel_name + " con imo " + newValue.imo + " y callsign " + newValue.call_sign + ". ";
        body = body + 'Todos los servicios contratados para la escala se verán afectados y los proveedores serán notificados del cambio.';
        var data_old = 'El tiempo estimado de llegada previo era ' + previousValue.eta.toDate();
        var data_new = 'El tiempo estimado de llegada ahora es  ' + newValue.eta.toDate() ;   

        const msg = {
          to: receiver_pcs_mail, 
          from: sender_mail, 
          //subject: 'Recibido Cambio de ETA para la escala ' + newValue.visit_number,
          //text: 'Se ha recibido un cambio de ETA para la escala en all4Maritime',
          //html: 'Se ha recibido un cambio de ETA en <strong>all4Maritime</strong>',
          attachments: [
            {
              content: xmlBase64,
              filename: newValue.visit_number + "-edi.xml",
              type: "application/xml",
              disposition: "attachment"
            }
          ],
          "personalizations":[
            {
               "to":[
                  {
                    "email":receiver_pcs_mail
                  }
               ],
               "dynamic_template_data":{  
                  "subject": subject,  
                  "title": title,
                  "body": body,
                  "data_old": data_old,
                  "data_new": data_new,
                }
            }
         ],
          template_id: template_id_pcs,
        }  
        const writeResult = await admin.firestore().collection('mail_message').add(msg);

      
        // Mensajes para los proveedores de servicios
        var idVisit = context.params.documentId;

        // Servicios
        const servicesRef = admin.firestore().collection('services');
        const servicesSnapshot = await servicesRef.where('visit_ref', '==', idVisit).get();
        var serviceDataFound = [];
        var servicesFound = [];
        if (servicesSnapshot.empty)
        {
          console.log('No matching documents services.');
        }
        else
        {
          console.log('Yes matching documents services.');
          var n = 0;
          servicesSnapshot.forEach(doc => {
            //console.log("REFERENCIA SERVICE_AVAILABLE", '=>', doc.data().service_available_ref);
            servicesFound.push(doc.data().service_available_ref);

            serviceDataFound[n] = [doc.data().estimated_start_time, doc.data().estimated_end_time];

            n = n + 1;
          });
        }

        // Companías de los servicios disponibles
        const serviceAvailableRef = admin.firestore().collection('service_available');
        const serviceAvailableSnapshot = await serviceAvailableRef.where('__name__', 'in', servicesFound).get();
        var companiesFound = [];
        var serviceAvailableDataFound = [];
        if (serviceAvailableSnapshot.empty)
        {
          console.log('No matching documents services availables.');
        }
        else
        {
          console.log('Yes matching documents services availables.');
          var i = 0;
          serviceAvailableSnapshot.forEach(docu => {
            //console.log("REFERENCIA COMPANY", '=>', docu.data().company_ref);
            companiesFound.push(docu.data().company_ref);

            serviceAvailableDataFound[i] = [docu.data().type, docu.data().price];

            i = i + 1;
          });
        }

        // Información de contacto de la compañía
        const companyRef = admin.firestore().collection('company');
        const companySnapshot = await companyRef.where('__name__', 'in', companiesFound).get();
        var contactFound = [];
        if (companySnapshot.empty)
        {
          console.log('No matching documents companies.');
        }
        else
        {
          console.log('Yes matching documents companies.');
          companySnapshot.forEach(docu => {
            //console.log("THE CONTACT", '=>', docu.data().contact);
            contactFound.push(docu.data().contact);
          });
        }      

        var j = 0;
        // Recorrido de los contactos       
        contactFound.forEach((contact) => {

          var title = 'Cambio en el servicio contratado';
          var subject = 'Cambio en el servicio contratado para la escala ' + newValue.visit_number;  
          var body = 'Le informamos del cambio producido en el tiempo estimado (ETA) de llegada en la escala ' + newValue.visit_number;
          body = body + ' del buque ' + newValue.vessel_name + " con imo " + newValue.imo + " y callsign " + newValue.call_sign + ", ";
          body = body + 'el cual afectará al servicio de ' + serviceAvailableDataFound[j][0] + ' que usted ofrece.';
          var data_old = 'El tiempo de inicio / fin del servicio anteriormente era ' + previousValue.eta.toDate() + '/' + previousValue.etd.toDate();
          var data_new = 'El tiempo de inicio / fin del servicio ahora es ' + newValue.eta.toDate() + '/' + newValue.etd.toDate(); 

          const msg = {
            to: contact, 
            from: sender_mail, 
            //subject: 'Recibido Cambio de ETA para la escala ' + newValue.visit_number,
            //text: 'Se ha recibido un cambio de ETA para la escala en all4Maritime',
            //html: 'Se ha recibido un cambio de ETA en <strong>all4Maritime</strong>',
            "personalizations":[
              {
                "to":[
                    {
                      "email": contact
                    }
                ],
                "dynamic_template_data":{    
                    "subject": subject,  
                    "title": title,
                    "body": body,       
                    "data_old": data_old,
                    "data_new": data_new,                                 
                  }
              }
          ],
            template_id: template_id_supplier,
          } 

          const writeResult = admin.firestore().collection('mail_message').add(msg);

          j = j + 1;

      });

      }
      else
      {
        functions.logger.log('No detectado cambio en el valor del ETA');
      }

      return "OK";

    });

exports.notify_new_mail_message= functions.firestore.document('/mail_message/{documentId}')
    .onCreate(async (snap, context) => {

      // Envio de mensaje (a PCS o Proveedor)
      const msg = snap.data();
      const to = msg.to;

      functions.logger.log("Nuevo mensaje para -> " + to);

      const send_mail = true;
      if (send_mail)
      {
        return sgMail
          .send(msg)
          .then(() => {
            functions.logger.log('Email sent');
          })
          .catch((error) => {
            functions.logger.log('Email ERROR', error);
        })
      }

      return "OK";

    });
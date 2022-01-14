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

const sgMail = require('@sendgrid/mail') 
sgMail.setApiKey(functions.config().sendgrid.token)
// [END import]

// [START addMessage]
// Take the text parameter passed to this HTTP endpoint and insert it into 
// Firestore under the path /messages/:documentId/original
// [START addMessageTrigger]
exports.addMessage = functions.https.onRequest(async (req, res) => {
// [END addMessageTrigger]
  // Grab the text parameter.
  const original = req.query.text;
  // [START adminSdkAdd]
  // Push the new message into Firestore using the Firebase Admin SDK.
  const writeResult = await admin.firestore().collection('messages').add({original: original});
  // Send back a message that we've successfully written the message
  res.json({result: `Message with ID: ${writeResult.id} added.`});
  // [END adminSdkAdd]
});
// [END addMessage]

// [START makeUppercase]
// Listens for new messages added to /messages/:documentId/original and creates an
// uppercase version of the message to /messages/:documentId/uppercase
// [START makeUppercaseTrigger]
exports.makeUppercase = functions.firestore.document('/messages/{documentId}')
    .onCreate((snap, context) => {
// [END makeUppercaseTrigger]
      // [START makeUppercaseBody]
      // Grab the current value of what was written to Firestore.
      const original = snap.data().original;

      // Access the parameter `{documentId}` with `context.params`
      functions.logger.log('Uppercasing', context.params.documentId, original);
      
      const uppercase = original.toUpperCase();
      
      // You must return a Promise when performing asynchronous tasks inside a Functions such as
      // writing to Firestore.
      // Setting an 'uppercase' field in Firestore document returns a Promise.
      return snap.ref.set({uppercase}, {merge: true});
      // [END makeUppercaseBody]
    });
// [END makeUppercase]

exports.new_visit_received = functions.firestore.document('/visits/{documentId}')
    .onCreate(async (snap, context) => {

      const visitNumber = snap.data().visitNumber;
      functions.logger.log('Nueva escala recibida', context.params.documentId, visitNumber);

      // Push the new message into Firestore using the Firebase Admin SDK.

      const msg = {
        to: 'franchofelez@gmail.com', // Change to your recipient
        from: 'franchofelez@gmail.com', // Change to your verified sender
        subject: 'Recibida Nueva escala ' + visitNumber,
        text: 'Se ha recibido una nueva escala en all4Maritime',
        html: 'Se ha recibido una nueva escala en <strong>all4Maritime</strong>',
      }

      const writeResult = await admin.firestore().collection('mail_messages').add(msg);

      const receiver = snap.data().receiver;
      if (receiver === undefined)
      {
        functions.logger.log('Escala sin receptor');
      }
      else
      {
        msg.to = receiver
        const writeResult = await admin.firestore().collection('mail_messages').add(msg);
      }
      
      return "OK";
    });


exports.send_new_mail = functions.firestore.document('/mail_messages/{documentId}')
    .onCreate(async (snap, context) => {

      const msg = snap.data();
      functions.logger.log('Nuevo mensaje a enviar', context.params.documentId, msg);

      const send_mail = false;
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
      return "";
      
    });

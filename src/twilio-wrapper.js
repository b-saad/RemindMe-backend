import { twilio_sid, twilio_auto_token, twilio_phone_number } from './config.json';

const client = require('twilio')(twilio_sid, twilio_auto_token);

/*
* Sends `message` to the `phoneNumber` provided then runs a
* @param phoneNumber - String
* @param message - String
* @param completion - (message) => {} 
*/
function sendMessage(phoneNumber, message, completion) {
    client.messages
        .create({
            body: message,
            from: twilio_phone_number,
            to: phoneNumber
        })
        .then(completion(message));
}

export {
    sendMessage
}

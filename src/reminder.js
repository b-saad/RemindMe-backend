import db from './db';
import { sendMessage } from './twilio-wrapper';

const CronJob = require('cron').CronJob;

/*
* Creates a reminder to be sent to `phoneNumber` at provided `date`
* @param phoneNumber: String
* @param message: String
* @param date: String - UTC 'YYYY-MM-DDThh:mm:ssZ'
* @param callback: (err) to be called when reminder has been complete
*/
function createReminder(phoneNumber, message, date, callback) {
    const insertQuery = `INSERT INTO reminder (phone_number, message) VALUES ("${phoneNumber}", "${message}");`;
    const selectLastIdQuery = 'SELECT LAST_INSERT_ID();'
    db.query(insertQuery, (err, result) => {
        if (err) {
            callback(err);
            return;
        }
        db.query(selectLastIdQuery, (err, result) => {
            if (err) {
                callback(err);
                return;
            }
            sendReminder(result[0]['LAST_INSERT_ID()'], date);
            callback(null);
        });
    });
}


/*
* Sends a reminder with `reminderId` at provided `date`
* @param reminderId: int
* @param date: String - UTC 'YYYY-MM-DDThh:mm:ssZ'
*/
function sendReminder(reminderId, date) {
    new CronJob(
        new Date(date),
        function() {
            const selectReminderQuery = `SELECT * FROM reminder WHERE reminder_id = ${reminderId}`;
            db.query(selectReminderQuery, (err, result) => {
                if (err) {
                    console.log(`An error ocurred when retrieving the reminder: ${err}`);
                    return;
                }
                const { phone_number, message } = result[0];
                sendMessage(phone_number, message, (response) => console.log(response));
            });
            this.stop();
            deleteReminder(reminderId);
        },
        null,
        true
    );
}

function deleteReminder(reminderId) {
    const deleteReminderQuery = `DELETE FROM reminder WHERE reminder_id = ${reminderId}`;
    db.query(deleteReminderQuery, (err, result) => {
        if (err) {
            console.log(`An error ocurred when deleting the reminder: ${err}`);
            return;
        }
    });
}

export {
    createReminder
}

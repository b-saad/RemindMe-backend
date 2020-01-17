import { db_host, db_user, db_password, db_name } from './config.json';
import { sendMessage } from './twilio-wrapper';

const CronJob = require('cron').CronJob;
const DB_CONFIG = {
    host: db_host,
    user: db_user,
    password: db_password,
    database: db_name
};

const mysql = require('mysql');

/*
* Creates a reminder to be sent to `phoneNumber` at provided `date`
* @param phoneNumber: String
* @param message: String
* @param date: String - UTC 'YYYY-MM-DDThh:mm:ssZ'
* @param callback: (err) to be called when reminder has been complete
*/
async function createReminder(phoneNumber, message, date, callback) {
    const insertQuery = `INSERT INTO reminder (phone_number, message) VALUES ("${phoneNumber}", "${message}");`;
    const selectLastIdQuery = 'SELECT LAST_INSERT_ID();'
    try {
        const connection = await mysql.createConnection(DB_CONFIG);
        connection.query(insertQuery, (err, result) => {
            if (err) {
                callback(err);
                return;
            }
            connection.query(selectLastIdQuery, (err, result) => {
                if (err) {
                    callback(err);
                    return;
                }
                connection.end();
                sendReminder(result[0]['LAST_INSERT_ID()'], date);
                callback(null);
            });
        });
    } catch (err) {
        console.log('createReminder caught' + err);
    }
}


/*
* Sends a reminder with `reminderId` at provided `date`
* @param reminderId: int
* @param date: String - UTC 'YYYY-MM-DDThh:mm:ssZ'
*/
function sendReminder(reminderId, date) {
    new CronJob(
        new Date(date),
        async function() {
            const selectReminderQuery = `SELECT * FROM reminder WHERE reminder_id = ${reminderId}`;
            try {
                const connection = await mysql.createConnection(DB_CONFIG);
                connection.query(selectReminderQuery, (err, result) => {
                    if (err) {
                        console.log(`An error ocurred when retrieving the reminder: ${err}`);
                        return;
                    }
                    const { phone_number, message } = result[0];
                    sendMessage(phone_number, `RemindMe - ${message}`, (message) => {});
                    deleteReminder(reminderId);
                    connection.end();
                });
                this.stop();
            } catch (err) {
                console.log('sendReminder caught' + err);
            }
        },
        null,
        true
    );
}

async function deleteReminder(reminderId) {
    const deleteReminderQuery = `DELETE FROM reminder WHERE reminder_id = ${reminderId}`;
    try {
        const connection = await mysql.createConnection(DB_CONFIG);
        connection.query(deleteReminderQuery, (err, result) => {
            if (err) {
                console.log(`An error ocurred when deleting the reminder: ${err}`);
                return;
            }
            connection.end();
        });
    } catch (err) {
        console.log('deleteReminder caught' + err);
    }
}

export {
    createReminder
}

import express from 'express';
import bodyParser from 'body-parser';
import db from './db' ;

const CronJob = require('cron').CronJob;
const app = express();
const PORT = 8000;

app.use(bodyParser.json());

// TEST ENDPOINT
app.get('/api/reminders', (req, res) => {
    const query = 'SELECT * FROM reminder;'
    db.query(query, (err, result) => {
        res.status(200).send(`Reminders:\n \'${JSON.stringify(result)}\'`);
    });
});

// TEST ENDPOINT
app.post('/api/cron', (req, res) => {
    const { date } = req.body;
    new CronJob(
        new Date(date),
        function() {
            console.log('cron job fired');
            this.stop();
        },
        null,
        true
    );
    res.status(200).send();
});

/*
* Request body needs to have 3 fields
* phoneNumber - String
* message - String
* date - String - UTC 'YYYY-MM-DDThh:mm:ssZ'
*/
app.post('/api/remind', (req, res) => {
    const { phoneNumber, message, date } = req.body;
    const insertQuery = `INSERT INTO reminder (phone_number, message) VALUES ("${phoneNumber}", "${message}");`;
    const selectLastIdQuery = 'SELECT LAST_INSERT_ID();'
    db.query(insertQuery, (err, result) => {
        if (err) {
            res.status(500).send(`An error ocurred: ${err}`);
            return;
        }
        db.query(selectLastIdQuery, (err, result) => {
            if (err) {
                res.status(500).send(`An error ocurred: ${err}`);
                return;
            }
            sendReminder(result[0]['LAST_INSERT_ID()'], date);
        });
        res.status(200).send(`inserted`);
    });
});

/*
* Sends a reminder with `reminder_id` at provided `date`
* @param reminder_id: int
* @param date: String - UTC 'YYYY-MM-DDThh:mm:ssZ'
*/
function sendReminder(reminder_id, date) {
    new CronJob(
        new Date(date),
        function() {
            const selectReminderQuery = `SELECT * FROM reminder WHERE reminder_id = ${reminder_id}`;
            db.query(selectReminderQuery, (err, result) => {
                if (err) {
                    console.log(`An error ocurred when retrieving the reminder: ${err}`);
                    return;
                }
                const { phone_number, message } = result[0];
                console.log(`${phone_number} - ${message}`);
            
                });
            this.stop();
        },
        null,
        true
    );
}

app.listen(PORT, () => 
    console.log(`Listening on port ${PORT}`)
);


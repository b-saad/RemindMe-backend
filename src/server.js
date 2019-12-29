import express from 'express';
import bodyParser from 'body-parser';
import db from './db' ;
import { createReminder } from './reminder';

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
    createReminder(phoneNumber, message, date, (err) => { 
        if (err) {
            res.status(500).send(`An error ocurred: ${err}`)
        } else {
            res.status(200).send(`${date}`);
        }
    });
});

app.listen(PORT, () => 
    console.log(`Listening on port ${PORT}`)
);


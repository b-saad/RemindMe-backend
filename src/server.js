import express from 'express';
import bodyParser from 'body-parser';
import { db_host, db_user, db_password, db_name } from './config.json';

const mysql = require('mysql');
const app = express();
const PORT = 8000;

const db = mysql.createConnection ({
    host: db_host,
    user: db_user,
    password: db_password,
    database: db_name
});



app.use(bodyParser.json());

// TEST ENDPOINT
app.get('/api/reminders', (req, res) => {
    db.connect((err) => {
        if (err) throw err;
        console.log('Connected!');
    });

    const query = "SELECT * FROM reminder";
    db.query(query, (err, result) => {
        // console.log(result);
        res.status(200).send(`Reminders:\n \'${JSON.stringify(result)}\'`);
    });

    db.end();
});

app.post('/api/remind', (req, res) => {
    const { phoneNumber, date, message } = req.body;
    res.status(200).send(`The message \'${message}\' will be sent to ${phoneNumber} on ${date}`);
});

app.listen(PORT, () => 
    console.log(`Listening on port ${PORT}`)
);


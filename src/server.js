import express from 'express';
import bodyParser from 'body-parser';
import { path_to_ssl_cert, path_to_ssl_private_key, path_to_ssl_chain } from './config.json';
import { createReminder } from './reminder';
import { validFutureDate } from './utility';

// Dependencies
const fs = require('fs');
const http = require('http');
const https = require('https');

const app = express();
const HTTP_PORT = 8000;
const HTTPS_PORT = 9000;

// To fix CORS errors
app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

/* 
* Certificates from letsencrypt - file paths should be of format
* "/etc/letsencrypt/live/{domain}/{file}"
*/
const privateKey = fs.readFileSync(path_to_ssl_private_key, 'utf8');
const certificate = fs.readFileSync(path_to_ssl_cert, 'utf8');
const ca = fs.readFileSync(path_to_ssl_chain, 'utf8');

const credentials = {
	key: privateKey,
	cert: certificate,
	ca: ca
};

app.use(bodyParser.json());

/*
* Request body needs to have 3 fields
* phoneNumber - String
* message - String
* date - String - UTC 'YYYY-MM-DDThh:mm:ssZ'
*/
app.post('/remind', (req, res) => {
    console.log('reminder request received');
    const { phoneNumber, message, date } = req.body;
    if (!validFutureDate(date)) {
        res.status(500).send(`Please provide a time in the future`);
        console.log(err);
        return
    }
    createReminder(phoneNumber, message, date, (err) => {
        if (err) {
            res.status(500).send(`An error ocurred`);
            console.log(err);
        } else {
            res.status(200).send(`Reminder will be sent on ${date}`);
        }
    });
});

// Starting both http & https servers
const httpServer = http.createServer(app);
const httpsServer = https.createServer(credentials, app);

httpServer.listen(HTTP_PORT, () => {
	console.log(`HTTP Server running on port ${HTTP_PORT}`);
});

httpsServer.listen(HTTPS_PORT, () => {
	console.log(`HTTPS Server running on port ${HTTPS_PORT}`);
});

import express from 'express';
import bodyParser from 'body-parser';

const app = express();
const PORT = 8000;

app.use(bodyParser.json());

app.post('/api/remind', (req, res) => {
    const { phoneNumber, date, message } = req.body;
    res.status(200).send(`The message \'${message}\' will be sent to ${phoneNumber} on ${date}`);
});

app.listen(PORT, () => 
    console.log(`Listening on port ${PORT}`)
);

import express from 'express';

const app = express();
const PORT = 8000;

app.post('/remind', (req, res) => 
    res.send('reminded')
);

app.listen(PORT, () => 
    console.log(`Listening on port ${PORT}`)
);

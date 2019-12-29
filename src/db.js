import { db_host, db_user, db_password, db_name } from './config.json';

const mysql = require('mysql');

const db = mysql.createConnection ({
    host: db_host,
    user: db_user,
    password: db_password,
    database: db_name
});

export default db;

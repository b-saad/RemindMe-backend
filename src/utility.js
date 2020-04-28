/*
* Checks if provided date is in the future
* @param date - String - UTC 'YYYY-MM-DDThh:mm:ssZ'
*/
function validFutureDate(date) {
    const now = new Date();
    const dateObject = Date.parse(date);
    return now > dateObject;
}

export {
    validFutureDate
}

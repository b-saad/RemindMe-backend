/*
* Checks if provided date is in the future
* @param date - String - UTC 'YYYY-MM-DDThh:mm:ssZ'
*/
function validFutureDate(date) {
    const now = new Date();
    const dateObject = Date.parse(date);
    console.log('now: ' + now)
    console.log('date: ' + dateObject)
    return now > dateObject;
}

export {
    validFutureDate
}

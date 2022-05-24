import winston from 'winston';

export function HandleAxiosError(error) {
    if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        winston.error(`Request failed. HTTP status: ${error.response.status}. Message: ${JSON.stringify(error.response.data)}.`);
    } else if (error.request) {
        // The request was made but no response was received
        // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
        // http.ClientRequest in node.js
        winston.error('The request was made but no response was received');
    } else {
        // Something happened in setting up the request that triggered an Error
        winston.error('Failed to perform request', error.message);
    }
    return Promise.reject(error);
}
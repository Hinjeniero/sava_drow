const express = require('express');
const bodyParser = require('body-parser');
const app = express();
var PORT = process.env.PORT || 9001;
var serversHosting = []
require("dotenv").config();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

JSON_MISSING_PARAMS = {success: false, message: 'Missing fields'}
JSON_SERVER_NOT_FOUND = {success: false, message: 'The server with that uuid was not found'}

const addHostMiddleware = () => {
    return (req, res, next) => {
        let requiredFields = 
            {
                uuid: false,
                ip: false, 
                port: false,
                timestamp: false,
                players: false
            };
        for (const el of Object.keys(req.body)) {
            requiredFields[el] = true;
        }
        for (const el of Object.keys(requiredFields)) {
            if (!requiredFields[el]){ return res.json(400, JSON_MISSING_PARAMS)}
        }
        next();
    }
}

const updateHostMiddleware = () => {
    return (req, res, next) => {
        let requiredFields = {uuid: false};
        for (const el of Object.keys(req.body)) {
            requiredFields[el] = true;
        }
        for (const el of Object.keys(requiredFields)) {
            if (!requiredFields[el]){ return res.json(400, JSON_MISSING_PARAMS)}
        }
        next();
    }
}

app.post('/host/add/', addHostMiddleware(), (req, res) => {
    data = {uuid: req.body.uuid, ip: req.body.ip, port: req.body.port, players: req.body.players, date: req.body.timestamp}
    serversHosting.push(data);
    console.log(serversHosting)
    res.json(200, {success: true, message: 'Your server with uuid '+data['uuid']+' was added succesfully'})
});

app.post('/host/update', updateHostMiddleware(), (req, res) => {
    var uuid = req.body.uuid
    for (var i = 0; i < serversHosting.length; i++){
        if (uuid === serversHosting[i]['uuid']){
            for (const el of Object.keys(serversHosting[i])){
                (el in req.body && el) && (serversHosting[i][el] = req.body[el])
            }
            res.json(200, {success: true, message: 'Server updated successfully', data: serversHosting[i]})
            return
        }
    }
    res.json(400, JSON_SERVER_NOT_FOUND)
});

app.get('/host/get/all', (req, res) => {
    res.json(200, {success: true, message: 'Servers retrieved successfully', data: serversHosting})
});

app.post('/host/delete', (req, res) => {
    var uuid = req.body.uuid
    for (var i = 0; i < serversHosting.length; i++){
        if (uuid === serversHosting[i]['uuid']){
            serversHosting.splice(i, 1)
            res.json(200, {success: true, message: 'Your server with uuid '+uuid+' was deleted successfully'})
            return
        }
    }
    res.json(400, JSON_SERVER_NOT_FOUND)
});

app.listen(PORT, () => {
    console.log(`server running on port ${PORT}`)
});
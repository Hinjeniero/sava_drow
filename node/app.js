const express = require('express');
const bodyParser = require('body-parser');
const app = express();
var PORT = process.env.PORT || 9001;
var serversHosting = []
require("dotenv").config();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

//This fuckin undefined shit
const addHostMiddleware = () => {
    return (req, res, next) => {
        console.log(req.body)
        if (req.body.uuid === undefined || req.body.ip === undefined || req.body.port === undefined || req.body.players === undefined || req.body.timestamp === undefined) {
            res.status(400).send('Missing params')
        } else {
            next()
        }
    }
}

app.post('/host/add/', addHostMiddleware(), (req, res) => {
    data = {uuid: req.body.uuid, ip: req.body.ip, port: req.body.port, players: req.body.players, date: req.body.timestamp}
    serversHosting.push(data);
    res.status(200).send({
      success: 'true',
      message: 'todos retrieved successfully',
      ip: 'New servers are '+serversHosting
    })
});

//Asynchronous loop that asks for a response on each server that is in the hosting shit

app.post('/hosting/update', (req, res) => {
    var uuid = req.body.uuid
    var server = "Whatever server comes out in the for loop"
    //for host in serversHosting:
        //Async non blocking IO operation
    if (server === undefined){
        res.status(400).send("We didnt find the server with that uuid")
    }else{
        res.status(200).send({
        success: 'true',
        message: 'todos retrieved successfully',
        update: 'The new server data is '+server
        })
    }
});

app.get('/hosting/get/all', (req, res) => {
    res.status(200).send({
      success: 'true',
      message: 'todos retrieved successfully',
      data: 'Available servers are '+serversHosting
    })
});

app.post('/hosting/delete', (req, res) => {
    var uuid = req.body.uuid
    var server = "Whatever server comes out in the for loop"
    //for host in serversHosting:
        //Async non blocking IO operation to search for that fuckin uuid
    if (server === undefined){
        res.status(400).send("We didnt find the server with that uuid")
    }else{
        res.status(200).send({
        success: 'true',
        message: 'todos retrieved successfully',
        update: 'The deleted server data is '+server
        })
    }
});

app.listen(PORT, () => {
    console.log(`server running on port ${PORT}`)
});
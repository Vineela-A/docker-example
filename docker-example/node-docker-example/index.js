var createError = require('http-errors');
var express = require('express');
var path = require('path');
const fs = require('fs');
const bodyParser = require("body-parser");
var morgan = require('morgan');
const cors = require('cors');
const app = express();              //Instantiate an express app, the main work horse of this server
const port = 5000;                  //Save the port number where your server will be listening

// tutorial routes
// require("./routes/diskspace.routes.js")(app);

const corsOptions = {
    origin: '*'
};

// const accessLogStream = fs.createWriteStream('./logs/', 'access.log');
var accessLogStream = fs.createWriteStream(path.join('./logs/', 'access.log'), { flags: 'a' })

// parse requests of content-type - application/json
app.use(bodyParser.json());

// parse requests of content-type - application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }));
/**
 * Log HTTP errors to access.log file
 */
app.use(morgan('combined', {
    stream: accessLogStream,
    // skip: (req, res) => { // to skip all the errors with status code less than 400
    //     return res.statusCode < 400
    // }
}));
app.use(cors(corsOptions));

// This applies for every REST API request
app.use(function(req, res, next) {
    const mockAuthCode = Date.now();
    res.setHeader("Content-Type", "application/json");
    res.removeHeader("X-Powered-By");
    next();
});

// app.use(express.urlencoded({ extended: false }));
// app.use(express.json());

// call sysc()
const db = require("./app/models");
db.sequelize.sync();

var diskSpaceRouter = require('./routes/diskspace.routes');
app.use('/diskspace', diskSpaceRouter);

app.use(async (req, res, next) => {
    next(createError.NotFound())
});

app.use((err, req, res, next) => {
    console.log('ERR STATUS :: ', err.status);
    if ( err.status === 400) {
        res.send({
            status: err.status,
            message: err.message
        })
    } else {
        res.status(err.status || 500);
        res.send({
            error: {
                status: err.status || 500,
                message: err.message
            }
        })
    }
})

app.listen(port, () => {            //server starts listening for any attempts from a client to connect at port: {port}
    console.log(`Now listening on port ${port}`); 
});

app.use(function(req, res, next) {
    req.getUrl = function() {
      return req.protocol + "://" + req.get('host') + req.originalUrl;
    }
    return next();
  });


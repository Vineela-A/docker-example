const sql = require('../config/db.config');
const dfParser = require('../../df-parser');
const res = require('express/lib/response');
const createError = require('http-errors');
const db = require("../models");
const Diskspace = db.diskspace;
const Op = db.Sequelize.Op;
var tableName = process.env.DISK_SPACE

/*
async function queryPromise1(tableName, insKeys, insValues) {
    return new Promise((resolve, reject) => {
        sql.query("INSERT INTO "+tableName+" ("+insKeys+") VALUES ("+insValues+")", (err, results) => {
            if (err) {
                reject(err)
            } else {
                message = 'Record inserted successfully';
                resolve(message);
            }
        });
    });
};
*/

// Retrieve all Tutorials from the database.



  
module.exports = {
    getAllDiskSpaceData : async (req, res) => {
        sql.query("SELECT * FROM "+tableName, (err, results) => {
            if (err) {
                console.log("error: ", err);
                return res.render(err);
            } else {
                // const categories = results.map(x => ({
                //     id: x.PackageID,
                //     catname: x.PackageType
                // }));
                res.json({'diskSpaceData': results});
            }
        });
    },

    insertDiskSpaceDetails : async(req, res) => {
        try {
            const reqBody = req.body;

            var exclusionList = ["/System/Volumes/Data/home", "/Volumes/Recovery", "/System/Volumes/Preboot", "/Volumes/Bitdefender", "/Volumes/XAMPP"];
            var keys = "";
            var values = "";
            var ip = reqBody.node_ip;
            sql.query("SELECT * FROM "+tableName + " WHERE node_ip='"+ ip +"'", (err, results) => {
                var message = "";
                if (err) {
                    console.log("error: ", err);
                    return res.render(err);
                } else {
                    if (results.length > 0) {
                        console.log(results[0]['id']);
                        sql.query("DELETE FROM "+tableName + " WHERE node_ip='"+ ip + "'", (errDelete, deleteResults) => {
                            if (errDelete) {
                                console.log("error: ", errDelete);
                                return res.render(errDelete);
                            } else {
                                console.log("Data already exists for ip "+ip+" so deleted the existing data");
                            }
                        });
                    }
                    for (const key in req.body) {
                        if (req.body.hasOwnProperty(key)) {
                            let value = req.body[key];
                            keys += "`"+key+"`,";
                            values += "'"+value.replaceAll("'", "\'")+"',";
                            if (key == "node_log") {
                                var nodeLog = decodeURIComponent(value);
                                var parsedContent = dfParser.parseDfResponse(nodeLog);

                                var string1 = "/Volumes";
                                var string2 = "/System/Volumes/Data";
                            
                                var result1 = Object.assign({}, parsedContent);
                                var result2 = Object.assign({}, parsedContent);
                                for (let i = 0; i < Object.keys(parsedContent).length; i++) {
                                    var mountedOnString1 = parsedContent[Object.keys(parsedContent)[i]]['mounted_on'].indexOf(string1)
                                    var mountedOnString2 = parsedContent[Object.keys(parsedContent)[i]]['mounted_on'].indexOf(string2)
                                    if (mountedOnString1) {
                                        delete result1[Object.keys(parsedContent)[i]];
                                    }
                                    if (mountedOnString2) {
                                        delete result2[Object.keys(parsedContent)[i]];
                                    }
                                }

                                var totalMatches1 = Object.keys(result1).length
                                var totalMatches2 =  Object.keys(result2).length
                            
                                Object.keys(parsedContent).forEach(async(key) => {
                                    var insKeys = keys
                                    var insValues = values
                                
                                    if (totalMatches2 > 0) {
                                        if(!exclusionList.includes(parsedContent[key]['mounted_on']) && !parsedContent[key]['mounted_on'].indexOf(string1)) {
                                            // console.log("else", parsedContent[key]['mounted_on']);
                                            insKeys += "`node_location`, ";
                                            insValues += "'"+parsedContent[key]['mounted_on']+"', ";
                                            insKeys += "`total_space`, ";
                                            insValues += "'"+parsedContent[key]['1k_blocks']+"', ";
                                            insKeys += "`used_space`, ";
                                            insValues += "'"+parsedContent[key]['used']+"', ";
                                            insKeys += "`free_space`";
                                            insValues += "'"+parsedContent[key]['available']+"'";
                                            message = await queryPromise1(tableName, insKeys, insValues);
                                            res.write(JSON.stringify({status: 'OK', message: message}));
                                        }
                                    } else {
                                        if(parsedContent[key]['mounted_on'] == "/" || (!exclusionList.includes(parsedContent[key]['mounted_on']) && !parsedContent[key]['mounted_on'].indexOf(string1))) {
                                            // console.log("else", parsedContent[key]['mounted_on']);
                                            insKeys += "`node_location`, ";
                                            insValues += "'"+parsedContent[key]['mounted_on']+"', ";
                                            insKeys += "`total_space`, ";
                                            insValues += "'"+parsedContent[key]['1k_blocks']+"', ";
                                            insKeys += "`used_space`, ";
                                            insValues += "'"+parsedContent[key]['used']+"', ";
                                            insKeys += "`free_space`";
                                            insValues += "'"+parsedContent[key]['available']+"'";
                                            message = await queryPromise1(tableName, insKeys, insValues);
                                            res.write(JSON.stringify({status: 'OK', message: message}));
                                        }
                                    }
                                    if(message != "") {
                                        res.send();
                                    }
                                });
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.log(error);
            throw error;
        }
    }
}

var express = require('express');
var router = express.Router();

const DiskSpaceController = require("../app/controllers/DiskSpaceController");

/* GET diskspace listing. */
// router.route('/').get(DiskSpaceController.findAll);

// Retrieve all Tutorials
router.route('/diskspace').get(DiskSpaceController.getAllDiskSpaceData);

router.route('/insertDiskSpaceDetails').post(DiskSpaceController.insertDiskSpaceDetails);

module.exports = router;
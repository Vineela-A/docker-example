const { DataTypes } = require("sequelize");

module.exports = (sequelize, Sequelize) => {
    const Diskspace = sequelize.define("diskspaces", {
      id: {
        type: DataTypes.INTEGER,
        primaryKey: true
      },
      node_log: {
        type: Sequelize.STRING
      },
      node_name: {
        type: Sequelize.STRING
      },
      node_location: {
        type: Sequelize.STRING
      },
      node_ip: {
        type: Sequelize.STRING
      },
      total_space: {
        type: Sequelize.STRING
      },
      used_space: {
        type: Sequelize.STRING
      },
      free_space: {
        type: Sequelize.STRING
      },
      date_time: {
        type: DataTypes.DATE
      }
    }, {
      timestamps: false
    });
  
    return Diskspace;
  }; 
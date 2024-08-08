const axios = require('axios');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const storageService = require('../services/storageService');

const NODE_CONFIG_PATH = path.join(__dirname, '../node_config.json');
const BASE_URL = process.env.BASE_URL || 'http://localhost:5000/api';

const replicateData = async (filename) => {
  try {
    if (fs.existsSync(NODE_CONFIG_PATH)) {
      const config = JSON.parse(fs.readFileSync(NODE_CONFIG_PATH, 'utf8'));
      const filePath = storageService.getFilePath(config.nodeId, filename);

      if (fs.existsSync(filePath)) {
        const data = fs.readFileSync(filePath, 'utf8');
        const checksum = crypto.createHash('sha256').update(data).digest('hex');

        const replicationRequest = {
          SourceNodeId: config.nodeId,
          DestinationNodeId: 'DestinationNodeId', // Replace with actual destination node ID
          Filename: filename,
          Data: data,
          Checksum: checksum
        };

        await axios.post(`${BASE_URL}/replication/replicate`, replicationRequest, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
      }
    }
  } catch (error) {
    console.error('Failed to replicate data:', error.message);
  }
};

module.exports = {
  replicateData
};

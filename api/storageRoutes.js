const express = require('express');
const router = express.Router();
const storageService = require('../services/storageService');
const replicationService = require('../services/replicationService');
const monitoringService = require('../services/monitoringService');
const axios = require('axios');
const multer = require('multer');
const upload = multer();
require('dotenv').config();

// Create an axios instance with custom configuration
const axiosInstance = axios.create({
  httpsAgent: new (require('https')).Agent({ rejectUnauthorized: false })
});

let failedAuthAttempts = 0; // Variable to track failed authentication attempts

const incrementFailedAuthAttempts = () => {
    failedAuthAttempts += 1;
};

const getFailedAuthAttempts = () => {
    return failedAuthAttempts;
};

// Authentication Middleware
const authenticate = async (req, res, next) => {
    const authHeader = req.headers['authorization'];
    if (!authHeader) {
        console.log('Authorization header missing');
        incrementFailedAuthAttempts();
        return res.sendStatus(401);
    }

    const token = authHeader.split(' ')[1];
    console.log(`Received token: ${token}`);

    try {
        const response = await axiosInstance.post(`${process.env.BASE_URL}/Token/verify`, { token });

        if (response.status === 200) {
            console.log('Token verification successful');
            req.user = response.data;
            next();
        } else {
            console.log('Token verification failed');
            incrementFailedAuthAttempts();
            res.sendStatus(403);
        }
    } catch (error) {
        console.error('Token verification failed:', error.message);
        incrementFailedAuthAttempts();
        res.sendStatus(403);
    }
};

// Authentication Endpoint
router.post('/authenticate', async (req, res) => {
    const { token } = req.body;
    try {
        // Authentication logic...
        const response = await axiosInstance.post(`${process.env.BASE_URL}/Token/verify`, { token });

        if (response.status === 200) {
            res.status(200).send('Authenticated');
        } else {
            incrementFailedAuthAttempts();
            res.status(401).send('Authentication failed');
        }
    } catch (error) {
        console.error('Authentication error:', error.message);
        incrementFailedAuthAttempts();
        res.status(500).send('Authentication error');
    }
});

// Get Failed Authentication Attempts
router.get('/status/auth-attempts', authenticate, async (req, res) => {
    try {
        const failedAttempts = getFailedAuthAttempts();
        res.status(200).json({ failedAttempts });
    } catch (error) {
        console.error('Failed to get auth attempts:', error.message);
        res.status(500).send('Failed to get auth attempts');
    }
});

const os = require('os');

// Helper functions to get CPU and memory usage
const getCpuUsage = () => {
    return new Promise((resolve, reject) => {
        const startTime = process.hrtime();
        const startUsage = process.cpuUsage();

        setTimeout(() => {
            const elapTime = process.hrtime(startTime);
            const elapUsage = process.cpuUsage(startUsage);

            const elapTimeMS = elapTime[0] * 1000 + elapTime[1] / 1000000;
            const elapUserMS = elapUsage.user / 1000;
            const elapSystMS = elapUsage.system / 1000;

            const cpuPercent = (100 * (elapUserMS + elapSystMS) / elapTimeMS).toFixed(2);
            resolve(cpuPercent);
        }, 100);
    });
};

const getMemoryUsage = () => {
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const usedMemory = totalMemory - freeMemory;

    return {
        totalMemory: (totalMemory / 1024 / 1024).toFixed(2),  // in MB
        usedMemory: (usedMemory / 1024 / 1024).toFixed(2),    // in MB
        freeMemory: (freeMemory / 1024 / 1024).toFixed(2)     // in MB
    };
};

// Resource Monitoring Endpoint
router.get('/status/resource-usage', authenticate, async (req, res) => {
    try {
        const cpuUsage = await getCpuUsage();
        const memoryUsage = getMemoryUsage();

        res.status(200).json({
            cpuUsage: `${cpuUsage}%`,
            memoryUsage
        });
    } catch (error) {
        console.error('Failed to get resource usage:', error.message);
        res.status(500).send('Failed to get resource usage');
    }
});

// Define routes
router.post('/upload', authenticate, upload.single('file'), async (req, res) => {
  const { userId, filename } = req.body;
  const data = req.file.buffer; // Get the file buffer

  try {
    storageService.saveFile(userId, filename, data);
    await replicationService.replicateData(filename); // Trigger replication after upload
    res.status(200).send('File uploaded and replicated successfully');
  } catch (error) {
    console.error('Error uploading file:', error.message);
    res.status(400).send(error.message);
  }
});

// Get storage stats
router.get('/stats', authenticate, (req, res) => {
  const stats = storageService.getStorageStats();
  res.status(200).json(stats);
});

// Delete a file
router.delete('/delete', authenticate, (req, res) => {
  const { userId, filename } = req.body;

  try {
    storageService.deleteFile(userId, filename);
    res.status(200).send('File deleted successfully');
  } catch (error) {
    res.status(400).send(error.message);
  }
});

// View a file
router.get('/view/:userId/:filename', authenticate, (req, res) => {
  const { userId, filename } = req.params;

  try {
    const fileContent = storageService.getFile(userId, filename);
    res.status(200).send(fileContent);
  } catch (error) {
    res.status(400).send(error.message);
  }
});

// Download a file
router.get('/download/:userId/:filename', authenticate, (req, res) => {
  const { userId, filename } = req.params;

  try {
    const fileContent = storageService.getFile(userId, filename);
    res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
    res.send(fileContent);
  } catch (error) {
    res.status(400).send(error.message);
  }
});

// Search data
router.get('/search', authenticate, (req, res) => {
  const { userId, query } = req.query;

  try {
    const results = storageService.searchData(userId, query);
    res.status(200).json(results);
  } catch (error) {
    res.status(400).send(error.message);
  }
});

// Rename a file
router.post('/rename', authenticate, (req, res) => {
  const { userId, oldFilename, newFilename } = req.body;

  try {
    storageService.renameFile(userId, oldFilename, newFilename);
    res.status(200).send('File renamed successfully');
  } catch (error) {
    res.status(400).send(error.message);
  }
});

// Get file size
router.get('/file-size/:filename', authenticate, (req, res) => {
  const { filename } = req.params;
  const fileSize = storageService.getFileSize(filename);
  res.status(200).send(fileSize.toString());
});

// Ping endpoint to check if the storage node is online and authenticated
router.get('/ping', authenticate, (req, res) => {
  try {
    res.status(200).send('Storage node is online and authenticated');
  } catch (error) {
    console.error('Ping check failed:', error.message);
    res.status(500).send('Storage node is online but encountered an error');
  }
});

module.exports = router;


module.exports = router;

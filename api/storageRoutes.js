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
  httpsAgent: new (require('https')).Agent({ rejectUnauthorized: false }) // Allow self-signed certificates
});

// Middleware to check authentication
const authenticate = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  if (!authHeader) {
    console.log('Authorization header missing');
    return res.sendStatus(401);
  }

  const token = authHeader.split(' ')[1];
  console.log(`Received token: ${token}`);

  try {
    const response = await axiosInstance.post(`${process.env.BASE_URL}/token/verify`, { token });
    if (response.status === 200) {
      req.user = response.data;
      next();
    } else {
      res.sendStatus(403);
    }
  } catch (error) {
    console.error('Token verification failed:', error.message);
    res.sendStatus(403);
  }
};

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

module.exports = router;

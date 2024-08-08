const fs = require('fs');
const path = require('path');

const saveFile = (userId, filename, data) => {
  const userDir = path.join(__dirname, '..', 'data', userId);
  if (!fs.existsSync(userDir)) {
    fs.mkdirSync(userDir, { recursive: true });
  }
  const filePath = path.join(userDir, filename);
  fs.writeFileSync(filePath, data); // Save binary data
};

const getFile = (userId, filename) => {
  const filePath = path.join(__dirname, '..', 'data', userId, filename);
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath); // Read binary data
  }
  throw new Error('File not found');
};

const deleteFile = (userId, filename) => {
  const filePath = path.join(__dirname, '..', 'data', userId, filename);
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
  } else {
    throw new Error('File not found');
  }
};

const getStorageStats = () => {
  // Implement storage statistics logic
  return { used: 0, available: 1000 };
};

const renameFile = (userId, oldFilename, newFilename) => {
  const oldFilePath = path.join(__dirname, '..', 'data', userId, oldFilename);
  const newFilePath = path.join(__dirname, '..', 'data', userId, newFilename);
  if (fs.existsSync(oldFilePath)) {
    fs.renameSync(oldFilePath, newFilePath);
  } else {
    throw new Error('File not found');
  }
};

const getFileSize = (filename) => {
  const stats = fs.statSync(filename);
  return stats.size;
};

const searchData = (userId, query) => {
  const userDir = path.join(__dirname, '..', 'data', userId);
  const results = [];
  if (fs.existsSync(userDir)) {
    const files = fs.readdirSync(userDir);
    files.forEach(file => {
      if (file.includes(query)) {
        results.push(file);
      }
    });
  }
  return results;
};

module.exports = {
  saveFile,
  getFile,
  deleteFile,
  getStorageStats,
  renameFile,
  getFileSize,
  searchData
};

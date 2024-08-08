const axios = require('axios');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec } = require('child_process');
const storageService = require('../services/storageService');

const NODE_CONFIG_PATH = path.join(__dirname, '../node_config.json');
const BASE_URL = process.env.BASE_URL || 'http://localhost:5000/api';

let downtimeStart = null;

const reportNodeStatus = async () => {
  try {
    if (fs.existsSync(NODE_CONFIG_PATH)) {
      const config = JSON.parse(fs.readFileSync(NODE_CONFIG_PATH, 'utf8'));

      const uptime = getUptime();
      const storageStats = storageService.getStorageStats();
      const onlineStatus = await getOnlineStatus();
      const systemHealth = await getSystemHealth();
      const downtime = getDowntime();
      const causeOfDowntime = getCauseOfDowntime();

      const statusData = {
        NodeId: config.nodeId,
        Uptime: uptime,
        StorageStats: storageStats,
        OnlineStatus: onlineStatus,
        SystemHealth: systemHealth,
        Downtime: downtime,
        CauseOfDowntime: causeOfDowntime
      };

      await axios.post(`${BASE_URL}/nodes/status`, statusData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }
  } catch (error) {
    console.error('Failed to report node status:', error.message);
  }
};

const getUptime = () => {
  return os.uptime();
};

const getOnlineStatus = async () => {
  return new Promise((resolve, reject) => {
    exec('ping -n 1 google.com', (error, stdout, stderr) => { // Adjusted for Windows
      if (error) {
        downtimeStart = new Date();
        resolve(false);
      } else {
        downtimeStart = null;
        resolve(true);
      }
    });
  });
};

const getSystemHealth = async () => {
  const memoryStats = getMemoryStats();
  const cpuStats = getCpuStats();
  const storageStats = storageService.getStorageStats();
  const gpuStats = await getGpuHealth();

  return {
    memory: memoryStats,
    cpu: cpuStats,
    storage: storageStats,
    gpu: gpuStats
  };
};

const getMemoryStats = () => {
  const totalMemory = os.totalmem();
  const freeMemory = os.freemem();
  return {
    total: totalMemory,
    free: freeMemory,
    used: totalMemory - freeMemory
  };
};

const getCpuStats = () => {
  const cpus = os.cpus();
  return cpus.map(cpu => ({
    model: cpu.model,
    speed: cpu.speed,
    times: cpu.times
  }));
};

const getGpuHealth = async () => {
  if (os.type() === 'Windows_NT') {
    return new Promise((resolve, reject) => {
      exec('wmic path win32_videocontroller get name,adapterram /format:csv', (error, stdout, stderr) => {
        if (error) {
          resolve(null); // No GPU or command not available
        } else {
          const lines = stdout.trim().split('\n');
          const gpuStats = lines.slice(1).map(line => {
            const [node, name, adapterram] = line.split(',');
            return {
              name,
              memory: `${parseInt(adapterram, 10) / (1024 * 1024)} MB`
            };
          });
          resolve(gpuStats);
        }
      });
    });
  } else {
    return new Promise((resolve, reject) => {
      exec('lshw -C display', (error, stdout, stderr) => {
        if (error) {
          resolve(null); // No GPU or command not available
        } else {
          const lines = stdout.trim().split('\n');
          const gpuStats = [];
          let currentGpu = null;
          lines.forEach(line => {
            if (line.includes('*-display')) {
              if (currentGpu) {
                gpuStats.push(currentGpu);
              }
              currentGpu = {};
            }
            if (line.includes('product:')) {
              currentGpu.name = line.split('product:')[1].trim();
            }
            if (line.includes('size:')) {
              currentGpu.memory = line.split('size:')[1].trim();
            }
          });
          if (currentGpu) {
            gpuStats.push(currentGpu);
          }
          resolve(gpuStats);
        }
      });
    });
  }
};

const getDowntime = () => {
  if (downtimeStart) {
    const currentTime = new Date();
    const downtime = (currentTime - downtimeStart) / 1000; // Downtime in seconds
    downtimeStart = null;
    return downtime;
  }
  return 0;
};

const getCauseOfDowntime = () => {
  if (downtimeStart) {
    return 'Network issues';
  }
  return 'None';
};

// Report node status every 10 minutes
setInterval(reportNodeStatus, 10 * 60 * 1000);

module.exports = {
  reportNodeStatus,
  getUptime,
  getOnlineStatus,
  getSystemHealth,
  getDowntime,
  getCauseOfDowntime
};

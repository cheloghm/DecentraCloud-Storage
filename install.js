const fs = require('fs');
const { exec } = require('child_process');
const os = require('os');
const path = require('path');

const STORAGE_DIR = path.join(__dirname, 'storage');

if (!fs.existsSync(STORAGE_DIR)) {
  fs.mkdirSync(STORAGE_DIR);
}

// Function to set permissions based on the OS
const setPermissions = () => {
  const platform = os.platform();

  if (platform === 'linux' || platform === 'darwin') {
    // Unix-based system
    exec(`chmod 700 ${STORAGE_DIR}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error setting permissions: ${error.message}`);
        return;
      }
      if (stderr) {
        console.error(`stderr: ${stderr}`);
        return;
      }
      console.log(`Permissions set to 700 for ${STORAGE_DIR}`);
    });
  } else if (platform === 'win32') {
    // Windows system
    exec(`attrib +h ${STORAGE_DIR}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error setting attributes: ${error.message}`);
        return;
      }
      if (stderr) {
        console.error(`stderr: ${stderr}`);
        return;
      }
      console.log(`Attributes set to hidden for ${STORAGE_DIR}`);
    });
  } else {
    console.error('Unsupported OS');
  }
};

// Set the permissions during installation
setPermissions();

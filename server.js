require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const storageRoutes = require('./api/storageRoutes');
const fs = require('fs');
const https = require('https');
const path = require('path');

const app = express();
let PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));
app.use('/storage', storageRoutes);

const httpsOptions = {
  key: fs.readFileSync(path.join(__dirname, 'certs', 'privatekey.pem')),
  cert: fs.readFileSync(path.join(__dirname, 'certs', 'certificate.pem'))
};

function startServer(port) {
  const server = https.createServer(httpsOptions, app).listen(port, () => {
    console.log(`Server is running on port ${port}`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`Port ${port} is already in use, trying another port...`);
      startServer(port + 1); // Try the next port
    } else {
      console.error(`Server error: ${err.message}`);
    }
  });

  return server;
}

const serverInstance = startServer(PORT);

// Handle graceful shutdown
process.on('SIGTERM', () => {
  serverInstance.close(() => {
    console.log('Server terminated');
    process.exit(0);
  });
});

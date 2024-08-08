# DecentraCloud Storage Node

## Overview

The DecentraCloud Storage Node is a key component of the DecentraCloud platform, allowing users to contribute storage space to a decentralized network. Users can store, manage, and retrieve files securely while earning cryptocurrency rewards for their contributions. This README provides instructions for setting up, configuring, and using the Storage Node.

## Features

- **Decentralized Storage**: Convert your machine into a storage node and contribute to the decentralized network.
- **Secure Data Storage**: Files are encrypted and securely stored across multiple nodes.
- **Cryptocurrency Mining**: Earn rewards based on storage contribution and system specifications.
- **API Endpoints**: Manage files via a RESTful API.
- **Monitoring**: Track system health, uptime, and storage statistics.

## Prerequisites

- Node.js (v14.x or later)
- Python 3.x
- Git
- OpenSSL (for generating SSL certificates)
- Internet connection

## Installation

### 1. Clone the Repository

```sh
git clone https://github.com/your-repo/DecentraCloud.git
cd DecentraCloud/Storage
```

### 2. Install Node.js Dependencies

```sh
npm install
```

### 3. Install Python Dependencies

```sh
pip install -r requirements.txt
```

### 4. Generate SSL Certificates

Generate self-signed SSL certificates for secure communication.

```sh
openssl req -nodes -new -x509 -keyout certs/privatekey.pem -out certs/certificate.pem
```

### 5. Configure Environment Variables

Create a `.env` file in the `Storage` directory with the following content:

```plaintext
PORT=3000
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=my_secret_key
STORAGE_LIMIT=1073741824 # 1GB
BASE_URL=https://localhost:7240/api
```

Replace the placeholder values with your actual configuration.

## Usage

### 1. Start the Server

```sh
npm start
```

The server will start on the port specified in the `.env` file (default is 3000).

### 2. Register the Storage Node

Use the provided CLI to register your storage node with the central server.

```sh
python node/cli.py register --email <your_email> --password <your_password> --storage <storage_space_in_GB> --nodename <node_name>
```

### 3. Authenticate the Storage Node

```sh
python node/cli.py login --nodename <node_name> --email <your_email> --password <your_password> --port <node_port>
```

## API Endpoints

### Upload a File

**Endpoint:** `POST /storage/upload`

**Description:** Uploads a file to the storage node.

**Example `curl` Command:**

```sh
curl -X POST https://localhost:3000/storage/upload \
-H "Authorization: Bearer <your_token>" \
-F "file=@path/to/your/file" \
-F "userId=<user_id>" \
-F "filename=<file_name>"
```

### Get Storage Stats

**Endpoint:** `GET /storage/stats`

**Description:** Retrieves storage statistics.

**Example `curl` Command:**

```sh
curl -X GET https://localhost:3000/storage/stats \
-H "Authorization: Bearer <your_token>"
```

### Delete a File

**Endpoint:** `DELETE /storage/delete`

**Description:** Deletes a specified file.

**Example `curl` Command:**

```sh
curl -X DELETE https://localhost:3000/storage/delete \
-H "Authorization: Bearer <your_token>" \
-H "Content-Type: application/json" \
-d '{"userId": "<user_id>", "filename": "<file_name>"}'
```

### View a File

**Endpoint:** `GET /storage/view/:userId/:filename`

**Description:** Views the content of a specified file.

**Example `curl` Command:**

```sh
curl -X GET https://localhost:3000/storage/view/<user_id>/<file_name> \
-H "Authorization: Bearer <your_token>"
```

### Download a File

**Endpoint:** `GET /storage/download/:userId/:filename`

**Description:** Downloads a specified file.

**Example `curl` Command:**

```sh
curl -X GET https://localhost:3000/storage/download/<user_id>/<file_name> \
-H "Authorization: Bearer <your_token>" -O
```

### Search Data

**Endpoint:** `GET /storage/search`

**Description:** Searches for files based on a query.

**Example `curl` Command:**

```sh
curl -X GET "https://localhost:3000/storage/search?userId=<user_id>&query=<search_query>" \
-H "Authorization: Bearer <your_token>"
```

### Rename a File

**Endpoint:** `POST /storage/rename`

**Description:** Renames a specified file.

**Example `curl` Command:**

```sh
curl -X POST https://localhost:3000/storage/rename \
-H "Authorization: Bearer <your_token>" \
-H "Content-Type: application/json" \
-d '{"userId": "<user_id>", "oldFilename": "<old_file_name>", "newFilename": "<new_file_name>"}'
```

### Get File Size

**Endpoint:** `GET /storage/file-size/:filename`

**Description:** Gets the size of a specified file.

**Example `curl` Command:**

```sh
curl -X GET https://localhost:3000/storage/file-size/<file_name> \
-H "Authorization: Bearer <your_token>"
```

## Development

### Directory Structure

```
DecentraCloud/Storage
├── api
│   └── storageRoutes.js
├── certs
│   ├── certificate.pem
│   └── privatekey.pem
├── data
├── encryption
├── env
├── models
├── node
│   ├── cli.py
│   └── reportStatus.js
├── node_modules
├── services
│   ├── replicationService.js
│   └── storageService.js
├── tests
├── .env
├── install.js
├── node_config.json
├── package-lock.json
├── package.json
├── requirements.txt
└── server.js
```

### Contributing

We will update you, when cotributions are allowed.

### License

This project is licensed under the MIT License.
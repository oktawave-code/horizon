# Horizon API

REST API for user management of Horizon platform. Build with Swagger.

## Getting Started

### Prerequisites

Development environment requires `NodeJS` with `npm` or `Docker` installed.

### Installing

#### Prepare configuration

Prepare `.env` file  in project root directory with custom configuration.

Example configuration:
```bash
# Server Port
APPLICATION_PORT=3000

# Url for token validation
AUTHORIZATION_URL=https://id.dev.oktawave.com/core/connect/accesstokenvalidation

# Kubernetes API url.
KUBERNETES_URL=http://127.0.0.1:8001

# Kubernetes authorization type.
# By default empty - uses kube proxy. Accepted values: X509, TokenFile.
# K8S_AUTH_TYPE=

# Path to directory containing certificates and keys. Used for X509 auth type.
# KEYSTORE=./keystore

# Use certificate verification for kubernetes API
K8S_API_STRICT_SSL=false

# Flows API group name
K8S_FLOWS_API_GROUPNAME=horizon.oktawave/v1alpha1

# Logging level
# Accepted values: error, warn, info, verbose, debug, silly 
LOGLEVEL=debug

# default 'flink-jombanager'
FLINK_API_SERVICE_NAME="flink-jobmanager"

# default 8081
FLINK_API_PORT=

# Central log service source
LOGS_SOURCE=

# Data storage url
# Connection url specification https://docs.mongodb.com/manual/reference/connection-string/
MONGODB_CONNECTION_URL='mongodb://localhost:27017/graphs'

# Horizon web editor server
# Data source for graph operations and validation
HORIZON_WEB_EDITOR_SERVER_URL=http://127.0.0.1:8000
```

#### Build and run with NodeJS

Install dependencies
```bash
npm install
```

Build and server application locally on port 8080, also watch sources for changes.

```bash
npm run start:dev
```

Open browser and go to url [http://localhost:8080/api/](http://localhost:8080/api/).

#### Build and run with Docker

Build image
```
docker build -t api .
```

Run image
```
docker run -p 8080:80 api
```

#### Other Npm commands worth mentioning
```bash
# Start development environment and watch sources
npm run start:dev

# Start dev env, watch and enable node debug
npm run start:debug

# Clean built distribution
npm run clean

# Build distribution
npm run build
```

## Running the tests

Unit tests
```
npm run test
```

Lint sources
```
npm run lint
```

## Deployment

Every `.env` variable can be overriden by env variable.
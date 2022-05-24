# Horizon web

Vuejs web application for Horizon platform managerment.

## Getting Started

### Prerequisites

Development environment requires `NodeJS` with `npm` or `Docker` installed.

### Installing

Prepare `.env` file for development environment or `.env.staging` for staging in project root directory with custom configuration:

```js
# Horizon Api Url
VUE_APP_API_URL="https://api.dev.hn.oktawave.com"

# Id server authority
VUE_APP_AUTHORITY="https://id.dev.oktawave.com/core"

# Vuejs router history mode - makes beautiful URLs
VUE_APP_HISTORY_MODE=true
```

Run with `NodeJS`

```bash
# install dependencies
npm install

# Build and serve application locally on port 8080
npm run serve
```

Run with `Docker` application for staging environment.
```bash
docker build -t web .
docker run -p 8080:80 web
```

All npm commands reference
```bash
# Serve development environment
npm run serve

# Serve staging environment
npm run serve:staging

# Build development package
npm run build

# Build staging package
npm run build:staging

# Lint code
npm run lint
```

## Running the tests

--

### Coding style tests

```
npm run lint
```

## Deployment

Default build configuration from `.env` files can be overriden in runtime environment. Edit config file `config.js` under `public` directory to override entries. Make note keys names in `conf.js` are not prefixed with `VUE_APP_` as they are in `.env` files.

Example of custom `config.js`

```js
window.appConfig = {
  // horizon api url
  API_URL: "https://horizon-api.hn.oktawave.com",
  // openid authority
  AUTHORITY: "https://id.dev.oktawave.com/core",
  // history mode
  HISTORY_MODE: true
}
```

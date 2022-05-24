# Configuration

Runtime configuration file `config.json`.

```js
window.appConfig = {
  // id server URL
  AUTHORITY: "https://id.dev.oktawave.com/core",
  // hostory mode
  HISTORY_MODE: true,
  // horizon api url
  API_URL: "https://horizon-api.hn.oktawave.com",
  // hfe jar id
  HFE_JAR_ID: "00000000-0000-0000-0000-000000000000_horizon-flow-editor.jar",
  // hfe jar entry class
  HFE_ENTRY_CLASS: "horizon.ApiServer"
}
```

# starter

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your tests
```
npm run test
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

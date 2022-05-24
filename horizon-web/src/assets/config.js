class ConfigManager {
  constructor () {
    this.config = {
      API_URL: process.env.VUE_APP_API_URL,
      HISTORY_MODE: process.env.VUE_APP_HISTORY_MODE,
      AUTHORITY: process.env.VUE_APP_AUTHORITY
    }
  }

  get (key) {
    return window.appConfig[key] || this.config[key]
  }
}

export default new ConfigManager()

class ConfigService {
  constructor () {
    this.config = {
      AUTHORITY: process.env.VUE_APP_AUTHORITY,
      HISTORY_MODE: process.env.VUE_APP_HISTORY_MODE,
      API_URL: process.env.VUE_APP_API_URL,
      HFE_JAR_ID: process.env.VUE_APP_HFE_JAR_ID,
      HFE_ENTRY_CLASS: process.env.VUE_APP_HFE_ENTRY_CLASS
    }
  }

  get (key) {
    return window.appConfig[key] || this.config[key]
  }
}

export default new ConfigService()

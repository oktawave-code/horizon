const backend = require('./mocks/MockBackend')

module.exports = {
  devServer: {
    disableHostCheck: true,
    setup: function (app, server) {
      if (process.env.NODE_ENV === 'development') {
        console.info('Development mock server enabled.')
        backend.mock(app)
      }
    }
  }
}
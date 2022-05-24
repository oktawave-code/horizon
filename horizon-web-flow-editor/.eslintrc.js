module.exports = {
  root: true,
  env: {
    node: true
  },
  'extends': [
    'plugin:vue/essential',
    '@vue/standard'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'new-cap': [
      'error',
      {
        newIsCapExceptionPattern: 'mx.*'
      }
    ]
  },
  parserOptions: {
    parser: 'babel-eslint'
  },
  globals: {
    Oidc: true,
    UIkit: true,
    mxPoint: true,
    mxRectangle: true,
    mxCellTracker: true,
    mxUtils: true,
    mxConstants: true,
    mxRubberband: true,
    mxGraphHandler: true,
    mxEditor: true,
    mxClient: true,
    mxEvent: true,
    mxConnectionHandler: true,
    mxObjectCodec: true,
    mxToolbar: true,
    mxGraph: true,
    mxPanningHandler: true
  }
}

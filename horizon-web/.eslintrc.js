// https://eslint.org/docs/user-guide/configuring

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
    'UIkit': true,
    'SwaggerClient': true,
    'Oidc': true
  }
}

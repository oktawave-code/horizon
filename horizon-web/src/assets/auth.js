import Config from '@/assets/config.js'

class AuthService {
  constructor () {
    Oidc.Log.logger = console
    Oidc.Log.level = Oidc.Log.INFO

    this.settings = {
      authority: Config.get('AUTHORITY'),
      client_id: 'HorizonWeb',
      redirect_uri: window.location.protocol + '//' + window.location.host + '/authorize.html',
      post_logout_redirect_uri: window.location.protocol + '//' + window.location.host + '/index.html',
      response_type: 'id_token token',
      scope: 'oktawave.api openid profile',
      silent_redirect_uri: window.location.protocol + '//' + window.location.host + '/silent_renew.html',
      filterProtocolClaims: false,
      automaticSilentRenew: true
    }

    const vm = this
    this.manager = new Oidc.UserManager(this.settings)
    this.manager.events.addAccessTokenExpired(() => vm.signOut())
    this.manager.events.addUserSignedOut(() => vm.signOut())
  }

  async signIn () {
    return this.manager.signinRedirect()
  }

  /**
   * Get current access token
   * @throws Error when its impossible to get user token
   * @returns token|null
   */
  async getAccessToken () {
    const user = await this.getUser()
    return user.access_token
  }

  async signOut () {
    return this.manager.signoutRedirect()
  }

  /**
   * Get user name from profile
   * @returns name field containing user name and surname
   */
  async getUserName () {
    const user = await this.getUser()
    return user.profile.name
  }

  async getUser () {
    const user = await this.manager.getUser()
    if (!user) {
      await this.signIn()
      return null
    }
    return user
  }
}

export default new AuthService()

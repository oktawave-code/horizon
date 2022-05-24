<template>
    <nav class="uk-navbar-container uk-margin" uk-navbar>
        <div class="uk-navbar-left">
          <a class="uk-navbar-item uk-logo" href="/"><img src="/logo_H.png" id="logo"></a>

          <ul class="uk-navbar-nav">
            <li>
                <a href="https://crash.ops.oktawave.com/confluence/pages/viewpage.action?pageId=52954176" target="_blank">
                    Read Docs
                </a>
            </li>
            <li>
                <a v-bind:href="apiUrl + '/api'" target="_blank">
                    API
                </a>
            </li>
          </ul>
        </div>
        <div class="uk-navbar-right">
          <div class="uk-navbar-item">
              <div>{{user}} | <a href="#" v-on:click="signOut">Sign out</a></div>
          </div>
        </div>
    </nav>
</template>

<script>
import AuthService from '@/assets/auth.js'
import Config from '@/assets/config.js'

export default {
  name: 'Header',
  data: function () {
    return {
      apiUrl: Config.get('API_URL'),
      user: ''
    }
  },
  mounted: async function () {
    this.user = await AuthService.getUserName()
  },
  methods: {
    signOut: function () {
      AuthService.signOut()
    }
  }
}
</script>

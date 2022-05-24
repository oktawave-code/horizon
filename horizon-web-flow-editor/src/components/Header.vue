<template>
  <div class="uk-width-1-1">
    <div id="header" class="uk-navbar-container uk-padding-xsmall uk-light" uk-navbar>
      <div class="uk-navbar-left">
        <a class="uk-navbar-item uk-logo" href="/">Horizon Web Editor</a>
      </div>

      <div class="uk-navbar-right">
        <div class="uk-navbar-item">
            <div>{{user}} | <a href="#" v-on:click="signOut">Sign out</a></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AuthService from '@/assets/AuthService.js'

export default {
  data () {
    return {
      user: null
    }
  },
  mounted: async function () {
    this.user = await AuthService.getUserName()
  },
  methods: {
    signOut () {
      AuthService.signOut()
    }
  }
}
</script>

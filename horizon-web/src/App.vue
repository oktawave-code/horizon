<template>
  <div>
    <panel-header class="header"></panel-header>
    <div class="uk-container">
        <router-view v-if="isInitialised"></router-view>

        <div v-if="!isInitialised" class="uk-position-center uk-text-center">
          <small>Loading...</small>
        </div>
    </div>
  </div>
</template>

<script>
import Header from '@/components/Header'
import AuthService from '@/assets/auth.js'
import Swagger from 'swagger-client'
import Config from '@/assets/config.js'

export default {
  name: 'App',
  components: {
    'panel-header': Header
  },
  data: function () {
    return {
      isInitialised: false
    }
  },
  mounted: async function () {
    const vm = this
    return new Swagger({
      url: Config.get('API_URL') + '/api-docs/swagger.json',
      requestInterceptor: async function (req) {
        req.headers['Bearer'] = await AuthService.getAccessToken()
      }
    }).then(function (client) {
      window.client = client
      window.client.spec.schemes = ['https']
      vm.isInitialised = true
    })
  }
}
</script>

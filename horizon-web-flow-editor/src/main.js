import Vue from 'vue'
import App from './App.vue'
import router from './router'
import AuthService from '@/assets/AuthService.js'

Vue.config.productionTip = false

/**
 * IMPORTANT: Router configuration must be set before application is mounted
 * to enable guard on page refresh.
 */
router.beforeEach(async function (to, from, next) {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  if (!requiresAuth) {
    next()
    return
  }

  try {
    const user = await AuthService.getUser()
    if (!user) {
      await AuthService.signIn()
    } else {
      next()
    }
  } catch (error) {
    next({ name: 'error', params: { message: 'Failed to authorize user.' } })
  }
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

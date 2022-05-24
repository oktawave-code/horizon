import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/views/Home.vue'
import GraphEditor from '@/views/Editor.vue'
import Error from '@/views/Error.vue'
import NotFound from '@/views/NotFound.vue'
import Config from '@/assets/ConfigService.js'

Vue.use(Router)

export default new Router({
  /**
   * FIXME removes hash from path but causes login redirect to index.html and renders empty page.
   * Solution: https://router.vuejs.org/guide/essentials/history-mode.html#example-server-configurations
   */
  mode: Config.get('HISTORY_MODE') ? 'history' : 'hash',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/error',
      name: 'error',
      component: Error,
      props: 'message'
    },
    {
      path: '/',
      name: 'home',
      meta: {
        requiresAuth: true
      },
      component: Home
    },
    {
      path: '/edit/:id',
      name: 'edit',
      meta: {
        requiresAuth: true
      },
      props: true,
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: GraphEditor
    },
    /**
     * IMPORTANT. Catch all route - simulates 404 HTTP(Not Found) error.
     * Must be the last route on the list to work correctly.
     */
    {
      path: '*',
      component: NotFound
    }
  ]
})

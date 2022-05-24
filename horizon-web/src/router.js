import Vue from 'vue'
import Router from 'vue-router'
import FlowsList from '@/components/FlowsList'
import FlowDetails from '@/components/FlowDetails'
import FlowCreate from '@/components/FlowCreate'
import FlowEdit from '@/components/FlowEdit'
import ProcessorLogs from '@/components/ProcessorLogs'
import Config from '@/assets/config.js'
// const NotFound = { template: '<p>Page not found</p>' }

Vue.use(Router)

export default new Router({
  mode: Config.get('HISTORY_MODE') ? 'history' : 'hash',
  routes: [
    {
      name: 'list',
      path: '/',
      meta: {
        requiresAuth: true
      },
      component: FlowsList
    },
    {
      name: 'details',
      path: '/details/:name',
      meta: {
        requiresAuth: true
      },
      component: FlowDetails,
      props: true
    },
    {
      name: 'create',
      path: '/create',
      meta: {
        requiresAuth: true
      },
      component: FlowCreate
    },
    {
      name: 'edit',
      path: '/edit/:name',
      meta: {
        requiresAuth: true
      },
      component: FlowEdit,
      props: true
    },
    {
      name: 'processorLogs',
      path: '/flow/:flow/processor/:processor/logs',
      meta: {
        requiresAuth: true
      },
      component: ProcessorLogs,
      props: true
    }
  ]
})

<template>
  <div class="uk-margin-bottom">
    <div class="uk-margin">
        <router-link tag="button" :to="{name: 'list'}" class="uk-button uk-button-default">&larr; Back to list</router-link>
    </div>

    <div class="uk-alert-danger" uk-alert v-if="!!error">
        <a class="uk-alert-close" uk-close></a>
        <p><span uk-icon="warning"></span> {{ error }}</p>
    </div>

    <flow-form
        v-bind:error="validationErrors"
        v-on:submit="createProcessor"
        v-on:cancel="cancel"></flow-form>
  </div>
</template>

<script>
import FlowForm from '@/components/FlowForm'

export default {
  components: {
    'flow-form': FlowForm
  },
  data: function () {
    return {
      error: null,
      validationErrors: []
    }
  },
  methods: {
    createProcessor: function ({ name, ...body }) {
      const that = this
      this.error = null
      this.validationErrors = []
      window.client.apis.flow.post_flow__name_(
        {
          name,
          FlowDto: body
        })
        .then(function (data) {
          that.$router.push({ name: 'list' })
        })
        .catch(function (error) {
          // FIXME not always message is present
          if (!error.response.body.message) {
            UIkit.notification({
              message: `Request failed with unknown reason. Server responded with status ${error.status}`,
              status: 'danger'
            })
            return
          }

          if (Array.isArray(error.response.body.message)) {
            that.validationErrors = error.response.body.message
          } else {
            that.error = error.response.body.message
          }

          UIkit.notification({
            message: 'Your form contains errors.',
            status: 'danger'
          })
        })
    },
    cancel: function () {
      this.$router.push({ name: 'list' })
    }
  }
}
</script>

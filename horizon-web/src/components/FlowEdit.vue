<template>
    <div class="uk-margin-bottom">
        <div class="uk-margin">
            <router-link tag="button" :to="{name: 'list'}" class="uk-button uk-button-default"><span uk-icon="arrow-left"></span> Back to list</router-link>
        </div>

        <div class="uk-alert-danger" uk-alert v-if="!!error">
            <a class="uk-alert-close" uk-close></a>
            <p><span uk-icon="warning"></span> {{ error }}</p>
        </div>

        <div>
        <flow-form
            v-if="!!flow"
            v-bind:error="error"
            v-bind:name="flow.name"
            v-bind:processors="flow.processors"
            v-bind:flink="flow.flink"
            v-bind:collectorRouting="flow.collectorRouting"
            v-bind:collectorThroughputLimit="flow.collectorThroughputLimit"
            v-bind:collectorMinThroughput="flow.collectorMinThroughput"
            v-bind:collectorMaxThroughput="flow.collectorMaxThroughput"
            v-bind:collectorRetention="flow.collectorRetention"
            v-bind:emitter="flow.emitter"
            v-bind:emitterPlan="flow.emitterPlan"
            v-bind:emitterRouting="flow.emitterRouting"
            v-on:submit="createProcessor"
            v-on:cancel="cancel"></flow-form>
        </div>
    </div>
</template>

<script>
import FlowForm from '@/components/FlowForm'

export default {
  components: {
    'flow-form': FlowForm
  },
  props: ['name'],
  data: function () {
    return {
      error: null,
      validationErrors: [],
      flow: null
    }
  },
  created: function () {
    this.getFlow()
  },
  methods: {
    getFlow: function () {
      const that = this
      window.client.apis.flow.get_flow__name_({ name: that.$props.name })
        .then(function (data) {
          that.flow = data.body
        })
    },
    createProcessor: function ({ name, ...body }) {
      const that = this
      this.error = null
      this.validationErrors = []
      window.client.apis.flow.put_flow__name_({
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

<template>
    <div>
      <div>
        <div class="uk-clearfix">
            <div class="uk-float-left">
                <router-link tag="button" :to="{name: 'details', params: {name: flow}}" class="uk-button uk-button-default"><span uk-icon="arrow-left"></span> Back to details</router-link>
            </div>
        </div>
      </div>

      <div class="uk-card uk-card-default uk-margin">
        <div class="uk-card-header">
          <h6 class="uk-card-title uk-margin-remove-bottom">Logs of processor {{processor}}(Flow: {{flow}})</h6>
        </div>

        <div class="uk-fieldset uk-card-body">
          <div class="uk-alert-primary" uk-alert>
              <a class="uk-alert-close" uk-close></a>
              <p>Logs are refreshed automatically.</p>
          </div>
          <pre style="height: 500px; overflow:scroll">{{logs}}</pre>
        </div>
      </div>
    </div>
</template>

<script>
export default {
  name: 'ProcessorLogs',
  props: {
    flow: String,
    type: String,
    processor: String
  },
  created: function () {
    this.getLogs()
    this.logsRefresher = setInterval(this.getLogs, 10000)
  },
  destroyed: function () {
    clearInterval(this.logsRefresher)
  },
  methods: {
    getLogs: function () {
      const that = this
      if (this.type === 'flink') {
        window.client.apis.processor.get_processor__flow__logs_flink({ flow: this.$props.flow })
          .then(function (data) {
            that.logs = data.data
          })
      } else {
        window.client.apis.processor.get_processor__flow__logs_processor__processorName_({ flow: this.$props.flow, processorName: this.$props.processor })
          .then(function (data) {
            that.logs = data.data
          })
      }
    }
  },
  data: function () {
    return {
      logs: '',
      logsRefresher: null
    }
  }
}
</script>

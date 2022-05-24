<template>
    <span>
        <span v-if="flowStatus === statuses.ready" class="uk-margin-small-right" uk-icon="check"></span>
        <span v-if="flowStatus === statuses.initializing" class="uk-margin-small-right" uk-icon="future"></span>
        <span v-if="flowStatus === statuses.failed" class="uk-margin-small-right" uk-icon="close"></span>
    </span>
</template>

<script>
export default {
  props: {
    status: Object
  },
  data: function () {
    return {
      statuses: {
        ready: 'ready',
        initializing: 'initializing',
        failed: 'failed'
      }
    }
  },
  computed: {
    flowStatus: function () {
      if (this.status.status && this.status.ready === this.status.expected) {
        return this.statuses.ready
      } else if (this.status.failed && !this.status.initializing) {
        return this.statuses.failed
      } else {
        return this.statuses.initializing
      }
    }
  }
}
</script>

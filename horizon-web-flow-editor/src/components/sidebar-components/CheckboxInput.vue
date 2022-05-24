<template>
  <div class="uk-margin uk-grid-small uk-child-width-auto uk-grid">
      <label class="uk-form-label" for="form-stacked-select">{{model.getLabel()}}</label>
      <div class="uk-text-middle" v-if="model.getDescription()">{{model.getDescription()}}</div>

      <label v-for="(option, index) in model.getOptions()" :key="index">
          <input class="uk-checkbox" v-bind:value="option.internalName" type="checkbox" v-model="value"> {{option.name}}
      </label>

  </div>
</template>

<script>
export default {
  props: {
    model: Object
  },
  template: `
  `,
  data: function () {
    return {
      // select value on init
      value: this.model.getValue()
    }
  },
  methods: {
    saveValue: function () {
      const value = this.value
      this.model.setValue(value)
    }
  }
}
</script>

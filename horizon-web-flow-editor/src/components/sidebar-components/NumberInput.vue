<template>
  <div class="uk-margin">
    <label class="uk-form-label" for="form-stacked-text">{{model.getLabel()}}</label>
    <div class="uk-text-middle" v-if="model.getDescription()">{{model.getDescription()}}</div>
    <div class="uk-form-controls">
      <input v-model="value" class="uk-input" type="number" v-bind:min="model.getMinValue()" v-bind:max="model.getMaxValue()" v-bind:step="model.getStep()" v-bind:name="model.getFieldName()" v-bind:required="model.isRequired()">
    </div>
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

<template>
  <div class="uk-margin">
    <label class="uk-form-label" for="form-stacked-text">{{model.getLabel()}}</label>
    <div class="uk-text-middle" v-if="model.getDescription()">{{model.getDescription()}}</div>
    <div class="uk-form-controls">
      <textarea v-model="value" v-if="model.isMultiline()" class="uk-textarea" rows="5" v-bind:name="model.getFieldName()" v-bind:required="model.isRequired()"></textarea>
      <input v-model="value" v-if="!model.isMultiline()" class="uk-input" type="text" v-bind:name="model.getFieldName()" v-bind:required="model.isRequired()">
    </div>
  </div>
</template>

<script>
export default {
  props: {
    model: Object
  },
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

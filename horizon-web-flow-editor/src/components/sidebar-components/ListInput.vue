<template>
  <div class="uk-margin">
    <label class="uk-form-label" for="form-stacked-select">{{model.getLabel()}}</label>
    <div class="uk-text-middle" v-if="model.getDescription()">{{model.getDescription()}}</div>
    <div class="uk-form-controls">
      <select class="uk-select" id="form-stacked-select" v-model="value">
        <option v-for="(option, index) in model.getOptions()" v-bind:value="option.internalName" :key="index">
          {{ option.name }}
        </option>
      </select>
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

export default Vue.component('list-input', {
});

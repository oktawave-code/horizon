<template>
  <div>
      <div v-if="!name">Nothing selected.</div>
      <form v-if="name" v-on:submit.prevent="onSubmit">
          <fieldset class="uk-fieldset">
              <legend class="uk-legend">{{name}}</legend>
              <div v-for="(property, index) in properties" :key="cell.getId() + index">
                  <text-input v-if="isTextStaticProperty(property)" v-bind:model="property"></text-input>
                  <number-input v-if="isNumberStaticProperty(property)" v-bind:model="property"></number-input>
                  <list-input v-if="isListStaticProperty(property)" v-bind:model="property"></list-input>
                  <checkbox-input v-if="isCheckboxStaticProperty(property)" v-bind:model="property"></checkbox-input>
              </div>
              <button class="uk-button uk-button-default">Submit</button>
          </fieldset>
      </form>
  </div>
</template>

<script>

import TextInput from '@/components/sidebar-components/TextInput.vue'
import NumberInput from '@/components/sidebar-components/NumberInput.vue'
import ListInput from '@/components/sidebar-components/ListInput.vue'
import CheckboxInput from '@/components/sidebar-components/CheckboxInput.vue'
import { StaticPropertyBase, TextStaticProperty, NumberStaticProperty, ListStaticProperty, CheckboxStaticProperty } from '@/engine/model/static-property.js'

export default {
  components: {
    TextInput,
    NumberInput,
    ListInput,
    CheckboxInput
  },
  props: {
    cell: Object
  },
  computed: {
    name: function () {
      return this.cell ? this.cell.getValue().getName() : ''
    },
    properties: function () {
      return this.cell ? this.cell.getValue().getStaticProperties() : []
    }
  },
  methods: {
    isTextStaticProperty: function (property) {
      return property instanceof TextStaticProperty
    },
    isNumberStaticProperty: function (property) {
      return property instanceof NumberStaticProperty
    },
    isListStaticProperty: function (property) {
      return property instanceof ListStaticProperty
    },
    isCheckboxStaticProperty: function (property) {
      return property instanceof CheckboxStaticProperty
    },
    onSubmit: function () {
      this.$children.forEach(function (component) {
        if (!component.model) {
          return
        }

        if (!(component.model instanceof StaticPropertyBase)) {
          return
        }

        component.saveValue()
      })
    }
  }
}
</script>

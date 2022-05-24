<template>
    <div>
        <router-link tag="button" :to="{name: 'create'}" class="uk-button uk-button-primary">Create flow</router-link>

        <h4>Flows list</h4>
        <table class="uk-table uk-table-divider">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Processor type</th>
                    <th>Status</th>
                    <th>Creation date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="flow in flows" :key="flow.name">
                    <td><router-link :to="{name: 'details', params: {name: flow.name}}">{{flow.name}}</router-link></td>
                    <td>{{ Array.isArray(flow.processors) && !!flow.processors.length ? 'Custom images' : 'Flink'}}</td>
                    <td>
                        <flow-status :status="flow.status"></flow-status>
                    </td>
                    <td>{{ new Date(flow.creationDate).toLocaleString() }}</td>
                    <td>
                        <router-link :to="{name: 'edit', params: {name: flow.name}}">Edit</router-link>,
                        <a href="#" v-on:click="deleteFlow(flow.name)">Delete</a>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import FlowStatus from '@/components/FlowStatus'

export default {
  components: {
    'flow-status': FlowStatus
  },
  data: function () {
    return {
      flows: []
    }
  },
  created: function () {
    this.getFlows()
  },
  methods: {
    getFlows: function () {
      const that = this
      window.client.apis.flow.get_flow({})
        .then(function (data) {
          that.flows = data.body.sort((f1, f2) => new Date(f2.creationDate) - new Date(f1.creationDate))
        })
    },
    deleteFlow: function (name) {
      const that = this
      window.client.apis.flow.delete_flow__name_({ name })
        .then(function (data) {
          that.getFlows()
        })
    }
  }
}
</script>

<template>
  <div class="uk-container uk-margin-top">
    <button class="uk-button uk-button-primary" uk-toggle="target: #add-new-graph" type="button">+ Create new graph</button>

    <h4>Graphs list</h4>
    <table class="uk-table uk-table-divider">
        <thead>
            <tr>
                <th>Name</th>
                <th>Creation date</th>
                <th>Last edit</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="graph in graphs" :key="graph.id">
                <td><router-link :to="{name: 'edit', params: { id: graph.id }}">{{ graph.name }}</router-link></td>
                <td>{{ graph.createdAt }}</td>
                <td>{{ graph.updatedAt }}</td>
                <td>Run | <button class="uk-button uk-button-link" type="button" v-on:click="confirmDeletion(graph)">Delete</button></td>
            </tr>
        </tbody>
    </table>

    <div id="add-new-graph" uk-modal>
      <div class="uk-modal-dialog uk-modal-body">
          <button class="uk-modal-close-default" type="button" uk-close></button>
          <h4 class="uk-modal-title">Create new graph</h4>

          <form class="uk-form-stacked" v-on:submit.prevent="submitNewGraph">

            <div class="uk-margin">
                <label class="uk-form-label" for="form-stacked-text">Name</label>
                <small>Only aplhanumeric characters allowed.</small>
                <div class="uk-form-controls">
                    <input class="uk-input" id="form-stacked-text" type="text" required maxlength="30" pattern="[A-Za-z0-9]+" v-model="graphName">
                </div>
            </div>

            <p class="uk-text-right">
              <button class="uk-button uk-button-primary uk-margin-right" type="submit">Submit</button>
              <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
            </p>

        </form>
      </div>
    </div>

    <div id="graph-removal-confirmation" uk-modal>
      <div class="uk-modal-dialog uk-modal-body">
          <h2 class="uk-modal-title">Remove graph {{ graphToRemove.name }}?</h2>
          <p>Your graph will be permanently deleted.</p>
          <p class="uk-text-right">
              <button class="uk-button uk-button-primary uk-margin-right" type="button" v-on:click="deleteGraph(graphToRemove)">Delete</button>
              <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
          </p>
      </div>
    </div>

  </div>
</template>

<script>
import GraphsService from '@/engine/GraphsService.js'

export default {
  name: 'GraphsList',
  data: function () {
    return {
      graphs: [],
      graphName: null,
      graphToRemove: {}
    }
  },
  created () {
    this.getGraphs()
  },
  methods: {
    getGraphs: async function () {
      try {
        this.graphs = await GraphsService.list()
      } catch (error) {
        UIkit.notification('Failed to get list of graphs.', { status: 'danger' })
      }
    },
    submitNewGraph: async function () {
      try {
        await GraphsService.create(this.graphName)
        await this.getGraphs()
        this.hideModal()
      } catch (error) {
        UIkit.notification('Unexpected error occured. Failed to create graph.', { status: 'danger' })
      }
    },
    hideModal () {
      UIkit.modal('#add-new-graph').hide()
      this.graphName = null
    },
    confirmDeletion: async function (graph) {
      this.graphToRemove = graph
      UIkit.modal('#graph-removal-confirmation').show()
    },
    deleteGraph: async function (graph) {
      try {
        await GraphsService.remove(graph)
        UIkit.modal('#graph-removal-confirmation').hide()
        this.graphToRemove = {}
        await this.getGraphs()
      } catch (error) {
        UIkit.notification('Unexpected error occured. Failed to delete graph.', { status: 'danger' })
      }
    }
  }
}
</script>

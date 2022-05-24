<template>
  <div class="uk-light editor-container">
      <div class="uk-width-1-1">
        <div id="subnav" class="uk-padding-small">
          <ul class="uk-subnav uk-subnav-divider uk-margin-remove">
            <li class="uk-active"><router-link :to="{ name: 'home' }"><span uk-icon="arrow-left"></span> Back to list</router-link></li>
            <li class="uk-active"><a v-on:click.prevent="save">Save</a></li>
            <li class="uk-active"><a v-on:click.prevent="saveAndRun">Save &amp; Run</a></li>
            <li><a href="">Stop</a></li>
          </ul>
        </div>
      </div>

      <div uk-grid uk-height-viewport="expand: true" class="uk-grid-collapse">
        <div class="uk-width-medium@m uk-overflow-auto">
          <div class="uk-height-max-large uk-margin-top uk-margin-left uk-margin-right">
            <h4>Operations</h4>
            <div id="toolbar"></div>
          </div>
        </div>

        <div class="uk-width-expand graphContainerWrapper">
          <div id="graphContainer"></div>
        </div>

        <div class="uk-width-medium@m uk-overflow-auto">
          <div class="uk-height-max-large uk-margin-top uk-margin-left uk-margin-right">
            <h4>Operation configuration</h4>
            <editor-sidebar class="uk-margin-bottom" v-bind:cell="selectedCell"></editor-sidebar>
          </div>
        </div>

        <div id="select-flow" uk-modal>
          <div class="uk-modal-dialog uk-modal-body">
              <h2 class="uk-modal-title">Select flow to deploy graph</h2>
              <form class="uk-form-stacked">
                <div class="uk-margin">
                    <label class="uk-form-label" for="form-stacked-select">Select flow</label>
                    <div class="uk-form-controls">
                        <select class="uk-select" id="form-stacked-select" v-model="selectedFlow">
                            <option disabled value="">Please select one</option>
                            <option v-for="flow in flowsList" v-bind:value="flow.name" :key="flow.name">
                              {{ flow.name }}
                            </option>
                        </select>
                    </div>
                </div>
              </form>
              <p class="uk-text-right">
                  <button class="uk-button uk-button-default uk-modal-close uk-margin-right" type="button">Cancel</button>
                  <button class="uk-button uk-button-primary" type="button" v-on:click="acceptRunGraphFlow(selectedFlow)">Run</button>
              </p>
          </div>
      </div>
    </div>
  </div>
</template>

<script>

import { initEditor, destroyEditor } from '@/graph/graph.js'
import { initToolbar } from '@/graph/toolbar.js'
import { enableInfiniteView } from '@/graph/graphInfiniteView.js'
import { setupPanning } from '@/graph/panning.js'
import { initConnectionHandler } from '@/graph/connectionHandler.js'
import { Operation } from '@/engine/model/OperationModel.js'
import JsonCodec from '@/engine/serializer.js'
import EditorSidebar from '@/components/EditorSidebar.vue'
import GraphsService from '@/engine/GraphsService.js'
import FlowsService from '@/engine/FlowsService.js'
import OperationsService from '@/engine/OperationsService.js'

let lastSavedModel = ''

export default {
  name: 'GraphEditor',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  components: {
    EditorSidebar
  },
  data: function () {
    return {
      editor: null,
      graph: {},
      selectedCell: null,
      flowsList: [],
      selectedFlow: null
    }
  },
  beforeRouteEnter: async function (to, from, next) {
    try {
      const graphModel = await GraphsService.get(to.params.id)
      const operations = await OperationsService.get()
      next(vm => {
        try {
          vm.initializeEditor(graphModel.graph, operations)
        } catch (error) {
          next({ name: 'error', params: { message: 'Failed to process graph configuration.' } })
        }
      })
    } catch (error) {
      next({ name: 'error', params: { message: 'Failed to load resources.' } })
    }
  },
  beforeRouteLeave: function (to, from, next) {
    const model = this.serialize(this.graph)
    if (lastSavedModel !== JSON.stringify(model)) {
      UIkit.modal.confirm('You have unsaved changes. Do yout really want to discard current work and leave?').then(function () {
        next()
      }, function () {
        next(false)
      })
    } else {
      next()
    }
  },
  beforeDestroy: function () {
    // TODO - check if all resources are destroyed
    if (this.editor) {
      destroyEditor(this.editor)
    }
  },
  methods: {
    initializeEditor: async function (model, operations) {
      const vm = this
      // cache current model
      lastSavedModel = JSON.stringify(model)
      // create editor
      const container = document.getElementById('graphContainer')
      vm.editor = initEditor(container)
      vm.graph = vm.editor.graph
      vm.deserialize(model)

      // FIXME operations should be resolved in router and passed as param
      initToolbar(vm.graph, operations)
      enableInfiniteView(vm.graph)
      setupPanning(vm.graph)
      initConnectionHandler(vm.graph)

      vm.graph.getSelectionModel().addListener(mxEvent.CHANGE, function (sender, evt) {
        const cell = vm.graph.getSelectionCell()
        if (!cell) {
          vm.selectedCell = null
          return
        }

        if (cell.getValue() instanceof Operation) {
          vm.selectedCell = cell
        }
      })

      // FIXME - enaling this scroll makes impossible to use mouse wheel in any other container on page
      // // Adds mouse wheel handling for zoom
      // mxEvent.addMouseWheelListener(function(evt, up)
      // {
      //     if (up) {
      //         vm.graph.zoomIn();
      //     } else {
      //         vm.graph.zoomOut();
      //     }

      //     // FIXME disables scrolling in other divs!
      //     mxEvent.consume(evt);
      // });,
    },
    serialize: function () {
      const codec = new JsonCodec()
      const jsonModel = codec.decode(this.graph.getModel())
      return jsonModel
    },
    deserialize: function (dataModel) {
      const _vertices = []
      const vm = this

      const parent = vm.graph.getDefaultParent()
      vm.graph.getModel().beginUpdate()

      try {
        dataModel.map(function (node) {
          if (!node.edge) {
            const value = new Operation(node.value)
            _vertices[node.id] = vm.graph.insertVertex(parent, node.id, value, node.geometry.x, node.geometry.y, node.geometry.width, node.geometry.height)
          } else if (node.edge) {
            vm.graph.insertEdge(parent, node.id, node.value, _vertices[node.source], _vertices[node.target])
          }
        })
      } finally {
        vm.graph.getModel().endUpdate()
      }
    },
    // load: function () {
    //   this.graph.getModel().clear()
    // },
    async save () {
      try {
        const model = this.serialize()
        await GraphsService.save(this.$props.id, model)
        lastSavedModel = JSON.stringify(model)
        UIkit.notification('Graph saved.', { status: 'success' })
        return true
      } catch (error) {
        UIkit.notification('Failed to save graph.', { status: 'danger' })
        return false
      }
    },
    async saveAndRun () {
      const saved = await this.save()
      if (!saved) {
        return
      }

      try {
        this.flowsList = await FlowsService.listFlinkFlows()
        UIkit.modal('#select-flow').show()
      } catch (error) {
        UIkit.notification('Failed to get flows.', { status: 'danger' })
      }
    },
    async acceptRunGraphFlow (flow) {
      try {
        await FlowsService.runGraph(flow, this.$props.id)
        UIkit.notification('Graph is running.', { status: 'success' })
      } catch (error) {
        UIkit.notification('Failed to run graph.', { status: 'danger' })
      }
    }
  }
}

</script>

<style>
.editor-container {
  background-color: #222;
}
</style>

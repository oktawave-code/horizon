import ApiService from './ApiService.js'
import GraphDefinitionModel from './model/GraphDefinitionModel.js'

class GraphsService {
  async list () {
    const response = await ApiService.get('/graph')
    const graphs = response.data
    return graphs.map(definition => new GraphDefinitionModel(definition))
  }

  /**
   * Get graph model
   */
  async get (id) {
    const response = await ApiService.get(`/graph/${id}`)
    return response.data
  }

  /**
   * Creates new graph
   * @param {name} Name of new graph
   */
  async create (name) {
    const response = await ApiService.post('/graph', { name })
    return response.data
  }

  async remove (graph) {
    const response = await ApiService.delete(`/graph/${graph.id}`)
    return response.data
  }

  async save (id, graphModel) {
    const response = await ApiService.patch(`/graph/${id}`, { graph: graphModel })
    return response.data
  }
}

export default new GraphsService()

import ApiService from './ApiService.js'
import Config from '@/assets/ConfigService.js'

class FlowsService {
  constructor () {
    this.HFE_JAR_ID = Config.get('HFE_JAR_ID')
    this.HFE_ENTRY_CLASS = Config.get('HFE_ENTRY_CLASS')
  }

  async listFlinkFlows () {
    const response = await ApiService.get('/flow')
    const flows = response.data
    return flows.filter(flow => flow.flink)
  }

  async runGraph (flow, graphId) {
    await ApiService.post(`/flink/${flow}/runJar/${this.HFE_JAR_ID}`, {
      entryClass: this.HFE_ENTRY_CLASS,
      // TODO CONFIG THIS
      parallelism: 1,
      programArgs: `-db ${graphId}`
      // "savepointPath": "string",
      // "allowNonRestoredState": true
    })
  }
}

export default new FlowsService()

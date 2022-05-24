import ApiService from './ApiService.js'
import { Operation } from './model/OperationModel.js'

class OperationsService {
  async get () {
    const response = await ApiService.get('/operations')
    const operations = response.data
    return operations.map(operation => new Operation(operation))
  }
}

export default new OperationsService()

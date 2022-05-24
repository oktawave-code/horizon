import axios from 'axios'
import AuthService from '@/assets/AuthService.js'
import Config from '@/assets/ConfigService.js'

class ApiService {
  constructor (baseURL) {
    this.client = axios.create({
      baseURL,
      headers: {
        Authorization: 'Bearer asdf'
      }
    })

    this.client.interceptors.request.use(async function (config) {
      const token = await AuthService.getAccessToken()
      config.headers['bearer'] = token
      return config
    })

    const interfaceMethods = [
      'get',
      'delete',
      'post',
      'put',
      'patch'
    ]

    const vm = this
    interfaceMethods.forEach(method => {
      vm[method] = async function (...args) {
        return vm.client[method].apply(vm, args)
      }
    })
  }
}

export default new ApiService(Config.get('API_URL'))

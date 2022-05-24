import { buildStaticProperty } from './static-property.js'

export class Operation {
  constructor (model) {
    Object.assign(this, model)
    this.staticProperties = (this.staticProperties || []).map(prop => buildStaticProperty(prop))
  }

  getCategory () {
    return this.category
  }

  getIcon () {
    return this.iconUri
  }

  getName () {
    return this.name
  }

  getDescription () {
    return this.description
  }

  getRequiredStreams () {
    return this.requiredStreams
  }

  isSink () {
    return this.noOutputs
  }

  getStaticProperties () {
    return this.staticProperties
  }
}

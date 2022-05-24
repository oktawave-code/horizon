export default class GraphDefinitionModel {
  constructor (model) {
    Object.assign(this, model)
  }

  getId () {
    return this.id
  }

  getName () {
    return this.name
  }

  getCreationDate () {
    return this.created
  }

  getLastEditDate () {
    return this.edited
  }

  getGraph () {
    return this.graph
  }
}

export default class JsonCodec extends mxObjectCodec {
  constructor () {
    super((value) => {})
  }

  encode (value) {
    const xmlDoc = mxUtils.createXmlDocument()
    const newObject = xmlDoc.createElement('Object')
    for (let prop in value) {
      newObject.setAttribute(prop, value[prop])
    }
    return newObject
  }

  decode (model) {
    //
    return Object.keys(model.cells).map(iCell => {
      const currentCell = model.getCell(iCell)

      // some unknown internal objects
      if (typeof currentCell.getValue() === 'undefined') {
        return null
      }

      // serialize cell
      if (!currentCell.isEdge()) {
        return new Cell(currentCell)
      }

      // serialize edge
      if (currentCell.isEdge()) {
        return new Edge(currentCell)
      }

      return null
    }
    ).filter((item) => (item !== null))
  }
}

class Cell {
  constructor (cell) {
    this.value = cell.value
    this.id = cell.id
    this.geometry = cell.geometry ? new Geometry(cell.geometry) : null

    // this.vertex = cell.vertex;
    // this.connectable = cell.connectable;
    // this.parent = (cell.parent || {}).id;
    // this.source = (cell.source || {}).id;
    // this.target = (cell.target || {}).id;
    // this.edges = (cell.edges || []).map(edge => new Edge(edge));
    // this.mxObjectId = cell.mxObjectId;
  }
}

class Edge {
  constructor (edge) {
    this.value = edge.value
    this.edge = edge.edge
    this.source = (edge.source || {}).id
    this.target = (edge.target || {}).id

    // this.geometry = edge.geometry;
    // this.id = edge.id;
    // this.parent = (edge.parent || {}).id;
    // this.mxObjectId = edge.mxObjectId;
  }
}

class Geometry {
  constructor (geometry) {
    this.x = geometry.x
    this.y = geometry.y
    this.width = geometry.width
    this.height = geometry.height

    // this.relative = geometry.relative;
    // this.TRANSLATE_CONTROL_POINTS = geometry.TRANSLATE_CONTROL_POINTS
    // this.alternateBounds = geometry.alternateBounds;
    // this.sourcePoint = geometry.sourcePoint;
    // this.targetPoint = geometry.targetPoint;
    // this.points = geometry.points;
    // this.offset = geometry.offset;
  }
}

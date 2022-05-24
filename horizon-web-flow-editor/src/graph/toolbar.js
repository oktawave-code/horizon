import { Operation } from '@/engine/model/OperationModel.js'

export function initToolbar (graph, operations) {
  // Creates new toolbar without event processing
  const toolbarPanel = document.getElementById('toolbar')
  const toolbar = new mxToolbar(toolbarPanel)
  toolbar.enabled = false

  // Render name only for operation cells
  mxGraph.prototype.convertValueToString = function (cell) {
    const value = cell.getValue()
    // if cell holds operation definition, show name from model
    return value instanceof Operation ? value.getName() : ''
  }

  function addToolbarItem (graph, toolbar, operation, cellWidth, cellHeight) {
    // Function that is executed when the image is dropped on
    // the graph. The cell argument points to the cell under
    // the mousepointer if there is one.
    const funct = function (graph, evt, cell, x, y) {
      const parent = graph.getDefaultParent()
      const model = graph.getModel()
      let vertex = null

      model.beginUpdate()
      try {
        // NOTE: For non-HTML labels the image must be displayed via the style
        // rather than the label markup, so use 'image=' + image for the style.
        // as follows: v1 = graph.insertVertex(parent, null, label,
        // pt.x, pt.y, 120, 120, 'image=' + image);
        vertex = graph.insertVertex(parent, null, operation.getName(), x, y, cellWidth, cellHeight)

        // set Operation object reference
        vertex.setValue(new Operation(operation))
      } finally {
        model.endUpdate()
      }

      graph.setSelectionCell(vertex)
    }

    const operationItem = document.createElement('div')
    operationItem.className += 'uk-card uk-card-primary uk-card-body uk-card-small uk-margin disable-select'

    const operationName = document.createElement('span')
    operationName.textContent = operation.getName()

    const operationDescription = document.createElement('span')
    operationDescription.setAttribute('uk-icon', 'icon: question; ratio: 0.8')
    operationDescription.setAttribute('uk-tooltip', operation.getDescription())
    operationDescription.className += 'uk-margin-small-left'

    operationItem.appendChild(operationName)
    operationItem.appendChild(operationDescription)

    toolbarPanel.appendChild(operationItem)

    // Creates the image which is used as the drag icon (preview)
    const dragElt = document.createElement('div')
    dragElt.style.border = 'dashed black 1px'
    dragElt.style.width = `${cellWidth}px`
    dragElt.style.height = `${cellHeight}px`

    mxUtils.makeDraggable(operationItem, graph, funct, dragElt)
  }

  // group operations by category
  const groupedOperations = operations.reduce(function (acc, operation) {
    (acc[operation.getCategory()] = acc[operation.getCategory()] || []).push(operation)
    return acc
  }, {})

  Object.keys(groupedOperations)
  // sort categories alphabetically
    .sort()
    .forEach(function (category) {
      // add category section
      const section = document.createElement('h5')
      section.textContent = category
      toolbarPanel.appendChild(section)

      groupedOperations[category].forEach(function (operation) {
        // insert operations into section
        addToolbarItem(graph, toolbar, operation, 100, 40)
      })
    })

  return toolbar
}

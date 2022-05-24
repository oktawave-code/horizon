export function initEditor (container) {
  // Checks if the browser is supported
  if (!mxClient.isBrowserSupported()) {
    // Displays an error message if the browser is not supported.
    mxUtils.error('Browser is not supported!', 200, false)
  }

  const editor = new mxEditor()
  const graph = editor.graph
  // const model = graph.getModel()

  // Sets the graph container and configures the editor
  editor.setGraphContainer(container)

  // Enables guides
  // Example: https://jgraph.github.io/mxgraph/javascript/examples/guides.html
  mxGraphHandler.prototype.guidesEnabled = true

  // Enables rubberband selection
  /* eslint-disable no-new */
  new mxRubberband(graph)

  // disables unconnected edges
  graph.allowDanglingEdges = false

  // Use nice looking rounded edges and clean path
  const style = graph.getStylesheet().getDefaultEdgeStyle()
  style[mxConstants.STYLE_STROKEWIDTH] = '2'

  // configure keys for editor
  const config = mxUtils.load('/keyhandler-commons.xml').getDocumentElement()
  editor.configure(config)

  // Disable cell value editing
  graph.cellsEditable = false

  // highlight cell on mouseover
  /* eslint-disable no-new */
  new mxCellTracker(graph, '#00FF00')

  graph.dropEnabled = true

  // Enables new connections in the graph
  graph.setConnectable(true)

  // Disable Cell resizing
  graph.setCellsResizable(false)

  // Removes the folding icon and disables any folding
  graph.isCellFoldable = function (cell) {
    return false
  }

  return editor
}

export function destroyEditor (editor) {
  editor.destroy()
}

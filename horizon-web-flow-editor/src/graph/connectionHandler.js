import { Operation } from '@/engine/model/OperationModel.js'

export function initConnectionHandler (graph) {
  // Enables connect icons to appear on top of HTML
  mxConnectionHandler.prototype.moveIconFront = true

  // Disables new connections via "hotspot" (point in the middle of cell)
  graph.connectionHandler.marker.isEnabled = function () {
    return this.graph.connectionHandler.first != null
  }

  // allows connection ending only if there are unused input slots
  mxConnectionHandler.prototype.isValidTarget = function (cell) {
    if (!(cell.getValue() instanceof Operation)) {
      return false
    }
    // get number of edges connected to this cell
    const connectedParents = (cell.edges || []).filter(edge => edge.target === cell)
    // check if there are remaining slots to connect
    return connectedParents.length < cell.getValue().getRequiredStreams().length
  }

  function isSink (cell) {
    return cell.getValue().isSink()
  }

  // Defines a new class for all icons
  function mxIconSet (state) {
    this.images = []
    const graph = state.view.graph

    // Output
    const img = mxUtils.createImage('/src/images/submenu.gif')
    img.setAttribute('title', 'Output')
    img.style.position = 'absolute'
    img.style.cursor = 'pointer'
    img.style.width = '16px'
    img.style.height = '16px'
    img.style.left = (state.x + state.width) + 'px'
    img.style.top = (state.y + Math.ceil(state.height / 2) - 8) + 'px'

    mxEvent.addGestureListeners(img, mxUtils.bind(this, function (evt) {
      const pt = mxUtils.convertPoint(graph.container, mxEvent.getClientX(evt), mxEvent.getClientY(evt))
      graph.connectionHandler.start(state, pt.x, pt.y)
      graph.isMouseDown = true
      graph.isMouseTrigger = mxEvent.isMouseEvent(evt)
      mxEvent.consume(evt)
    })
    )

    state.view.graph.container.appendChild(img)
    this.images.push(img)
  };

  mxIconSet.prototype.destroy = function () {
    if (this.images != null) {
      for (var i = 0; i < this.images.length; i++) {
        var img = this.images[i]
        img.parentNode.removeChild(img)
      }
    }

    this.images = null
  }

  // Defines the tolerance before removing the icons
  const iconTolerance = 20

  // Shows icons if the mouse is over a cell
  graph.addMouseListener({
    currentState: null,
    currentIconSet: null,
    mouseDown: () => {},
    mouseMove: function (sender, me) {
      if (this.currentState !== null && (me.getState() === this.currentState || me.getState() === null)) {
        const tol = iconTolerance
        const tmp = new mxRectangle(me.getGraphX() - tol, me.getGraphY() - tol, 2 * tol, 2 * tol)
        if (mxUtils.intersects(tmp, this.currentState)) {
          return
        }
      }

      let tmp = graph.view.getState(me.getCell())

      // Ignores everything but vertices
      if (graph.isMouseDown || (tmp != null && !graph.getModel().isVertex(tmp.cell))) {
        tmp = null
      }

      if (tmp !== this.currentState) {
        if (this.currentState != null) {
          this.dragLeave(me.getEvent(), this.currentState)
        }

        this.currentState = tmp
        if (this.currentState != null) {
          this.dragEnter(me.getEvent(), this.currentState)
        }
      }
    },
    mouseUp: function (sender, me) { },
    dragEnter: function (evt, state) {
      const cell = state.cell
      // check if cell represents Operation
      if (!(cell.getValue() instanceof Operation)) {
        return
      }

      if (isSink(cell)) {
        return
      }

      if (this.currentIconSet == null) {
        this.currentIconSet = new mxIconSet(state)
      }
    },
    dragLeave: function (evt, state) {
      if (this.currentIconSet != null) {
        this.currentIconSet.destroy()
        this.currentIconSet = null
      }
    }
  })

  return graph
}

export function setupPanning (graph) {
  // TODO fix scrollbar move on space hit
  // TODO space + mousemove should move viewport
  // TODO implement and test mobile panning
  // TODO moving objects using keyboard arrows instead scrollbar moving

  // let spaceKeyPressed = false;

  // const keydownHandler = mxUtils.bind(document.getElementById('graphContainer'), function(evt)
  // {
  //     if (evt.which == 32 /* Space */)
  //     {
  //         spaceKeyPressed = true;

  //         // Disables scroll after space keystroke with scrollbars
  //         if (!graph.isEditing() && mxEvent.getSource(evt) == graph.container)
  //         {
  //             mxEvent.consume(evt);
  //         }
  //     }
  // });

  // mxEvent.addListener(document, 'keydown', keydownHandler);

  mxPanningHandler.prototype.isPanningTrigger = function (me) {
    var evt = me.getEvent()

    return (mxEvent.isLeftMouseButton(evt) && ((this.useLeftButtonForPanning &&
                me.getState() == null) || (mxEvent.isControlDown(evt) &&
                !mxEvent.isShiftDown(evt)))) || (this.usePopupTrigger &&
                mxEvent.isPopupTrigger(evt))
  }

  var panningHandlerIsForcePanningEvent = graph.panningHandler.isForcePanningEvent
  graph.panningHandler.isForcePanningEvent = function (me) {
    // Ctrl+left button is reported as right button in FF on Mac
    return panningHandlerIsForcePanningEvent.apply(this, arguments) ||
            // spaceKeyPressed ||
            (mxEvent.isMouseEvent(me.getEvent()) &&
            (this.usePopupTrigger || !mxEvent.isPopupTrigger(me.getEvent())) &&
            ((!mxEvent.isControlDown(me.getEvent()) &&
            mxEvent.isRightMouseButton(me.getEvent())) ||
            mxEvent.isMiddleMouseButton(me.getEvent())))
  }

  graph.panningHandler.usePopupTrigger = true
  graph.setPanning(true)
}

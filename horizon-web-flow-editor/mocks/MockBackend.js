var bodyParser = require('body-parser');
const graphs = require('./graphs.js')
const operations = require('./operations.js')

let GRAPHS_INDEX = graphs.length

function mock (app) {
  console.log('Mock backend enabled')
  app.use(bodyParser.json()); // for parsing application/json
  app.use(bodyParser.urlencoded({ extended: true })); // for parsing application/x-www-form-urlencoded

  /* OPERATIONS */
  app.get('/operations', (req, res) => {
    res.json(operations)
  })

  /* GRAPHS */
  app.get('/graph/:id', (req, res) => {
    const id = +req.params.id
    const graph = graphs.find(graph => graph.id === id)

    if (!graph) {
      res.sendStatus(404)
    }
    res.json(graph)
  })
 
  app.get('/graph', (req, res) => {
    res.json(graphs)
  })

  app.post('/graph', (req, res) => {
    GRAPHS_INDEX++
    const graph = {
      id: GRAPHS_INDEX,
      name: req.body.name,
      created: new Date(),
      edited: new Date(),
      graph: []
    };
    graphs.push(graph)
    res.sendStatus(200)
  })

  app.patch('/graph/:id', (req, res) => {
    const id = +req.params.id
    const graph = graphs.find(graph => graph.id === id)

    if (!graph) {
      res.sendStatus(404)
    }

    graph.graph = req.body.graph
    res.sendStatus(200)
  })

  app.delete('/graph/:id', (req, res) => {
    const id = +req.params.id
    const index = graphs.findIndex(graph => graph.id === id)

    if (index < 0) {
      res.sendStatus(404)
    }

    graphs.splice(index, 1)
    res.sendStatus(200)
  })
}

module.exports = { mock }

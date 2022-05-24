<template>
    <div>
      <div class="uk-clearfix">
          <div class="uk-float-left">
              <router-link tag="button" :to="{name: 'list'}" class="uk-button uk-button-default"><span uk-icon="arrow-left"></span> Back to list</router-link>
          </div>

          <div class="uk-float-right">
              <router-link tag="button" class="uk-button uk-button-primary" :to="{name: 'edit', props: {name: flow.name}}">Edit flow</router-link>
              <button class="uk-button uk-button-danger" v-on:click="deleteFlow">Delete flow</button>
          </div>
      </div>

      <div class="uk-card uk-card-default uk-margin">
          <div class="uk-card-header">
              <h6 class="uk-card-title uk-margin-remove-bottom">Flow details</h6>
          </div>

          <div class="uk-fieldset uk-card-body">
              <dl class="uk-description-list">
                  <dt>Name</dt>
                  <dd>{{ flow.name }}</dd>

                  <dt>Creation date</dt>
                  <dd>{{ new Date(flow.creationDate).toLocaleString() }}</dd>

                  <dt>Status</dt>
                  <dd>
                    <flow-status :status="flow.status"></flow-status>
                  </dd>

                  <dt>Collector endpoint</dt>
                  <dd>{{ flow.collectorEndpoint || 'Not created yet.' }}</dd>

                  <dt>Emitter endpoint</dt>
                  <dd>{{ flow.emitterEndpoint || 'Not created yet.' }}</dd>
              </dl>
          </div>
      </div>

      <div class="uk-card uk-card-default uk-margin">
          <div class="uk-card-header">
              <h6 class="uk-card-title uk-margin-remove-bottom">Collector</h6>
          </div>

          <div class="uk-fieldset uk-card-body">
              <h3>General</h3>
              <div class="uk-margin">
                  <dl class="uk-description-list">
                      <dt>Throughput limit</dt>
                      <dd>{{ flow.collectorThroughputLimit }} req/s</dd>

                      <dt>Throughput maximum limit</dt>
                      <dd>{{ flow.collectorMaxThroughput }} req/s</dd>

                      <dt>Retention</dt>
                      <dd>{{ flow.collectorRetention / 24 }} day(s)</dd>
                  </dl>
              </div>

              <h3>Routing</h3>

              <h4>Http metadata transfer</h4>
              <div class="uk-margin">
                  <p>
                      <span v-if="!flow.collectorRouting.meta.length">No routing specified.</span>
                      <table class="uk-table uk-table-divider" v-if="!!flow.collectorRouting.meta.length">
                          <thead>
                              <tr>
                                  <td>Source input</td>
                                  <td>with name</td>
                                  <td>transfer to metadata field with name</td>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="(rule, index) in flow.collectorRouting.meta" :key="index">
                                  <td>{{ rule.getSourceName() }}</td>
                                  <td>{{ rule.source }}</td>
                                  <td>{{ rule.meta }}</td>
                              </tr>
                          </tbody>
                      </table>
                  </p>
              </div>

              <h4>Routing</h4>
              <div class="uk-margin">
                  <p>
                      <span v-if="!flow.collectorRouting.routing.length">No routing specified.</span>
                      <table class="uk-table uk-table-divider" v-if="!!flow.collectorRouting.routing.length">
                          <thead>
                              <tr>
                                  <td>Match by</td>
                                  <td>with name</td>
                                  <td>and filter by</td>
                                  <td>and insert into topic</td>
                                  <td>and stop matching</td>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="(rule, index) in flow.collectorRouting.routing" :key="index">
                                  <td>{{ rule.getSourceName() }}</td>
                                  <td>{{ rule.source }}</td>
                                  <td>{{ rule.filter }}</td>
                                  <td>{{ rule.topic }}</td>
                                  <td>
                                      <span v-if="!!rule.final" class="uk-margin-small-right" uk-icon="check"></span>
                                      <span v-if="!rule.final" class="uk-margin-small-right" uk-icon="close"></span>
                                  </td>
                              </tr>
                          </tbody>
                      </table>
                  </p>
              </div>

              <h4>Unrouted messages</h4>
              <div class="uk-margin">
                  <p>
                      Errors: {{ flow.collectorRouting.unrouted.error }}<br/>
                      Errors topic: {{ flow.collectorRouting.unrouted.topic }}<br/>
                  </p>
              </div>

              <h3>Topics</h3>
              <div class="uk-margin">
                  <p>
                      <span v-if="!topics.length">No topics created yet.</span>
                      <table class="uk-table uk-table-divider" v-if="!!topics.length">
                          <thead>
                              <tr>
                                  <td>Name</td>
                                  <td>Partitions number</td>
                                  <td>Actions</td>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="(topic, index) in topics" :key="index">
                                  <td>{{ topic.name }}</td>
                                  <td>{{ topic.partitionsNumber }}</td>
                                  <td><button type="button" class="uk-button uk-button-link" v-on:click="deleteTopic(topic.name)">Delete</button></td>
                              </tr>
                          </tbody>
                      </table>
                  </p>

                  <p v-if="!flow.status">Topics creation disabled until flow is fully initialized.</p>
                  <button class="uk-button uk-button-default" type="button" uk-toggle="target: #add-topic" v-if="!!flow.status">Create topic</button>
              </div>
          </div>
      </div>

      <div class="uk-card uk-card-default uk-margin">
          <div class="uk-card-header">
              <h6 class="uk-card-title uk-margin-remove-bottom">Processors</h6>
          </div>

          <div class="uk-fieldset uk-card-body" v-if="!!flow.processors && !flow.processors.length">
              <h3>General</h3>

              <div class="uk-margin">
                  <dl class="uk-description-list">
                      <dt>Type</dt>
                      <dd>Flink</dd>

                      <dt>Taskmanagers number</dt>
                      <dd>{{ flow.flink.replicas }}</dd>

                      <dt>Max taskmanager replicas</dt>
                      <dd>{{ flow.flink.maxReplicas }}</dd>

                      <dt>Plan</dt>
                      <dd>{{ flow.flink.plan }}</dd>
                  </dl>
              </div>

              <h3>Logs</h3>
              <div class="uk-margin">
                <router-link :to="{name: 'processorLogs', params: {flow: flow.name, type: 'flink'}}">LOGS</router-link>
              </div>

              <h3>Jars</h3>
              <div class="uk-margin">
                  <p>List of uploaded jars to the Flink cluster and ready to be run. Dont know how to start? Read our <a href="https://crash.ops.oktawave.com/confluence/pages/viewpage.action?pageId=52954176" target="_blank">guide</a>.</p>
                  <p>
                      <span v-if="!jars.length">No jars uploaded.</span>
                      <table class="uk-table uk-table-divider" v-if="!!jars.length">
                          <thead>
                              <tr>
                                  <th>Name</th>
                                  <th>Upload date</th>
                                  <th>Entrypoints</th>
                                  <th>Actions</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="(jar, index) in jars" :key="index">
                                  <td>{{ jar.name }}</td>
                                  <td>{{ new Date(jar.uploaded).toLocaleString() }}</td>
                                  <td>
                                      {{ jar.entry.map(e => e.name).join(', ') }}
                                  </td>
                                  <td>
                                      <button class="uk-button uk-button-link" type="button" uk-toggle="target: #run-jar" v-on:click="setRunJarForm(jar)">Run</button>
                                      <button class="uk-button uk-button-link" type="button" v-on:click="deleteJar(jar.id)">Delete</button>
                                  </td>
                              </tr>
                          </tbody>
                      </table>
                  </p>
              </div>

              <p v-if="!flow.status">Jars upload disabled until flow is fully initialized.</p>
              <form v-if="!!flow.status">
                  <div class="uk-margin" uk-margin>
                      <div uk-form-custom="target: true">
                          <input type="file" ref="jarfile" v-on:change="handleFileUpload()" id="jarfile" name="jarfile" required>
                          <input class="uk-input uk-form-width-medium" type="text" placeholder="Select jar file" disabled required>
                      </div>
                      <button class="uk-button uk-button-default" v-on:click="submitFile()" :disabled="isJarUploading">
                          <span v-if="!isJarUploading">Upload</span>
                          <div uk-spinner v-if="isJarUploading"></div>
                      </button>
                  </div>
              </form>

              <h3>Jobs</h3>
              <div class="uk-margin">
                  <p>
                      <span v-if="!jobs.jobs.length">No jobs to display.</span>
                      <table class="uk-table uk-table-divider" v-if="!!jobs.jobs.length">
                          <thead>
                              <tr>
                                  <th>Name</th>
                                  <th>Start time</th>
                                  <th>Job Id</th>
                                  <th>Status</th>
                                  <th>Actions</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="(job, index) in jobs.jobs" :key="index">
                                  <td>{{ job.name }}</td>
                                  <td>{{ new Date(job['start-time']).toLocaleString() }}</td>
                                  <td>{{ job.jid }}</td>
                                  <td>{{ job.state }}</td>
                                  <td>
                                      <button type="button" class="uk-button uk-button-link" v-on:click="cancelJob(job.jid)">Cancel</button>
                                  </td>
                              </tr>
                          </tbody>
                      </table>
                  </p>
              </div>
          </div>

          <div class="uk-fieldset uk-card-body" v-if="!!flow.processors && !!flow.processors.length">
              <h3>Custom images</h3>

              <div class="uk-margin">
                  <p>
                      <span v-if="!flow.processors.length">No images specified.</span>
                      <table class="uk-table uk-table-divider" v-if="!!flow.processors.length">
                          <thead>
                              <tr>
                                  <th>Name</th>
                                  <th>Image</th>
                                  <th>Instances #</th>
                                  <th>Max replicas</th>
                                  <th>Credentials</th>
                                  <th>Sgx</th>
                                  <th>Plan</th>
                                  <th>Status</th>
                                  <th>Actions</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="(processor, index) in flow.processors" :key="index">
                                  <td>{{ processor.name }}</td>
                                  <td>{{ processor.imageUrl }}</td>
                                  <td>{{ processor.replicas }}</td>
                                  <td>{{ processor.maxReplicas }}</td>
                                  <td :title="processor.credentials">{{ !!processor.credentials ? processor.credentials.slice(0, 20) + '...' : false }}</td>
                                  <td>
                                      <span v-if="!!processor.sgx" class="uk-margin-small-right" uk-icon="check"></span>
                                      <span v-if="!processor.sgx" class="uk-margin-small-right" uk-icon="close"></span>
                                  </td>
                                  <td>{{ processor.plan }}</td>
                                  <td>{{ processor.status }}</td>
                                  <td><router-link :to="{name: 'processorLogs', params: {flow: flow.name, type: 'custom', processor: processor.name}}">LOGS</router-link></td>
                              </tr>
                          </tbody>
                      </table>
                  </p>
              </div>
          </div>
      </div>

      <div class="uk-card uk-card-default uk-margin">
          <div class="uk-card-header">
              <h6 class="uk-card-title uk-margin-remove-bottom">Emitter</h6>
          </div>

          <div class="uk-fieldset uk-card-body">
              <h3>General</h3>
              <div class="uk-margin">
                  <dl class="uk-description-list">
                      <dt>Storage type</dt>
                      <dd>{{flow.emitter}}</dd>

                      <dt>Storage plan</dt>
                      <dd>{{flow.emitterPlan}}</dd>
                  </dl>
              </div>

              <h3>Routing</h3>
              <div class="uk-margin">
                  <p>
                      <span v-if="!flow.emitterRouting.rules.length">No routing specified.</span>
                      <table class="uk-table uk-table-divider" v-if="!!flow.emitterRouting.rules.length">
                          <thead>
                              <tr>
                                  <th>Rule name</th>
                                  <th>Map internal uri</th>
                                  <th>and expose as</th>
                              </tr>
                          </thead>
                          <tbody>
                              <tr v-for="(rule, index) in flow.emitterRouting.rules" :key="index">
                                  <td>{{ rule.name }}</td>
                                  <td>{{ rule.dst }}</td>
                                  <td>{{ rule.src }}</td>
                              </tr>
                          </tbody>
                      </table>
                  </p>
              </div>
          </div>
      </div>

      <div id="run-jar" uk-offcanvas="overlay: true">
          <div class="uk-offcanvas-bar">
              <button class="uk-offcanvas-close" type="button" uk-close></button>

              <form class="uk-form-stacked">
                  <fieldset class="uk-fieldset">

                      <legend class="uk-legend">Run jar</legend>

                      <p>
                          Jar name: {{ runJarData.name }}<br/>
                          Upload date: {{ new Date(runJarData.uploaded).toLocaleString() }}
                      </p>

                      <div class="uk-alert-danger" uk-alert v-if="!!runJarError">
                          <a class="uk-alert-close" uk-close></a>
                          <p><span uk-icon="warning"></span> {{ runJarError }}</p>
                      </div>

                      <div class="uk-margin">
                          <label class="uk-form-label">Entry class <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Definec entrypoint class for flink job."></span></label>

                          <select v-model="runJarFormData.entryClass" required class="uk-form-controls uk-select">
                              <option v-for="(entryClass, index) in runJarData.entry" v-bind:value="entryClass.name" :key="index">{{entryClass.name}}</option>
                          </select>
                          <form-error v-bind:list="(runJarValidationErrors || {})['error-entryClass']"></form-error>
                      </div>

                      <div class="uk-margin">
                          <label class="uk-form-label" for="form-stacked-text" required>Parralelism <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Defines parallelism for a job. The more parallel instances running the more data can be processed."></span></label>
                          <div class="uk-form-controls">
                              <input class="uk-input" type="number" v-model.number="runJarFormData.parallelism" min="1">
                          </div>
                          <form-error v-bind:list="(runJarValidationErrors || {})['error-parallelism']"></form-error>
                      </div>

                      <div class="uk-margin">
                          <label class="uk-form-label" for="form-stacked-text">Program arguments <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Optional arguments for the job."></span></label>
                          <div class="uk-form-controls">
                              <input class="uk-input" type="text" v-model="runJarFormData.programArgs">
                          </div>
                          <form-error v-bind:list="(runJarValidationErrors || {})['error-programArgs']"></form-error>
                      </div>

                      <div class="uk-margin uk-grid-small uk-child-width-auto uk-grid">
                          <label><input class="uk-checkbox" type="checkbox" v-model="runJarFormData.allowNonRestoredState"> Allow non restored state</label>
                          <form-error v-bind:list="(runJarValidationErrors || {})['error-allowNonRestoredState']"></form-error>
                      </div>

                      <div class="uk-margin">
                          <button type="button" class="uk-button uk-button-secondary" v-on:click="runJar()">
                              <span v-if="!isJarPreparingToRun">Submit</span>
                              <div uk-spinner v-if="isJarPreparingToRun"></div>
                          </button>
                      </div>
                  </fieldset>
              </form>
          </div>
      </div>

      <div id="add-topic" uk-offcanvas="overlay: true">
          <div class="uk-offcanvas-bar">
              <button class="uk-offcanvas-close" type="button" uk-close></button>

              <form class="uk-form-stacked">
                  <fieldset class="uk-fieldset">

                      <legend class="uk-legend">Create topic</legend>

                        <div class="uk-alert-danger" uk-alert v-if="!!createTopicError">
                            <a class="uk-alert-close" uk-close></a>
                            <p><span uk-icon="warning"></span> {{ createTopicError }}</p>
                        </div>

                      <div class="uk-margin">
                          <label class="uk-form-label" v-bind:for="'createTopic'">Name</label>
                          <div class="uk-form-controls">
                              <input class="uk-input" type="text" v-bind:id="'createTopic'" v-model="topicName" required>
                          </div>
                          <form-error v-bind:list="(createTopicValidationErrors || {})['error-name']"></form-error>
                      </div>

                      <div class="uk-margin">
                          <label class="uk-form-label" v-bind:for="'partitionNumber'">Partitions number <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Partitions indicates number of topic replicas. More replicas gives better write operations performance."></span></label>
                          <div class="uk-form-controls">
                              <input class="uk-input" type="number" v-bind:id="'partitionNumber'" v-model="topicPartitionsNumber" required>
                          </div>
                          <form-error v-bind:list="(createTopicValidationErrors || {})['error-partitionsNumber']"></form-error>
                      </div>

                      <div class="uk-margin">
                          <button type="button" class="uk-button uk-button-primary" v-on:click="createTopic(topicName, topicPartitionsNumber)">Submit</button>
                      </div>
                  </fieldset>
              </form>
          </div>
      </div>
  </div>
</template>

<script>
import { mapRoutingRuleToObject, mapMetaRuleToObject } from '@/assets/routing-utils'
import { flattenValidationErrors } from '@/assets/validation-errors-mapper'
import FormError from '@/components/FormError'
import FlowStatus from '@/components/FlowStatus'

export default {
  props: ['name'],
  components: {
    'form-error': FormError,
    'flow-status': FlowStatus
  },
  data: function () {
    return {
      flow: {
        status: {},
        collectorRouting: {
          meta: [],
          routing: [],
          unrouted: {}
        },
        emitterRouting: {
          rules: []
        }
      },
      jars: [],
      topics: [],
      topicName: '',
      topicPartitionsNumber: 1,
      createTopicValidationErrors: [],
      createTopicError: null,
      jarfile: null,
      isJarUploading: false,
      isJarPreparingToRun: false,
      runJarFormData: {},
      runJarData: {},
      runJarValidationErrors: [],
      runJarError: null,
      jobs: {
        // FIXME
        jobs: []
      }
    }
  },
  created: function () {
    this.getFlow()
  },
  methods: {
    getFlow: function () {
      const that = this
      window.client.apis.flow.get_flow__name_({ name: this.$props.name })
        .then(function (data) {
          that.flow = data.body
          that.flow.collectorRouting.routing = that.flow.collectorRouting.routing.map(
            mapRoutingRuleToObject
          )
          that.flow.collectorRouting.meta = that.flow.collectorRouting.meta.map(
            mapMetaRuleToObject
          )
          that.flow.emitterRouting.rules = that.flow.emitterRouting.rules.filter(
            rule => rule.type === that.flow.emitter
          )
          if (!!that.flow.status && !that.flow.processors.length) {
            that.getJars()
            that.getJobs()
          }
          if (that.flow.status) {
            that.getTopics()
          }
        })
    },
    deleteFlow: function () {
      const that = this
      window.client.apis.flow.delete_flow__name_({ name: this.$props.name })
        .then(function (data) {
          that.$router.push({ name: 'list' })
        })
    },
    getTopics: function () {
      const that = this
      window.client.apis.topic.get_topic__flow_({ flow: this.$props.name })
        .then(function (data) {
          that.topics = data.body
        })
    },
    createTopic: function (topicName, partitionsNumber) {
      const that = this
      this.topicName = ''
      this.topicPartitionsNumber = 1
      window.client.apis.topic.post_topic__flow_(
        {
          flow: this.$props.name,
          TopicDto: { name: topicName, partitionsNumber }
        })
        .then(function (data) {
          UIkit.offcanvas('#add-topic').hide()
          that.getTopics()
        })
        .catch(function (error) {
          // FIXME not always message is present
          if (!error.response.body.message) {
            UIkit.notification({
              message: `Request failed with unknown reason. Server responded with status ${error.status}`,
              status: 'danger'
            })
            return
          }

          if (Array.isArray(error.response.body.message)) {
            that.createTopicValidationErrors = flattenValidationErrors(error.response.body.message)
          } else {
            that.createTopicError = error.response.body.message
          }

          UIkit.notification({
            message: 'Your form contains errors.',
            status: 'danger'
          })
        })
    },
    deleteTopic: function (topic) {
      const that = this
      window.client.apis.topic.delete_topic__flow_({ flow: this.$props.name, TopicDto: { name: topic } })
        .then(function (data) {
          that.getTopics()
        })
    },
    handleFileUpload () {
      this.jarfile = this.$refs.jarfile.files[0]
    },
    submitFile () {
      if (this.jarfile) {
        const that = this
        this.isJarUploading = true
        window.client.apis.flink.post_flink__flow__uploadJar({ flow: this.$props.name, jarfile: this.jarfile })
          .then(function (data) {
            that.isJarUploading = false
            that.getJars()
          })
          .catch(function (error) {
            that.isJarUploading = false
            // FIXME not always message is present
            if (!error.response.body.message) {
              UIkit.notification({
                message: `Request failed with unknown reason. Server responded with status ${error.status}`,
                status: 'danger'
              })
            }
          })
      }
    },
    getJars () {
      const that = this
      window.client.apis.flink.get_flink__flow__jars({ flow: that.$props.name })
        .then(function (data) {
          that.jars = data.body
        })
    },
    deleteJar (jarId) {
      const that = this
      window.client.apis.flink.delete_flink__flow__jarId_({ flow: that.$props.name, jarId: jarId })
        .then(function (data) {
          that.getJars()
        })
    },
    setRunJarForm (jar) {
      this.runJarData = jar
      this.runJarFormData = {}
    },
    runJar () {
      const that = this
      this.runJarError = null
      this.runJarValidationErrors = []
      this.isJarPreparingToRun = true
      window.client.apis.flink.post_flink__flow__runJar__jarId_(
        {
          flow: that.$props.name,
          jarId: that.runJarData.id,
          RunJar: that.runJarFormData
        })
        .then(function (data) {
          UIkit.offcanvas('#run-jar').hide()
          that.runJarData = {}
          that.runJarFormData = {}
          that.isJarPreparingToRun = false
          that.getJobs()
        })
        .catch(function (error) {
          that.isJarPreparingToRun = false
          // FIXME not always message is present
          if (!error.response.body.message) {
            UIkit.notification({
              message: `Request failed with unknown reason. Server responded with status ${error.status}`,
              status: 'danger'
            })
            return
          }

          if (Array.isArray(error.response.body.message)) {
            that.runJarValidationErrors = flattenValidationErrors(error.response.body.message)
          } else {
            that.runJarError = error.response.body.message
          }

          UIkit.notification({
            message: 'Your form contains errors.',
            status: 'danger'
          })
        })
    },
    getJobs () {
      const that = this
      window.client.apis.flink.get_flink__flow__jobs({ flow: that.$props.name })
        .then(function (data) {
          that.jobs = data.body
        })
    },
    cancelJob (jobId) {
      const that = this
      window.client.apis.flink.patch_flink__flow__jobs__jobId_({ flow: that.$props.name, jobId: jobId })
        .then(function (data) {
          that.getJobs()
        })
    }
  }
}
</script>

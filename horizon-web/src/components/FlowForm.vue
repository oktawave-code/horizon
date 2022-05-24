<template>
    <form id="flow-form" v-on:submit.prevent="submitForm()">
            <fieldset class="uk-fieldset">
                <div class="uk-card uk-card-default uk-margin">
                    <div class="uk-card-header">
                        <h6 class="uk-card-title uk-margin-remove-bottom">General</h6>
                    </div>

                    <div class="uk-fieldset uk-card-body">
                        <div class="uk-margin uk-width-xlarge">
                            <label class="uk-form-label" for="nameField">Name*  <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Flow name. As it's used in flow endpoint, must contain only alphanumeric characters and be lowercase."></span></label>
                            <input class="uk-input" type="text" id="nameField" required v-model="flowName" :disabled="!!name ? true : false">
                        </div>
                    </div>
                </div>
            </fieldset>

            <div class="uk-card uk-card-default uk-margin">
                <div class="uk-card-header">
                    <h6 class="uk-card-title uk-margin-remove-bottom">Collector</h6>
                </div>

                <div class="uk-fieldset uk-card-body">
                    <fieldset class="uk-fieldset uk-width-xlarge">
                        <legend class="uk-legend">General</legend>

                        <div class="uk-margin">
                            <label class="uk-form-label">Throughtput limit <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Sets ingress limit per second."></span></label>
                            <div uk-grid>
                                <div class="uk-width-expand"><input class="uk-range" type="range" min="1000" max="10000" step="1000" v-model.number="flowCollectorThroughputLimit" required></div>
                                <div class="uk-width-auto">{{ flowCollectorThroughputLimit }} req/s</div>
                            </div>
                            <form-error v-bind:list="(formErrors || {})['error-collectorThroughputLimit']"></form-error>
                        </div>

                        <div class="uk-margin">
                            <label class="uk-form-label">Maximum throughtput limit <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Enables ingress autoscaling during traffic peaks."></span></label>
                            <div uk-grid>
                                <div class="uk-width-expand"><input class="uk-range" type="range" min="1000" max="10000" step="1000" v-model.number="flowCollectorMaxThroughput" required></div>
                                <div class="uk-width-auto">{{ flowCollectorMaxThroughput }} req/s</div>
                            </div>
                            <form-error v-bind:list="(formErrors || {})['error-collectorMaxThroughput']"></form-error>
                        </div>

                        <div class="uk-margin">
                            <label class="uk-form-label">Retention <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Messages are permanently stored for specified period of time."></span></label>
                            <div uk-grid>
                                <div class="uk-width-expand"><input class="uk-range" type="range" min="24" max="168" step="24" v-model.number="flowCollectorRetention" required></div>
                                <div class="uk-width-auto">{{ flowCollectorRetention / 24 }} day(s)</div>
                            </div>
                            <form-error v-bind:list="(formErrors || {})['error-collectorRetention']"></form-error>
                        </div>
                    </fieldset>

                    <div class="uk-section uk-section-xsmall">
                        <fieldset class="uk-fieldset">
                            <legend class="uk-legend">Routing</legend>

                            <h4>Http metadata transfer</h4>
                            <p>
                                Allows to pass additional metadata to processor from message HTTP heareds or URL.
                            </p>
                            <section class="uk-margin">
                                <table class="uk-table uk-table-divider uk-table-small" v-if="!!flowCollectorRouting.meta.length">
                                    <thead>
                                        <tr>
                                            <td>#</td>
                                            <td>Source input</td>
                                            <td>with name</td>
                                            <td>transfer to metadata field with name</td>
                                            <td>Actions</td>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(rule, index) in flowCollectorRouting.meta" :key="index">
                                            <td class="uk-table-middle">
                                                {{index + 1}}.
                                            </td>

                                            <td>
                                                <select required class="uk-form-controls uk-select uk-form-small" v-on:change="updateMetadataRule(index, $event)">
                                                    <option value="header">Header</option>
                                                    <option value="url">Url</option>
                                                </select>
                                            </td>

                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.source" placeholder="Insert source name" required v-bind:disabled="rule.isSourceDisabled">
                                                <form-error v-bind:list="(formErrors || {})['error-collectorRouting-meta-' + index + '-source']"></form-error>
                                            </td>

                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.meta" placeholder="Insert matadata field name" required>
                                                <form-error v-bind:list="(formErrors || {})['error-collectorRouting-meta-' + index + '-meta']"></form-error>
                                            </td>

                                            <td class="uk-table-middle">
                                                <button class="uk-button uk-button-link" type="button" v-on:click="deleteMetaRule(index)">Delete</button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>

                                <button type="button" class="uk-button uk-button-default" v-on:click="addMetaRule">+ Add metadata transfer rule</button>
                            </section>

                            <h4>Routing</h4>
                            <p>
                                Define routing rules for collector.
                            </p>
                            <section class="uk-margin">
                                <table class="uk-table uk-table-divider uk-table-small" v-if="!!flowCollectorRouting.routing.length">
                                    <thead>
                                        <tr>
                                            <td>#</td>
                                            <td>Match</td>
                                            <td>with name</td>
                                            <td>with value <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Filter can be a regexp or simple string."></span></td>
                                            <td>and insert into topic</td>
                                            <td>and stop matching <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="After rule is matched, no further rules will be checked."></span></td>
                                            <td>Actions</td>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(rule, index) in flowCollectorRouting.routing" :key="index">
                                            <td class="uk-table-middle">
                                                {{index + 1}}.
                                            </td>

                                            <td>
                                                <select required class="uk-form-controls uk-select uk-form-small" v-on:change="updateRule(index, $event)" v-once>
                                                    <option value="url" v-bind:selected="rule.getSourceName() === 'url'">Url</option>
                                                    <option value="header" v-bind:selected="rule.getSourceName() === 'header'">Header</option>
                                                    <option value="any" v-bind:selected="rule.getSourceName() === 'any'">All</option>
                                                </select>
                                            </td>

                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.source" placeholder="Specify name" required v-bind:disabled="rule.isSourceDisabled">
                                                <form-error v-bind:list="(formErrors || {})['error-collectorRouting-routing-' + index + '-rule']"></form-error>
                                            </td>

                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.filter" placeholder="Insert filter" v-bind:disabled="rule.isFilterDisabled">
                                                <form-error v-bind:list="(formErrors || {})['error-collectorRouting-routing-' + index + '-filter']"></form-error>
                                            </td>

                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.topic" placeholder="Insert topic name">
                                                <form-error v-bind:list="(formErrors || {})['error-collectorRouting-routing-' + index + '-topic']"></form-error>
                                            </td>

                                            <td class="uk-table-middle">
                                                <input class="uk-checkbox" type="checkbox" v-model="rule.final">
                                                <form-error v-bind:list="(formErrors || {})['error-collectorRouting-routing-' + index + '-final']"></form-error>
                                            </td>
                                            <td class="uk-table-middle">
                                                <button class="uk-button uk-button-link" type="button" v-on:click="deleteRoutingRule(index)">Delete</button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>

                                <button type="button" class="uk-button uk-button-default" v-on:click="addRoutingRule">+ Add routing rule</button>
                            </section>

                            <h4>Unrouted</h4>
                            <section class="uk-width-xlarge">
                                <div class="uk-margin">
                                    <label>
                                        <input class="uk-checkbox" type="checkbox" required v-model="flowCollectorRouting.unrouted.error"> Unrouted
                                        <form-error v-bind:list="(formErrors || {})['error-collectorRouting-unrouted-error']"></form-error>
                                    </label>
                                </div>

                                <div class="uk-margin">
                                    <label class="uk-form-label" v-bind:for="'collectorRoutingUnroutedTopic'">Topic for unrouted messages</label>
                                    <input class="uk-input" type="text" v-bind:id="'collectorRoutingUnroutedTopic'" required v-model="flowCollectorRouting.unrouted.topic">
                                    <form-error v-bind:list="(formErrors || {})['error-collectorRouting-unrouted-topic']"></form-error>
                                </div>
                            </section>
                        </fieldset>
                    </div>
                </div>
            </div>

            <div class="uk-card uk-card-default uk-margin">
                <div class="uk-card-header">
                    <h6 class="uk-card-title uk-margin-remove-bottom">Processor</h6>
                </div>

                <div class="uk-fieldset uk-card-body">

                    <fieldset class="uk-fieldset">

                        <legend class="uk-legend">Processor type</legend>

                        <div class="uk-margin uk-grid-small uk-child-width-auto uk-grid">
                            <label><input class="uk-radio" type="radio" name="radio2" value="flink" checked v-model="processorType"> Flink <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Enables Apache Flink processor. Allows using high-level DSL for defining streaming data processing processes."></span></label>
                            <label><input class="uk-radio" type="radio" name="radio2" value="custom" v-model="processorType"> Custom image <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Enables custom containers as processors. Gives more flexibilty, but requires more manual work. Also allows using Intel SGX functionality for cryptographic purposes."></span></label>
                        </div>

                    </fieldset>

                    <fieldset class="uk-fieldset" v-if="processorType === 'flink'">

                        <legend class="uk-legend">Flink options</legend>
                        <form-error v-bind:list="(formErrors || {})['error-flink']"></form-error>

                        <div class="uk-margin uk-width-xlarge">
                            <label class="uk-form-label">Taskmanagers number <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Defines number of flink nodes available for running tasks."></span></label>
                            <div uk-grid>
                                <div class="uk-width-expand"><input class="uk-range" type="range" min="1" max="5" step="1" v-model.number="flowFlink.replicas" required></div>
                                <div class="uk-width-auto">{{ flowFlink.replicas }}</div>
                                <form-error v-bind:list="(formErrors || {})['error-flink-replicas']"></form-error>
                            </div>
                        </div>

                        <div class="uk-margin uk-width-xlarge">
                            <label class="uk-form-label">Taskmanagers maximum number <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Enables autoscaling of flink nodes number during traffic peak."></span></label>
                            <div uk-grid>
                                <div class="uk-width-expand"><input class="uk-range" type="range" min="1" max="5" step="1" v-model.number="flowFlink.maxReplicas" required></div>
                                <div class="uk-width-auto">{{ flowFlink.maxReplicas }}</div>
                                <form-error v-bind:list="(formErrors || {})['error-flink-maxReplicas']"></form-error>
                            </div>
                        </div>

                        <div class="uk-margin uk-width-xlarge">
                            <label class="uk-form-label" for="flinkProcessorPlan">Plan <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Specifies available resources for single taskmanager node."></span></label>

                            <select v-model="flowFlink.plan" required class="uk-form-controls uk-select" id="flinkProcessorPlan">
                                <option v-for="(option, index) in plans.processorPlan" v-bind:value="option" :key="index">{{option}}</option>
                            </select>
                            <form-error v-bind:list="(formErrors || {})['error-flink-plan']"></form-error>
                        </div>

                    </fieldset>

                    <fieldset class="uk-fieldset " v-if="processorType === 'custom'">
                        <legend class="uk-legend">Processors</legend>
                        <form-error v-bind:list="(formErrors || {})['error-processors']"></form-error>

                        <div class="uk-margin">
                            <p>
                                At least one processor must be created. Dont know how to build processor? Read our <a href="https://crash.ops.oktawave.com/confluence/display/HN/Getting+started" target="_blank">guide</a>.
                            </p>
                            <ul v-if="invalidProcessorsLenth" class="uk-list">
                                <li class="uk-text-danger uk-text-small">Please add processor before submission.</li>
                            </ul>
                            <div v-for="(processor, index) in flowProcessors" class="uk-card uk-card-default uk-margin" :key="index">
                                <div class="uk-card-header">
                                    <h6 class="uk-card-title uk-margin-remove-bottom">Processor {{index + 1}}</h6>
                                    <a class="uk-close-large uk-card-badge" v-on:click="removeProcessor(index)" uk-close></a>
                                </div>

                                <fieldset class="uk-fieldset uk-card-body">
                                    <div class="uk-width-xlarge">
                                        <div class="uk-margin">
                                            <label class="uk-form-label" v-bind:for="'processorName-' + index">Name*</label>
                                            <input class="uk-input" type="text" v-bind:id="'processorName-' + index" required v-model="processor.name">
                                            <form-error v-bind:list="(formErrors || {})['error-processors-' + index + '-name']"></form-error>
                                        </div>

                                        <div class="uk-margin">
                                            <label class="uk-form-label" v-bind:for="'imageUrl-' + index">Image URL* <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Url to publicly accessible container image."></span></label>
                                            <input
                                                class="uk-input"
                                                type="text"
                                                v-bind:id="'imageUrl-' + index"
                                                placeholder="registry.hn.oktawave.com/myProcessor:v1.0"
                                                required
                                                v-model="processor.imageUrl">
                                            <form-error v-bind:list="(formErrors || {})['error-processors-' + index + '-imageUrl']"></form-error>
                                        </div>

                                        <div class="uk-margin">
                                            <label class="uk-form-label" v-bind:for="'credentials-' + index">Credentials <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Base64 encoded security credentials for image access. Supported registries DockerHub, Google Cloud, AWS."></span></label>
                                            <input class="uk-input" type="text" v-bind:id="'credentials-' + index" v-model="processor.credentials">
                                            <form-error v-bind:list="(formErrors || {})['error-processors-' + index + '-credentials']"></form-error>
                                        </div>

                                        <div class="uk-margin uk-width-xlarge">
                                            <label class="uk-form-label">Replicas number* <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Number of image parallel replicas."></span></label>
                                            <div uk-grid>
                                                <div class="uk-width-expand"><input class="uk-range" type="range" min="1" max="5" step="1" v-model.number="processor.replicas" required></div>
                                                <div class="uk-width-auto">{{ processor.replicas }}</div>
                                            </div>
                                            <form-error v-bind:list="(formErrors || {})['error-processors-' + index + '-replicas']"></form-error>
                                        </div>

                                        <div class="uk-margin uk-width-xlarge">
                                            <label class="uk-form-label">Replicas maximum number <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Enables autoscaling of image replicas for increased traffic peak."></span></label>
                                            <div uk-grid>
                                                <div class="uk-width-expand"><input class="uk-range" type="range" min="1" max="5" step="1" v-model.number="processor.maxReplicas" required></div>
                                                <div class="uk-width-auto">{{ processor.maxReplicas }}</div>
                                            </div>
                                            <form-error v-bind:list="(formErrors || {})['error-processors-' + index + '-maxReplicas']"></form-error>
                                        </div>

                                        <div class="uk-margin">
                                            <label class="uk-form-label" for="processorPlan">Plan <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Specifies available resources for container."></span></label>

                                            <select v-model="processor.plan" required class="uk-form-controls uk-select" id="processorPlan">
                                                <option v-for="(option, index) in plans.processorPlan" v-bind:value="option" :key="index">{{option}}</option>
                                            </select>
                                            <form-error v-bind:list="(formErrors || {})['error-processors-' + index + '-plan']"></form-error>
                                        </div>

                                        <div class="uk-margin">
                                            <label v-bind:for="'isSgx-' + index">
                                                <input class="uk-checkbox" type="checkbox" v-bind:id="'isSgx-' + index" v-model="processor.sgx"> Enable SGX <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Allows to use Intel SGX functionality."></span>
                                            </label>
                                            <form-error v-bind:list="(formErrors || {})['error-processors-' + index + '-sgx']"></form-error>
                                        </div>
                                    </div>
                                </fieldset>
                            </div>

                            <button type="button" class="uk-button uk-button-default" v-on:click="addProcessor">+ Add processor</button>
                        </div>
                    </fieldset>
                </div>
            </div>

            <div class="uk-card uk-card-default uk-margin">
                <div class="uk-card-header">
                    <h6 class="uk-card-title uk-margin-remove-bottom">Emitter</h6>
                </div>

                <div class="uk-fieldset uk-card-body">
                    <fieldset class="uk-fieldset uk-width-xlarge">
                        <legend class="uk-legend">Details</legend>

                        <div class="uk-margin">
                            <label class="uk-form-label" for="emitter-select">Storage type <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Specifies storage system for processed data."></span></label>

                            <select v-model="flowEmitter" required class="uk-form-controls uk-select" id="emitter-select" v-on:change="updatePlan()">
                                <option value="elasticsearch">Elasticsearch</option>
                                <option value="redis">Redis</option>
                                <option value="ocs">Ocs</option>
                            </select>
                            <form-error v-bind:list="(formErrors || {})['error-emitter']"></form-error>
                        </div>

                        <div class="uk-margin">
                            <label class="uk-form-label" for="emitterPlan">Plan <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Defines available resources for storage system."></span></label>

                            <select v-model="flowEmitterPlan" required class="uk-form-controls uk-select" id="emitterPlan">
                                <option v-for="(option, index) in getAvailableEmitterPlans(flowEmitter)" v-bind:value="option" :key="index">{{option}}</option>
                            </select>
                            <form-error v-bind:list="(formErrors || {})['error-emitterPlan']"></form-error>
                        </div>

                        <div class="uk-margin" v-if="flowEmitter === 'ocs'">
                            <label class="uk-form-label" for="ocsUser">Ocs user*</label>
                            <input class="uk-input" type="text" id="ocsUser" required v-model="flowEmitterOcsUser">
                            <form-error v-bind:list="(formErrors || {})['error-emitterOcsUser']"></form-error>
                        </div>

                        <div class="uk-margin" v-if="flowEmitter === 'ocs'">
                            <label class="uk-form-label" for="ocsPassword">Ocs password*</label>
                            <input class="uk-input" type="text" id="ocsPassword" required v-model="flowEmitterOcsPassword">
                            <form-error v-bind:list="(formErrors || {})['error-emitterOcsPassword']"></form-error>
                        </div>
                    </fieldset>

                    <div class="uk-section uk-section-xsmall">
                        <fieldset class="uk-fieldset">
                            <legend class="uk-legend">Routing</legend>

                            <section class="uk-margin">
                                <table class="uk-table uk-table-divider uk-table-small">
                                    <thead>
                                        <tr>
                                            <td>#</td>
                                            <td>Rule name</td>
                                            <td>Map internal uri <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Relative path to resource in storage system. Escpecially useful for covering internal system complexity."></span></td>
                                            <td>and exspose as <span uk-icon="icon: info; ratio: 0.7" uk-tooltip="Relative path exposed as Emitter public endpoint."></span></td>
                                            <td>Actions</td>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="(rule, index) in flowEmitterRouting[flowEmitter].rules" :key="index">
                                            <td class="uk-table-middle">
                                                {{index + 1}}.
                                            </td>
                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.name" placeholder="Insert rule name" required>
                                                <form-error v-bind:list="(formErrors || {})['error-emitterRouting-' + index + '-name']"></form-error>
                                            </td>

                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.dst" placeholder="Insert internal uri" required>
                                                <form-error v-bind:list="(formErrors || {})['error-emitterRouting-' + index + '-dst']"></form-error>
                                            </td>

                                            <td>
                                                <input class="uk-input uk-form-blank uk-form-small" type="text" v-model="rule.src" placeholder="Insert public uri" required>
                                                <form-error v-bind:list="(formErrors || {})['error-emitterRouting-' + index + '-src']"></form-error>
                                            </td>

                                            <td class="uk-table-middle">
                                                <button class="uk-button uk-button-link" type="button" v-on:click="deleteEmitterRoutingRule(index)" v-bind:disabled="index === 0">Delete</button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>

                                <button type="button" class="uk-button uk-button-default" v-on:click="addEmitterRoutingRule">+ Add routing rule</button>
                            </section>
                        </fieldset>
                    </div>
                </div>
            </div>

            <div class="uk-margin uk-align-right">
                <button class="uk-button uk-button-primary" type="submit">Submit</button>
                <button class="uk-button uk-button-default" type="button" v-on:click="$emit('cancel')">Cancel</button>
            </div>
        </form>
</template>

<script>
import Vue from 'vue'
import FormError from '@/components/FormError'
import { getRandomName } from '@/assets/name-generator'
import { mapRoutingRuleToObject, mapMetaRuleToObject, AnyRule, UrlMetadataRule, HeaderRule, HeaderMetadataRule, UrlRule } from '@/assets/routing-utils'
import { flattenValidationErrors } from '@/assets/validation-errors-mapper'

export default {
  components: {
    'form-error': FormError
  },
  name: 'FlowForm',
  props: {
    error: Array,
    name: {
      type: String,
      default: ''
    },
    collectorThroughputLimit: {
      type: Number,
      default: 1000
    },
    collectorMinThroughput: Number,
    collectorMaxThroughput: {
      type: Number,
      default: 1000
    },
    collectorRetention: {
      type: Number,
      default: 24
    },
    processors: {
      type: Array,
      default: function () {
        return []
      }
    },
    collectorRouting: {
      type: Object,
      default: function () {
        return {
          meta: [],
          routing: [],
          unrouted: {
            error: true,
            topic: 'err'
          }
        }
      }
    },
    flink: {
      type: Object,
      default: function () {
        return {
          replicas: 1,
          minReplicas: 1,
          maxReplicas: 1,
          plan: window.client.spec.definitions.Processor.properties.plan.enum[0]
        }
      }
    },
    emitter: {
      type: String,
      default: 'elasticsearch'
    },
    emitterPlan: String,
    emitterRouting: {
      type: Object,
      default: function () {
        return {
          rules: []
        }
      }
    },
    emitterOcsUser: String,
    emitterOcsPassword: String
  },
  computed: {
    formErrors: function () {
      return flattenValidationErrors(this.error)
    }
  },
  data: function () {
    const collectorRouterRules = this.collectorRouting.routing.map(
      mapRoutingRuleToObject
    )
    const collectorMetaRules = this.collectorRouting.meta.map(
      mapMetaRuleToObject
    )

    const emitterRoutingRulesConfig = {}
    const emitterTypes = window.client.spec.definitions.FlowDto.properties.emitter.enum
    emitterTypes.forEach(type => {
      emitterRoutingRulesConfig[type] = {
        rules: [{
          name: 'default',
          type: type,
          src: '/',
          dst: '/'
        }]
      }
    })
    if (this.emitterRouting.rules.length) {
      emitterRoutingRulesConfig[this.emitter] = this.emitterRouting
    }

    return {
      flowName: this.name,
      flowProcessors: this.processors,
      flowFlink: this.flink,
      flowCollectorRouting: {
        routing: collectorRouterRules,
        meta: collectorMetaRules,
        unrouted: this.collectorRouting.unrouted
      },
      flowEmitter: this.emitter,
      flowCollectorThroughputLimit: this.collectorThroughputLimit,
      flowCollectorRetention: this.collectorRetention,
      flowEmitterPlan:
        this.emitterPlan ||
        window.client.spec.definitions.FlowDto.properties.emitterPlan.enum[0],
      flowCollectorMaxThroughput: this.collectorMaxThroughput,
      flowEmitterRouting: emitterRoutingRulesConfig,
      flowEmitterOcsUser: this.emitterOcsUser,
      flowEmitterOcsPassword: this.emitterOcsPassword,
      plans: {
        collectorThroughputLimit:
          window.client.spec.definitions.FlowDto.properties.collectorThroughputLimit.enum,
        collectorRetention:
          window.client.spec.definitions.FlowDto.properties.collectorRetention.enum,
        emitterPlan: window.client.spec.definitions.FlowDto.properties.emitterPlan.enum,
        processorPlan: window.client.spec.definitions.Processor.properties.plan.enum
      },
      processorType: this.processors.length ? 'custom' : 'flink',
      invalidProcessorsLenth: false
    }
  },
  methods: {
    addProcessor: function () {
      const that = this
      this.processors.push({
        name: getRandomName().toLowerCase(),
        replicas: 1,
        maxReplicas: 1,
        sgx: false,
        plan: that.plans.processorPlan[0]
      })
    },
    removeProcessor: function (index) {
      this.processors.splice(index, 1)
    },
    deleteMetaRule: function (index) {
      this.flowCollectorRouting.meta.splice(index, 1)
    },
    addMetaRule: function () {
      this.flowCollectorRouting.meta.push(new HeaderMetadataRule())
    },
    deleteRoutingRule: function (index) {
      this.flowCollectorRouting.routing.splice(index, 1)
    },
    addRoutingRule: function () {
      this.flowCollectorRouting.routing.push(new UrlRule())
    },
    deleteEmitterRoutingRule: function (index) {
      this.flowEmitterRouting[this.flowEmitter].rules.splice(index, 1)
    },
    addEmitterRoutingRule: function () {
      this.flowEmitterRouting[this.flowEmitter].rules.push({
        type: this.flowEmitter
      })
    },
    getAvailableEmitterPlans: function (type) {
      return this.plans.emitterPlan.filter(plan =>
        plan.startsWith(type.toUpperCase())
      )
    },
    updatePlan: function () {
      this.flowEmitterPlan = this.getAvailableEmitterPlans(this.flowEmitter)[0]
    },
    updateRule: function (index, event) {
      const option = event.target.value
      switch (option) {
        case 'url':
          Vue.set(this.flowCollectorRouting.routing, index, new UrlRule())
          break
        case 'header':
          Vue.set(this.flowCollectorRouting.routing, index, new HeaderRule())
          break
        case 'any':
          Vue.set(this.flowCollectorRouting.routing, index, new AnyRule())
          break
      }
    },
    updateMetadataRule: function (index, event) {
      const option = event.target.value
      switch (option) {
        case 'url':
          Vue.set(this.flowCollectorRouting.meta, index, new UrlMetadataRule())
          break
        case 'header':
          Vue.set(
            this.flowCollectorRouting.meta,
            index,
            new HeaderMetadataRule()
          )
          break
      }
    },
    getModel: function () {
      const that = this
      if (this.processorType === 'flink') {
        this.flowFlink.minReplicas = this.flowFlink.replicas
      }
      this.flowProcessors.forEach(
        processor => (processor.minReplicas = processor.replicas)
      )
      const collectorRouting = {
        routing: this.flowCollectorRouting.routing.map(rule => rule.getData()),
        meta: this.flowCollectorRouting.meta.map(rule => rule.getData()),
        unrouted: this.flowCollectorRouting.unrouted
      }

      return {
        name: this.flowName,
        processors: this.processorType === 'custom' ? this.flowProcessors : [],
        flink: this.processorType === 'flink' ? this.flowFlink : null,
        collectorRouting: collectorRouting,
        collectorThroughputLimit: this.flowCollectorThroughputLimit,
        collectorMinThroughput: this.flowCollectorThroughputLimit,
        collectorMaxThroughput: this.flowCollectorMaxThroughput,
        collectorRetention: this.flowCollectorRetention,
        emitter: this.flowEmitter,
        emitterPlan: this.flowEmitterPlan,
        emitterRouting: {
          rules: that.flowEmitterRouting[that.flowEmitter].rules
        },
        emitterOcsUser: this.flowEmitterOcsUser,
        emitterOcsPassword: this.flowEmitterOcsPassword
      }
    },
    submitForm: function () {
      const that = this
      const form = document.getElementById('flow-form')
      if (!this.formValid()) {
        UIkit.notification({
          message: 'Your form contains errors.',
          status: 'danger'
        })
        return
      }
      if (form.checkValidity()) {
        this.$emit('submit', that.getModel())
      }
    },
    formValid: function () {
      if (this.processorType === 'custom' && !this.processors.length) {
        this.invalidProcessorsLenth = true
        return false
      }
      return true
    }
  }
}
</script>

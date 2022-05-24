import { FlowDto } from "./dto/flow-dto";
import FlowDetailsDto from "./dto/flow-details-dto";
import { EmitterStorageType, ProcessorPlans, EmitterPlans } from "./constants";
import { Processor } from "./dto/processor-dto";
import { CollectorRouting } from "./dto/collector-routing-dto";
import { EmitterRouting } from "./dto/emitter-routing-dto";
import { FlinkConfiguration } from "./dto/flink-configuration.dto";
import { FlowStatus } from "./dto/flow-status.dto";

function createCollectorSpec(collectorRouting: CollectorRouting, throughput: number, retention: number, minThroughput: number, maxThroughput: number) {
    return {
        collector: {
            cnt: 2,
            limits: {
                input: throughput.toString(),
                inputOptions: minThroughput === maxThroughput ? [minThroughput.toString()] : Array.from(new Array(((maxThroughput - minThroughput) / 1000) + 1), (val, index) => (index * 1000 + minThroughput).toString())
            },
            meta: collectorRouting.meta,
            routing: collectorRouting.routing,
            unrouted: collectorRouting.unrouted
        },
        kafka: {
            cnt: 3,
            retention: retention,
            quota: `${Math.floor((throughput/1000) * 3600 * retention)}M` 
        }
    };
}

function createProcessorSpec(processors: Processor[], flinkConfiguration: FlinkConfiguration) {
  const processorConfiguration = {};
  if (!!flinkConfiguration) {
    processorConfiguration['processor'] = [];
    processorConfiguration['flink'] = {
      cnt: flinkConfiguration.replicas,
      limits: {
          cpu: ProcessorPlans[flinkConfiguration.plan].cpu,
          memory: ProcessorPlans[flinkConfiguration.plan].memory,
          minCnt: flinkConfiguration.minReplicas,
          maxCnt: flinkConfiguration.maxReplicas
      }
    };
  } else {
    processorConfiguration['processor'] = processors.map(prc => {
      return {
          cnt: prc.replicas,
          image: prc.imageUrl,
          name: prc.name,
          sgx: prc.sgx,
          credentials: prc.credentials,
          limits: {
              cpu: ProcessorPlans[prc.plan].cpu,
              memory: ProcessorPlans[prc.plan].memory,
              minCnt: prc.minReplicas,
              maxCnt: prc.maxReplicas
          }
      };
    });
  }

  return processorConfiguration;
}

function createEmitterSpec(emitter: string, emitterPlan: string, router: EmitterRouting, ocsUser: string, ocsPassword: string) {
    const plan = EmitterPlans[emitter].find(plan => plan.name === emitterPlan);
    return {
        elasticsearch: emitter === EmitterStorageType.ELASTICSEARCH ? { name: emitter, cnt: 3, quota: plan.config.quota } : {},
        redis: emitter === EmitterStorageType.REDIS ? { name: emitter, cnt: 3, limits: { memory: plan.config.memory }} : {},
        ocs: emitter === EmitterStorageType.OCS ? { name: emitter, quota: plan.config.quota, user: ocsUser, pass: ocsPassword } : {},
        emitter: {
            cnt: 2,
            limits: {
                output: "1000"
            },
            routing: router.rules
        }
    };
}

function createFlowSpec(clientId: string, name: string, flow: FlowDto) {
    return Object.assign({}, {
        clientId: clientId,
        namespace: [name, clientId].join('-')
    },
    createCollectorSpec(flow.collectorRouting, flow.collectorThroughputLimit, flow.collectorRetention, flow.collectorMinThroughput, flow.collectorMaxThroughput),
    createProcessorSpec(flow.processors, flow.flink),
    createEmitterSpec(flow.emitter, flow.emitterPlan, flow.emitterRouting, flow.emitterOcsUser, flow.emitterOcsPassword));
}

export function getSchema(apiVersion: string, clientId: string, name: string, flow: FlowDto): object {
    return {
        "apiVersion": apiVersion,
        "kind": 'Flow',
        "metadata": {
            "name": `${name}-${clientId}`,
            "labels": {
                "clientId": clientId
            },
            annotations: {
                processorsPlans: JSON.stringify(flow.processors.map(prc => { return {name: prc.name, plan: prc.plan}})),
                flinkPlan: !!flow.flink ? JSON.stringify({plan: flow.flink.plan}) : "{}",
                emitterPlan: flow.emitterPlan
            }
        },
        "spec": createFlowSpec(clientId, name, flow)
    };
};

export function getPatchSchema(apiVersion: string, clientId: string, name: string, flow: FlowDto): object {
    return {
        "metadata": {
            "name": `${name}-${clientId}`,
            "labels": {
                "clientId": clientId
            },
            annotations: {
                processorsPlans: JSON.stringify(flow.processors.map(prc => { return {name: prc.name, plan: prc.plan}})),
                flinkPlan: !!flow.flink ? JSON.stringify({plan: flow.flink.plan}) : "{}", 
                emitterPlan: flow.emitterPlan
            }
        },
        "spec": createFlowSpec(clientId, name, flow)
    };
};


export function mapToFlowDetailsDto(obj: any): FlowDetailsDto {
    const emitterType = !!obj.spec.elasticsearch.cnt ? EmitterStorageType.ELASTICSEARCH
        : obj.spec.redis.cnt ? EmitterStorageType.REDIS
        : obj.spec.ocs.name ? EmitterStorageType.OCS
        : '';

    const collectorLimits = obj.spec.collector.limits.inputOptions;

    const processorPlans = JSON.parse(obj.metadata.annotations.processorsPlans);

    const flow: FlowDetailsDto = {
        name: obj.metadata.name.split('-')[0],
        creationDate: obj.metadata.creationTimestamp,
        status: extractStatus(obj.status),
        collectorEndpoint: !!obj.status && !!obj.status.endpoints ? obj.status.endpoints.collector : null,
        emitterEndpoint: !!obj.status && !!obj.status.endpoints ? obj.status.endpoints.emitter : null,
        collectorRouting: {
            meta: obj.spec.collector.meta,
            routing: obj.spec.collector.routing,
            unrouted: obj.spec.collector.unrouted
        },
        collectorThroughputLimit: Number(obj.spec.collector.limits.input),
        collectorMinThroughput: Number(collectorLimits[0]),
        collectorMaxThroughput: Number(collectorLimits[collectorLimits.length - 1]),
        collectorRetention: obj.spec.kafka.retention,
        flink: !!obj.spec.flink ? {
            replicas: Number(obj.spec.flink.cnt),
            plan: JSON.parse(obj.metadata.annotations.flinkPlan).plan,
            minReplicas: Number(obj.spec.flink.limits.minCnt),
            maxReplicas: Number(obj.spec.flink.limits.maxCnt)
        } : null,
        processors: obj.spec.processor.map(processor => {
            return {
                imageUrl: processor.image,
                replicas: processor.cnt,
                name: processor.name,
                credentials: processor.credentials,
                sgx: processor.sgx,
                plan: processorPlans.find(def => def.name === processor.name).plan,
                minReplicas: processor.limits.minCnt,
                maxReplicas: processor.limits.maxCnt,
                status: extractProcessorStatus(obj.status.podsInfo, processor.name)
            };
        }),
        emitter: emitterType,
        emitterPlan: obj.metadata.annotations.emitterPlan,
        emitterRouting: {rules: obj.spec.emitter.routing},
        emitterOcsUser: obj.spec.emitter.ocsuser
    };
    return flow;
}

function extractProcessorStatus(podsInfo, processorName) {
    const podInfo = (podsInfo || []).find(info => info.name.startsWith('processor-' + processorName));
    if (!podInfo) {
        return "Unknown";
    }
    return detectStatus(podInfo);
}

enum FlowStatusType {
    Ready = "Ready",
    Initializing = "Initializing",
    Failed = "Failed"
}

function extractStatus(status) {
    const componentsStatus = calculateComponentsStatus((status || {}).podsInfo);
    const flowStatus: FlowStatus = {
        status: calculateFlowStatus(status),
        initializing: componentsStatus.initializing,
        ready: componentsStatus.ready,
        failed: componentsStatus.failed,
        expected: componentsStatus.expected 
    }
    return flowStatus;
}

function calculateFlowStatus(status) {
    if (!status || !status.conditions) {
        return null;
    }

    const condition = status.conditions.find(item => item.type === "Available") || {};
    return condition.status === "True";
}

function calculateComponentsStatus(podsInfo) {
    const status = {
        ready: 0,
        initializing: 0,
        failed: 0,
        expected: (podsInfo || 0).length
    };
    (podsInfo || []).forEach(podInfo => {
        const result = detectStatus(podInfo)
        if (result === FlowStatusType.Ready) {
            status.ready++;
        } else if (result === FlowStatusType.Initializing) {
            status.initializing++;
        } else {
            status.failed++
        }
    });
    return status;
}

function detectStatus(podInfo) {
    if ((podInfo.phase === "Running" || podInfo.phase === "Succeeded") && podInfo.Ready.status === "True") {
        return FlowStatusType.Ready;
    } else if (podInfo.phase === "Pending" && podInfo.Ready.status != "True" && podInfo.Unschedulable.status != "True") {
        return FlowStatusType.Initializing;
    } else {
        return FlowStatusType.Failed;
    }
}

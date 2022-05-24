import requests
import json
import sys
import os
from flask import Flask
from flask import jsonify

prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')

app = Flask(__name__)

def doquery(query):
    response = requests.get(prometheus_url + '/api/v1/query', params={'query': query})
    content_json = json.loads(response.content)

    if len(content_json['data']['result']) == 0:
        content_json = 0

    return content_json

def genflowJSON(flow, clientid,
                processor_cpu_total, processor_memory_total, processor_plans,
                flink_cpu_total, flink_memory_total, flink_plans,
                collector_retentions, collector_plans, collector_bytes,
                emitter_plans, emitter_bytes):
    root = {}
    collector = {}
    processor = {}
    flink = {}
    emitter = {}

    root['name'] = flow
    root['clientid'] = clientid
    root['collector'] = collector
    root['emitter'] = emitter
    root['processor'] = processor
    root['flink'] = flink

    collector['plans'] = collector_plans
    collector['network_bytes'] = collector_bytes
    collector['retentions'] = collector_retentions

    processor['plans'] = processor_plans
    processor['cpu'] = processor_cpu_total
    processor['memory'] = processor_memory_total

    flink['plans'] = flink_plans
    flink['cpu'] = flink_cpu_total
    flink['memory'] = flink_memory_total

    emitter['plans'] = emitter_plans
    emitter['network_bytes'] = emitter_bytes

    jsonstr = json.dumps(root)
    return jsonstr

def genflowsJSON(json_flows):
    root = {}
    flows = []

    for flow in json_flows['data']['result']:
        flows.append(flow['metric']['flow_namespace'])

    root['flows'] = flows
    jsonstr = json.dumps(root)
    return jsonstr

@app.route('/')
def root():
    return "Welcome to flowbillexporter!"

@app.route('/flow/')
def flows():
    q_flows = "count by (flow_namespace)(count_over_time(flow_retention[1h]))"
    data_flows = doquery(q_flows)
    jsonstr = genflowsJSON(data_flows)
    return jsonstr

@app.route('/flow/<flow>')
def flow(flow):
    ### queries
    ## global
    # clientid
    q_clientid = "flow_collector_input_limit{flow_namespace=\"%s\",rawValue!=''}[1h]" % (flow)
    data_clientid = doquery(q_clientid)
    if data_clientid != 0:
        clientid = data_clientid['data']['result'][0]['metric']['clientId']
    else:
        return "clientid not found", 404

    ## collector
    # collector bytes
    q_collector_bytes = "sum(increase(nginx_server_bytes{ns=\"%s\",host=~\".*collector.*\",direction=\"in\"}[1h]))" % (flow)
    data_collector_bytes = doquery(q_collector_bytes)
    collector_bytes = 0

    if data_collector_bytes != 0:
        collector_bytes = data_collector_bytes['data']['result'][0]['value'][1]

    # collector retentions
    q_collector_retentions = "sum by (rawValue)(count_over_time(flow_retention{flow_namespace=\"%s\"}[1h]))" % (flow)
    data_collector_retentions = doquery(q_collector_retentions)

    collector_retentions = {}

    if data_collector_retentions != 0:
        for retention_plan in data_collector_retentions['data']['result']:
            collector_retentions.update({retention_plan['metric']['rawValue']: retention_plan['value'][1]})

    #  collector plans #OK
    q_collector_plans = "sum by (rawValue)(count_over_time(flow_collector_input_limit{flow_namespace=\"%s\"}[1h]))" % (flow)
    data_collector_plans = doquery(q_collector_plans)
    collector_plans = {}
    for collector_plan in data_collector_plans['data']['result']:
        collector_plans.update({collector_plan['metric']['rawValue']: collector_plan['value'][1]})

    ## emitter
    # emitter network bytes
    q_emitter_network_bytes = "sum(increase(nginx_server_bytes{ns=\"%s\",host=~\".*emiter.*\",direction=\"out\"}[1h]))" % (flow)
    data_emitter_bytes = doquery(q_emitter_network_bytes)
    emitter_bytes = 0

    if data_emitter_bytes != 0:
        emitter_bytes = data_emitter_bytes['data']['result'][0]['value'][1]

    # emitter plans
    q_emitter_plans = "sum by (rawValue)(count_over_time(flow_emitter_output_limit{flow_namespace=\"%s\"}[1h]))" % (flow)
    data_emitter_plans = doquery(q_emitter_plans)
    emitter_plans = {}
    for emitter_plan in data_emitter_plans['data']['result']:
        emitter_plans.update({emitter_plan['metric']['rawValue']: emitter_plan['value'][1]})

    ## processor
    # processor cpu
    q_processor_cpu = "sum(avg by (container_name)(rate(container_cpu_usage_seconds_total{namespace=\"%s\",container_name=~\"processor.*\"}[1h])))" % (flow)
    data_processor_cpu = doquery(q_processor_cpu)
    processor_cpu_total = 0

    if data_processor_cpu != 0:
        processor_cpu_total = data_processor_cpu['data']['result'][0]['value'][1]

    # processor memory
    q_processor_memory = "sum(avg_over_time(container_memory_usage_bytes{namespace=\"%s\",container_name=~\"processor.*\"}[1h] offset 1h)/1024/1024)" % (flow)
    data_processor_memory = doquery(q_processor_memory)
    processor_memory_total = 0

    if data_processor_memory != 0:
        processor_memory_total = data_processor_memory['data']['result'][0]['value'][1]

    # processor plans
    processor_plans = {}
    processor_cpu_plans = {}
    processor_memory_plans = {}

    q_processor_cpu_plans = "sum by (rawValue)(count_over_time(flow_processor_cpu_plan{flow_namespace=\"%s\"}[1h]))" % (flow)
    q_processor_memory_plans = "sum by (rawValue)(count_over_time(flow_processor_memory_plan{flow_namespace=\"%s\"}[1h]))" % (flow)

    data_processor_cpu_plans = doquery(q_processor_cpu_plans)
    data_processor_memory_plans = doquery(q_processor_memory_plans)

    if data_processor_cpu_plans != 0 and data_processor_memory_plans != 0:
        for processor_cpu_plan in data_processor_cpu_plans['data']['result']:
            processor_cpu_plans.update({processor_cpu_plan['metric']['rawValue']: processor_cpu_plan['value'][1]})

        for processor_memory_plan in data_processor_memory_plans['data']['result']:
            processor_memory_plans.update({processor_memory_plan['metric']['rawValue']: processor_memory_plan['value'][1]})

        processor_plans['cpu'] = processor_cpu_plans
        processor_plans['memory'] = processor_memory_plans

    # flink cpu
    q_flink_cpu = "sum(avg by (container_name)(rate(container_cpu_usage_seconds_total{namespace=\"%s\",container_name=~\"flink-taskmanager.*\"}[1h])))" % (flow)
    data_flink_cpu = doquery(q_flink_cpu)
    flink_cpu_total = 0

    if data_flink_cpu != 0:
        flink_cpu_total = data_flink_cpu['data']['result'][0]['value'][1]

    # flink memory
    q_flink_memory = "sum(avg_over_time(container_memory_usage_bytes{namespace=\"%s\",container_name=~\"flink-taskmanager.*\"}[1h] offset 1h)/1024/1024)" % (flow)
    data_flink_memory = doquery(q_flink_memory)
    flink_memory_total = 0

    if data_flink_memory != 0:
        flink_memory_total = data_flink_memory['data']['result'][0]['value'][1]

	# flink plans
    flink_plans = {}
    flink_cpu_plans = {}
    flink_memory_plans = {}

    q_flink_cpu_plans = "sum by (rawValue)(count_over_time(flow_flink_cpu_plan{flow_namespace=\"%s\"}[1h]))" % (flow)
    q_flink_memory_plans = "sum by (rawValue)(count_over_time(flow_flink_memory_plan{flow_namespace=\"%s\"}[1h]))" % (flow)

    data_flink_cpu_plans = doquery(q_flink_cpu_plans)
    data_flink_memory_plans = doquery(q_flink_memory_plans)

    if data_flink_cpu_plans != 0 and data_flink_memory_plans != 0:
        for flink_cpu_plan in data_flink_cpu_plans['data']['result']:
            flink_cpu_plans.update({flink_cpu_plan['metric']['rawValue']: flink_cpu_plan['value'][1]})

        for flink_memory_plan in data_flink_memory_plans['data']['result']:
            flink_memory_plans.update({flink_memory_plan['metric']['rawValue']: flink_memory_plan['value'][1]})

        flink_plans['cpu'] = flink_cpu_plans
        flink_plans['memory'] = flink_memory_plans

    # build json
    jsonstr = genflowJSON(flow, clientid, 
                          processor_cpu_total, processor_memory_total, processor_plans,
                          flink_cpu_total, flink_memory_total, flink_plans,
                          collector_retentions, collector_plans, collector_bytes, 
                          emitter_plans, emitter_bytes)

    return jsonstr

if __name__ == "__main__":
    app.run(host="0.0.0.0")

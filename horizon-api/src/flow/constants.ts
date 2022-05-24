export enum EmitterStorageType {
    ELASTICSEARCH = 'elasticsearch',
    REDIS = 'redis',
    OCS = 'ocs'
}

export const EmitterStorageTypesNames = Object.keys(EmitterStorageType).map(key => EmitterStorageType[key]);

export const CollectorThroughputLimits = [
    1000,
    2000,
    3000,
    4000,
    5000,
    6000,
    7000,
    8000,
    9000,
    10000
]; 

export const CollectorRetention = [
    24,
    48,
    72,
    96,
    120,
    144,
    168
];

export const ProcessorPlans = {
    CPU_05_MEM_128: {cpu: 0.5, memory: "128Mi"},
    CPU_1_MEM_256: {cpu: "1", memory: "128Mi"}
}

export const ProcessorPlansNames = Object.keys(ProcessorPlans);

export const ElasticsearchPlans = [
    {name: 'ELASTICSEARCH_1GB', config: { quota: "1G" }},
    {name: 'ELASTICSEARCH_2GB', config: { quota: "2G" }},
    {name: 'ELASTICSEARCH_4GB', config: { quota: "4G" }},
    {name: 'ELASTICSEARCH_8GB', config: { quota: "8G" }},
    {name: 'ELASTICSEARCH_16GB', config: { quota: "16G" }},
    {name: 'ELASTICSEARCH_32GB', config: { quota: "32G" }},
    {name: 'ELASTICSEARCH_64GB', config: { quota: "64G" }},
    {name: 'ELASTICSEARCH_128GB', config: { quota: "128G" }}
];

export const RedisPlans = [
    {name: 'REDIS_128MB', config: { memory: "128M" }},
    {name: 'REDIS_256MB', config: { memory: "256M" }}
];

export const OcsPlans = [
    {name: 'OCS_1GB', config: { quota: "1G"}},
    {name: 'OCS_2GB', config: { quota: "2G"}}
];

export const EmitterPlans = {
    elasticsearch: ElasticsearchPlans,
    redis: RedisPlans,
    ocs: OcsPlans
}

export const EmitterPlansNames = Object.keys(EmitterPlans)
        .map(key => EmitterPlans[key])
        .reduce((prev, next) => prev.concat(next), [])
        .map(item => item.name);

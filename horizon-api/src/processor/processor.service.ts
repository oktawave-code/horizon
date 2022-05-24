import { Injectable } from "@nestjs/common";
import Axios from 'axios';
import { HandleAxiosError } from "../utils/AxiosUtils";

@Injectable()
export class ProcessorService {

    client: any;

    constructor() {
        this.client = Axios.create({
            baseURL: (process.env.LOGS_SOURCE || 'http://localhost:9200')
        });
        this.client.interceptors.response.use(function (response) {
            return response;
        }, HandleAxiosError);
    }

    public async getLogsForProcessor(clientId: string, flow: string, processorName: string): Promise<String> {
        const result = await this.client.get(`/filebeat-6.4.1-*/_search?filter_path=hits.hits._source.message`, {
            data: {
                "sort": [
                    {
                        "@timestamp": "asc"
                    }
                ],
                "query": {
                    "bool": {
                        "must": [
                            { "term": { "kubernetes.namespace": `${flow}-${clientId}` } },
                            { "term": { "kubernetes.labels.app": "processor" } },
                            { "term": { "kubernetes.labels.name": processorName } }
                        ]
                    }
                },
                "_source": ["message"],
                "size": 500
            }
        });
        return result.data.hits ? result.data.hits.hits.map(hit => hit._source.message).join('\n') : '';
    }

    public async getLogsForFlink(clientId: string, flow: string): Promise<String> {
        const result = await this.client.get(`/filebeat-6.4.1-*/_search?filter_path=hits.hits._source.message`, {
            data: {
                "sort": [
                    {
                        "@timestamp": "asc"
                    }
                ],
                "query": {
                    "bool": {
                        "must": [
                            { "term": { "kubernetes.namespace": `${flow}-${clientId}` } },
                            { "term": { "kubernetes.labels.app": "flink" } }
                        ]
                    }
                },
                "_source": ["message"],
                "size": 500
            }
        });
        return result.data.hits ? result.data.hits.hits.map(hit => hit._source.message).join('\n') : '';
    }
}
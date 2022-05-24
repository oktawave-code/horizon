import { Injectable, HttpException, NotFoundException, ConflictException, HttpStatus } from "@nestjs/common";
import { FlowDto } from "./dto/flow-dto";
import { getSchema, getPatchSchema, mapToFlowDetailsDto } from "./flow.mappers";
import { K8SApiClient } from "./client.service";
import FlowDetailsDto from "./dto/flow-details-dto";

@Injectable()
export class FlowService {

    client: any;
    apiName: string;

    constructor() {
        const kubeApiConfig = {
            url: (process.env.KUBERNETES_URL || 'https://kubernetes.default.svc') + '/apis',
            
            strictSSL: process.env.K8S_API_STRICT_SSL === 'true',
            caPatch: process.env.K8S_API_CA || '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt',
            
            type: process.env.K8S_AUTH_TYPE || '',

            tokenPatch: process.env.K8S_SERVICEACCOUNT_TOKEN_FILE || '/var/run/secrets/kubernetes.io/serviceaccount/token',
            
            keyPath: (process.env.KEYSTORE || './keystore') + '/key.pem',
            certPath: (process.env.KEYSTORE || './keystore') + '/cert.pem',
        };
        this.apiName = process.env.K8S_FLOWS_API_GROUPNAME || '';
        this.client = new K8SApiClient(kubeApiConfig).getClient();
    }

    public async getAll(clientId: string): Promise<FlowDetailsDto[]> {
        const labelSelector = encodeURIComponent(`clientId=${clientId}`);
        const result = await this.client.get(`/${this.apiName}/flows?labelSelector=${labelSelector}`);
        return result.data.items.map(item => mapToFlowDetailsDto(item));
    }

    public async get(clientId: string, name: string): Promise<FlowDetailsDto> {
        const labelSelector = encodeURIComponent(`clientId=${clientId}`);
        try {
            const result = await this.client.get(`/${this.apiName}/flows/${name}-${clientId}?labelSelector=${labelSelector}`);
            return mapToFlowDetailsDto(result.data);
        } catch (error) {
            if (error.response) {
                if (error.response.status === HttpStatus.NOT_FOUND) {
                    return null;
                }
            }
            throw error;
        }
    }

    public async create(clientId: string, name: string, flow: FlowDto): Promise<any> {
        const existingFlow = await this.get(clientId, name);
        if (existingFlow) {
            throw new ConflictException("Flow with this name already exists.");
        }
        const schema = getSchema(this.apiName, clientId, name, flow);
        const result = await this.client.post(`/${this.apiName}/flows`, schema);
        return {};
    }

    public async update(clientId: string, name: string, flow: FlowDto): Promise<any> {
        const existingFlow = await this.get(clientId, name);
        if (!existingFlow) {
            throw new NotFoundException('Flow does not exist.');
        }
        const schema = getPatchSchema(this.apiName, clientId, name, flow);
        const result = await this.client.patch(`/${this.apiName}/flows/${name}-${clientId}`, schema, {
            headers: {
                'Content-Type': 'application/merge-patch+json'
            }
        });
        return {};
    }

    public async delete(clientId: string, name: string): Promise<any> {
        const result = await this.get(clientId, name);
        if (result && result.name !== name) {
            throw new NotFoundException();
        }
        return await this.client.delete(`/${this.apiName}/flows/${name}-${clientId}`);
    }
}
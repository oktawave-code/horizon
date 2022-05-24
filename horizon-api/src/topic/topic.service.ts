import { Injectable } from "@nestjs/common";
import { TopicDto } from "./topic.dto";
import Axios from "axios";

@Injectable()
export class TopicService {

    FLOW_API_NAME = 'flow-api';

    constructor() {}

    public async getAll(token: string, clientId: string, flow: string): Promise<TopicDto[]> {
        const response = await Axios.get(`http://${this.FLOW_API_NAME}.${flow}-${clientId}/topics`, {
            headers: {
                'Bearer': token
            }
        });   
        return this.topicsToDto(response.data);
    }

    public async create(token: string, clientId: string, flow: string, topic: TopicDto): Promise<any> {
        const response = await Axios({
            url:`http://${this.FLOW_API_NAME}.${flow}-${clientId}/topics`,
            method: 'post',
            headers: {
                'Bearer': token
            },
            data: [topic]
        });
        return this.topicsToDto(response.data);
    }

    public async delete(token: string, clientId: string, flow: string, topic: TopicDto): Promise<any> {
        const response = await Axios({
            url:`http://${this.FLOW_API_NAME}.${flow}-${clientId}/topics`,
            method: 'delete',
            headers: {
                'Bearer': token
            },
            data: [topic.name]
        });
        return this.topicsToDto(response.data);
    }

    topicsToDto(topics: any) {
        const set = topics.map(topic => {
            const t: TopicDto = {
                name: topic.name,
                partitionsNumber: topic.partitionsNumber
            }
            return t;
        })
        return set;
    }
}
import { Injectable, Post } from "@nestjs/common";
import Axios from "axios";
import { JarFileDetails } from "./dto/list-jars-dto";
import { plainToClass } from "class-transformer";
import FormData from 'form-data';
import { RunJar } from "./dto/run-jar-dto";

@Injectable()
export class FlinkService {

    FLINK_API_SERVICE_NAME = process.env.FLINK_API_SERVICE_NAME || 'flink-jobmanager';
    FLINK_API_PORT = process.env.FLINK_API_PORT || 8081;

    constructor() {}

    public async getJars(clientId: string, flow: string): Promise<JarFileDetails[]> {
        const response = await Axios.get(`http://${this.FLINK_API_SERVICE_NAME}.${flow}-${clientId}:${this.FLINK_API_PORT}/jars`);   
        return response.data.files.map(file => plainToClass(JarFileDetails, file));
    }

    public async uploadJar(clientId: string, flow: string, jarfile): Promise<String> {
        const form = new FormData();
        form.append("file", jarfile.buffer, {
            filename: jarfile.originalname,
            contentType: 'application/x-java-archive',
        });
        const response = await Axios.post(`http://${this.FLINK_API_SERVICE_NAME}.${flow}-${clientId}:${this.FLINK_API_PORT}/jars/upload`, form, {
            headers: form.getHeaders()
        });
        return response.data.status;
    }

    public async runJar(clientId: string, flow: string, jarId: string, runJarDto: RunJar) {
        const response = await Axios.post(`http://${this.FLINK_API_SERVICE_NAME}.${flow}-${clientId}:${this.FLINK_API_PORT}/jars/${jarId}/run`, runJarDto); 
        return response.data; 
    }

    public async deleteJar(clientId: string, flow: string, jarId: string) {
        const response = await Axios.delete(`http://${this.FLINK_API_SERVICE_NAME}.${flow}-${clientId}:${this.FLINK_API_PORT}/jars/${jarId}`); 
        return response.data;
    }

    public async getJobs(clientId: string, flow: string) {
        const response = await Axios.get(`http://${this.FLINK_API_SERVICE_NAME}.${flow}-${clientId}:${this.FLINK_API_PORT}/jobs/overview`); 
        return response.data;
    }

    public async getJob(clientId: string, flow: string, jobId: string) {
        const response = await Axios.get(`http://${this.FLINK_API_SERVICE_NAME}.${flow}-${clientId}:${this.FLINK_API_PORT}/jobs/${jobId}`); 
        return response.data;
    }

    public async cancelJob(clientId: string, flow: string, jobId: string) {
        const response = await Axios.patch(`http://${this.FLINK_API_SERVICE_NAME}.${flow}-${clientId}:${this.FLINK_API_PORT}/jobs/${jobId}`); 
        return response.data;
    }
}
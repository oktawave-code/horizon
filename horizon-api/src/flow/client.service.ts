import { Injectable, HttpService } from "@nestjs/common";
import Axios, { AxiosRequestConfig } from 'axios';
import https from 'https';
import fs from 'fs';
import path from 'path';
import { HandleAxiosError } from "../utils/AxiosUtils";

@Injectable()
export class K8SApiClient {

    private config: object;
    public client: any;

    constructor(config: any) {
        this.config = config;

        const axiosConfig = <AxiosRequestConfig>{
            baseURL: config.url
        };

        const httpsAgentConfig = {
            rejectUnauthorized : config.strictSSL,
        }

        if (config.strictSSL) {
            httpsAgentConfig['ca'] = fs.readFileSync(path.resolve(process.cwd(), config.caPatch))
        }

        if (config.type === 'TokenFile') {
            axiosConfig.headers = {
                Authorization: 'Bearer ' + fs.readFileSync(path.resolve(process.cwd(), config.tokenPatch))
            };
        }

        if (config.type === 'X509') {
            httpsAgentConfig['key'] = fs.readFileSync(path.resolve(process.cwd(), config.keyPath));
            httpsAgentConfig['cert'] = fs.readFileSync(path.resolve(process.cwd(), config.certPath));
        }

        axiosConfig.httpsAgent = new https.Agent(httpsAgentConfig);
        this.client = Axios.create(axiosConfig);
        this.client.interceptors.response.use(function (response) {
            return response;
        }, HandleAxiosError);
    }

    getClient() {
        return this.client;
    }

}
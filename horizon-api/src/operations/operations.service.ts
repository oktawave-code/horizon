import { Injectable } from "@nestjs/common";
import Axios from "axios";

@Injectable()
export class OperationsService {

  HORIZON_WEB_EDITOR_SERVER_URL = process.env.HORIZON_WEB_EDITOR_SERVER_URL;

  async get() {
    const response = await Axios.get(`${this.HORIZON_WEB_EDITOR_SERVER_URL}/defs`);
    return response.data;
  }
}
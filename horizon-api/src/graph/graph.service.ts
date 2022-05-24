import { Model } from 'mongoose';
import Axios from 'axios';

import { Injectable, NotFoundException } from "@nestjs/common";
import { GraphDto } from "./dto/graph.dto";
import { GraphDetailsDto } from "./dto/graph-details.dto";
import { CreateGraphDto } from "./dto/create-graph.dto";
import { GraphSchemaDto } from "./dto/graph-schema.dto";
import { InjectModel } from '@nestjs/mongoose';


@Injectable()
export class GraphService {

  HORIZON_WEB_EDITOR_SERVER_URL = process.env.HORIZON_WEB_EDITOR_SERVER_URL;

  constructor(@InjectModel('Graph') private readonly graphModel: Model<GraphDetailsDto>) {}

  async getAll(clientId: String): Promise<GraphDto[]> {
    return await this.graphModel.find({clientId}, 'id name createdAt updatedAt').exec();
  }

  async get(clientId: String, id: String): Promise<GraphDetailsDto> {
    const model = await this.graphModel.findOne({_id: id, clientId}, 'id name createdAt updatedAt graph');
    if (!model) {
      throw new NotFoundException();
    }
    return model;
  }

  async create(clientId: String, createGraphDto: CreateGraphDto) {
    const createdGraph = new this.graphModel(Object.assign({}, {clientId, graph: []}, createGraphDto));
    return await createdGraph.save();
  }

  async update(clientId: String, id: String, graph: GraphSchemaDto) {
    // save validated model
    const model = await this.graphModel.findOneAndUpdate({_id: id, clientId}, graph);
    if (!model) {
      throw new NotFoundException();
    }
    return model;
  }

  async delete(clientId: String, id: String) {
    const model = await this.graphModel.findOneAndDelete({_id: id, clientId});
    if (!model) {
      throw new NotFoundException();
    }
    return model;
  }

  /**
   * 
   * @param graph 
   * @returns Validation errors or null if valid
   */
  async validate(graph: GraphSchemaDto) {
    try {
      // FIXME idiotic but efficient fix for full graph schema validation
      await Axios.post(`${this.HORIZON_WEB_EDITOR_SERVER_URL}/validator`, {
        id: 0,
        name: '',
        created: '',
        edited: '',        
        graph: graph.graph
      });
      // data is valid
      return 
    } catch (error) {
      if (error.response && error.response.status === 400 && error.response.data) {
        // data is invalid, HTTP 400 response, return message
        return error.response.data;
      }
      // something gone wrong, throw error
      throw error;
    }
  }
}
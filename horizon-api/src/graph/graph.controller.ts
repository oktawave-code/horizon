import winston from 'winston';
import { InternalServerErrorException, BadRequestException } from "@nestjs/common";
import { CastError } from "mongoose";

import { Controller, UseGuards, Get, Request, Param, Post, Body, Patch, Delete, NotFoundException } from '@nestjs/common';
import { ApiUseTags, ApiBearerAuth} from '@nestjs/swagger';
import { AuthorizationGuard } from '../guard/AuthorizationGuard';
import { GraphService } from './graph.service';
import { GraphDto } from './dto/graph.dto';
import { GraphDetailsDto } from './dto/graph-details.dto';
import { CreateGraphDto } from './dto/create-graph.dto';
import { GraphSchemaDto } from './dto/graph-schema.dto';

@ApiBearerAuth()
@UseGuards(AuthorizationGuard)
@ApiUseTags('graph')
@Controller('graph')
export class GraphController {

  constructor(private readonly graphService: GraphService) {}
  
  /**
   * Get list of graphs
   */
  @Get()
  async getAll(@Request() req): Promise<GraphDto[]> {
    try {
      return this.graphService.getAll(req.User.Id);
    } catch(error) {
      winston.debug(`Get graphs list. Client: ${req.User.Id}`, error.message);
      throw new NotFoundException();
    }
  }

  /**
   * Get graph by id with config
   * @param id 
   */
  @Get(':id')
  async getFlow(@Request() req, @Param('id') id: String): Promise<GraphDetailsDto> {
    try {
      return await this.graphService.get(req.User.Id, id);
    } catch(error) {
      winston.debug(`Get graph by id. Client: ${req.User.Id}`, error.message);
      
      if (error instanceof CastError || error instanceof NotFoundException) {
        throw new NotFoundException();
      }

      throw new InternalServerErrorException();
    }
  }

  /**
   * Create new graph
   * @param graph - body object containing graph data
   */
  @Post()
  async createFlow(@Request() req, @Body() createGraphDto: CreateGraphDto) {
    try {
      await this.graphService.create(req.User.Id, createGraphDto);
    } catch (error) {
      winston.error('Create graph.', req.User.Id, error);
      throw new InternalServerErrorException();
    }
  }

  /**
   * Update graph model
   * @param id 
   * @param graph 
   */
  @Patch(':id')
  async updateFlow(@Request() req, @Param('id') id: String, @Body() graph: GraphSchemaDto) {
    const validationErrors = await this.graphService.validate(graph);
    if (validationErrors) {
      throw new BadRequestException(validationErrors);
    }
        
    try {
      await this.graphService.update(req.User.Id, id, graph);
    } catch(error) {
      winston.debug(`Update graph by id. Client: ${req.User.Id}`, error.message);
      
      if (error instanceof CastError || error instanceof NotFoundException) {
        throw new NotFoundException();
      }

      throw new InternalServerErrorException();
    }
  }

  /**
   * Delete graph
   * @param id 
   */
  @Delete(':id')
  async deleteFlow(@Request() req, @Param('id') id: String) {
    try {
      await this.graphService.delete(req.User.Id, id);
    } catch(error) {
      winston.debug(`Delete graph by id. Client: ${req.User.Id}`, error.message);
      
      if (error instanceof CastError || error instanceof NotFoundException) {
        throw new NotFoundException();
      }

      throw new InternalServerErrorException();
    }
  }
}
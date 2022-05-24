import { Get, Controller, Param, Post, Body, Delete, Res, Query, UseGuards, Request, Put, UsePipes } from '@nestjs/common';
import { AuthorizationGuard } from '../guard/AuthorizationGuard';
import { ApiUseTags, ApiBearerAuth, ApiCreatedResponse } from '@nestjs/swagger';
import { ProcessorService } from './processor.service';

@ApiBearerAuth()
@UseGuards(AuthorizationGuard)
@ApiUseTags('processor')
@Controller('processor')
export class ProcessorController {

    constructor(private readonly processorService: ProcessorService) {}
    
    @Get(':flow/logs/processor/:processorName')
    @ApiCreatedResponse({ description: 'Returns last 500 lines from processor logs.'})
    async getLogsForProcessor(@Request() req, @Param('flow') flow: string, @Param('processorName') processorName: string): Promise<String> {
        return this.processorService.getLogsForProcessor(req.User.Id, flow, processorName);
    }
    
    @Get(':flow/logs/flink')
    @ApiCreatedResponse({ description: 'Returns last 500 lines from flink logs.'})
    async getLogsForFlink(@Request() req, @Param('flow') flow: string): Promise<String> {
        return this.processorService.getLogsForFlink(req.User.Id, flow);
    }
}
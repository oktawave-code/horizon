import { Get, Controller, Param, Post, Body, Delete, Res, Query, UseGuards, Request, Put, UsePipes, NotFoundException } from '@nestjs/common';
import { FlowDto } from './dto/flow-dto';
import { ApiUseTags, ApiBearerAuth } from '@nestjs/swagger';
import { AuthorizationGuard } from '../guard/AuthorizationGuard';
import { FlowService } from './flow.service';
import { NameValidator } from './name-validator';
import FlowDetailsDto from './dto/flow-details-dto';

@ApiBearerAuth()
@UseGuards(AuthorizationGuard)
@ApiUseTags('flow')
@Controller('flow')
export class FlowController {

    constructor(private readonly flowService: FlowService) {}
    
    @Get()
    async getAll(@Request() req): Promise<FlowDetailsDto[]> {
        return this.flowService.getAll(req.User.Id);
    }

    @Get(':name')
    async getFlow(@Request() req, @Param('name', new NameValidator()) name: string): Promise<FlowDetailsDto> {
        const flow = await this.flowService.get(req.User.Id, name);
        if (!flow) {
            throw new NotFoundException();
        }
        return flow;
    }

    @Post(':name')
    async createFlow(@Request() req, @Param('name', new NameValidator()) name: string, @Body() flow: FlowDto) {
        await this.flowService.create(req.User.Id, name, flow);
    }

    @Put(':name')
    async updateFlow(@Request() req, @Param('name', new NameValidator()) name: string, @Body() flow: FlowDto) {
        await this.flowService.update(req.User.Id, name, flow);
    }

    @Delete(':name')
    async deleteFlow(@Request() req, @Param('name', new NameValidator()) name: string) {
        await this.flowService.delete(req.User.Id, name);
    }
}

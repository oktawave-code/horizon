import { Get, Controller, Param, Post, Delete, UseGuards, Request, Body } from '@nestjs/common';
import { ApiUseTags, ApiBearerAuth } from '@nestjs/swagger';
import { AuthorizationGuard } from '../guard/AuthorizationGuard';
import { TopicDto } from './topic.dto';
import { TopicService } from './topic.service';

@ApiBearerAuth()
@UseGuards(AuthorizationGuard)
@ApiUseTags('topic')
@Controller('topic')
export class TopicController {

    constructor(private readonly topicService: TopicService) {}
    
    @Get(':flow')
    async getAll(@Request() req, @Param('flow') flow: string): Promise<TopicDto[]> {
        return this.topicService.getAll(req.User.Token, req.User.Id, flow);
    }

    @Post(':flow')
    async create(@Request() req, @Param('flow') flow: string, @Body() topic: TopicDto) {
        await this.topicService.create(req.User.Token, req.User.Id, flow, topic);
    }

    @Delete(':flow')
    async delete(@Request() req, @Param('flow') flow: string, @Body() topic: TopicDto) {
        await this.topicService.delete(req.User.Token, req.User.Id, flow, topic);
    }
}

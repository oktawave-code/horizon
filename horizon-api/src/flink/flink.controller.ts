import { Get, Controller, Param, Post, Delete, UseGuards, Request, Body, UseInterceptors, FileInterceptor, UploadedFile, Patch } from '@nestjs/common';
import { ApiUseTags, ApiBearerAuth, ApiConsumes, ApiImplicitFile} from '@nestjs/swagger';
import { AuthorizationGuard } from '../guard/AuthorizationGuard';
import { FlinkService } from './flink.service';
import { JarFileDetails } from './dto/list-jars-dto';
import { RunJar } from './dto/run-jar-dto';

@ApiBearerAuth()
@UseGuards(AuthorizationGuard)
@ApiUseTags('flink')
@Controller('flink')
export class FlinkController {

    constructor(private readonly flinkService: FlinkService) {}
    
    @Get(':flow/jars')
    async getJars(@Request() req, @Param('flow') flow: string): Promise<JarFileDetails[]> {
        return this.flinkService.getJars(req.User.Id, flow);
    }

    // TODO proxy file instead of uploading
    @Post(':flow/uploadJar')
    @UseInterceptors(FileInterceptor('jarfile'))
    @ApiConsumes('multipart/form-data')
    @ApiImplicitFile({
        name: 'jarfile',
        required: true
    })
    async uploadJar(@Request() req, @Param('flow') flow: string, @UploadedFile() jarfile): Promise<String> {
        return this.flinkService.uploadJar(req.User.Id, flow, jarfile);
    }

    @Post(':flow/runJar/:jarId')
    async runJar(@Request() req, @Param('flow') flow: string, @Param('jarId') jarid: string, @Body() runJarDto: RunJar) {
        return this.flinkService.runJar(req.User.Id, flow, jarid, runJarDto);
    }

    @Delete(':flow/:jarId')
    async deleteJar(@Request() req, @Param('flow') flow: string, @Param('jarId') jarid: string) {
        return this.flinkService.deleteJar(req.User.Id, flow, jarid);
    }

    @Get(':flow/jobs')
    async getJobs(@Request() req, @Param('flow') flow: string) {
        return this.flinkService.getJobs(req.User.Id, flow);
    }

    @Get(':flow/jobs/:jobId')
    async getJob(@Request() req, @Param('flow') flow: string, @Param('jobId') jobId: string) {
        return this.flinkService.getJob(req.User.Id, flow, jobId);
    }

    @Patch(':flow/jobs/:jobId')
    async cancelJob(@Request() req, @Param('flow') flow: string, @Param('jobId') jobId: string) {
        return this.flinkService.cancelJob(req.User.Id, flow, jobId);
    }  
}

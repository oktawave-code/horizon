import { Module } from '@nestjs/common';
import { FlinkController } from './flink.controller';
import { FlinkService } from './flink.service';

@Module({
    controllers: [FlinkController],
    providers: [FlinkService]
})

export class FlinkModule{}

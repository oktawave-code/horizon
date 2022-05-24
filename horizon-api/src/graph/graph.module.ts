import { Module } from '@nestjs/common';
import { GraphController } from './graph.controller';
import { GraphService } from './graph.service';
import { MongooseModule } from '@nestjs/mongoose';
import { GraphSchema } from './schema/graph.schema';

@Module({
    controllers: [GraphController],
    providers: [GraphService],
    imports: [MongooseModule.forFeature([{ name: 'Graph', schema: GraphSchema }])]
})

export class GraphModule{}

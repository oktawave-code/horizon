import { Module, MiddlewareConsumer, NestModule } from '@nestjs/common';
import { FlowModule } from './flow/flow.module';
import { AuthorizationMiddleware } from './middleware/authorization.middleware';
import { TopicModule } from './topic/topic.module';
import { FlinkModule } from './flink/flink.module';
import { ProcessorModule } from './processor/processor.module';
import { GraphModule } from './graph/graph.module';
import { MongooseModule } from '@nestjs/mongoose';
import { OperationsModule } from './operations/operations.module';

@Module({
    imports: [
        FlowModule,
        TopicModule,
        FlinkModule,
        ProcessorModule,
        GraphModule,
        OperationsModule,
        MongooseModule.forRoot(process.env.MONGODB_CONNECTION_URL)
    ]
})

export class AppModule implements NestModule {
    configure(consumer: MiddlewareConsumer) {
      consumer
        .apply(AuthorizationMiddleware)
        .forRoutes('/');
    }
  }

import { ApiModelProperty } from "@nestjs/swagger";
import { CollectorRouting } from "./collector-routing-dto";
import { Processor } from "./processor-dto";
import { EmitterRouting } from "./emitter-routing-dto";
import { FlinkConfiguration } from "./flink-configuration.dto";
import { FlowStatus } from "./flow-status.dto";

export default class FlowDetailsDto {

    @ApiModelProperty()
    readonly name: string;

    @ApiModelProperty()
    readonly creationDate: Date;

    @ApiModelProperty()
    readonly status: FlowStatus;

    @ApiModelProperty()
    readonly collectorEndpoint: string;

    @ApiModelProperty()
    readonly collectorThroughputLimit: number;

    @ApiModelProperty()
    readonly collectorMinThroughput: number;

    @ApiModelProperty()
    readonly collectorMaxThroughput: number;
    
    @ApiModelProperty()
    readonly collectorRetention: number;

    @ApiModelProperty()
    readonly emitterEndpoint: string;

    @ApiModelProperty()
    readonly collectorRouting: CollectorRouting;

    @ApiModelProperty()
    readonly processors: ProcessorExtended[];

    @ApiModelProperty()
    readonly flink: FlinkConfiguration;

    @ApiModelProperty()
    readonly emitter: string;

    @ApiModelProperty()
    readonly emitterPlan: string;

    @ApiModelProperty()
    readonly emitterRouting: EmitterRouting;

    @ApiModelProperty()
    readonly emitterOcsUser: string;
}

class ProcessorExtended extends Processor {

    @ApiModelProperty()
    readonly status: String;

}
import { ApiModelProperty } from "@nestjs/swagger";
import { ValidateNested, IsIn, IsDefined, ValidateIf, IsNotEmpty, Validate } from "class-validator";
import { Type } from "class-transformer";
import { CollectorRouting } from "./collector-routing-dto";
import { Processor } from "./processor-dto";
import { EmitterStorageType, CollectorThroughputLimits, CollectorRetention, EmitterStorageTypesNames, EmitterPlansNames } from "../constants";
import { EmitterRouting } from "./emitter-routing-dto";
import { FlinkConfiguration } from "./flink-configuration.dto";
import { IsGreaterOrEqualThan } from "../../utils/GreaterOrEqualThan.validator";
import { ValidEmitterPlan } from "./validators/EmitterPlan.validator";
import { OneOfIsNotEmpty } from "./validators/OneOfIsNotEmpty.validator";

export class FlowDto {
    @ApiModelProperty({
        required: true,
        type: CollectorRouting
    })    
    @ValidateNested()
    @Type(() => CollectorRouting)
    readonly collectorRouting: CollectorRouting;

    @ApiModelProperty({
        required: true,
        enum: CollectorThroughputLimits
    })
    @IsIn(CollectorThroughputLimits)
    @IsGreaterOrEqualThan("collectorMinThroughput")
    readonly collectorThroughputLimit: number;

    @ApiModelProperty({
        required: true,
        enum: CollectorThroughputLimits
    })
    @IsIn(CollectorThroughputLimits)
    readonly collectorMinThroughput: number;

    @ApiModelProperty({
        required: true,
        enum: CollectorThroughputLimits
    })
    @IsIn(CollectorThroughputLimits)
    @IsGreaterOrEqualThan("collectorThroughputLimit")
    readonly collectorMaxThroughput: number;

    @ApiModelProperty({
        required: true,
        enum: CollectorRetention
    })
    @IsIn(CollectorRetention)
    readonly collectorRetention: number;

    @ApiModelProperty({
        isArray: true,
        type: Processor
    })
    @ValidateNested({
        each: true
    })
    @IsDefined()
    
    @Validate(OneOfIsNotEmpty, ["flink", "processors"])
    @Type(() => Processor)
    processors: Processor[];

    @ApiModelProperty({
        type: FlinkConfiguration
    })
    @Validate(OneOfIsNotEmpty, ["flink", "processors"])
    @Type(() => FlinkConfiguration)
    flink: FlinkConfiguration;

    @ApiModelProperty({
        required: true,
        enum: EmitterStorageTypesNames
    })
    @IsIn(EmitterStorageTypesNames)
    emitter: EmitterStorageType;

    @ApiModelProperty({
        required: true,
        enum: EmitterPlansNames
    })
    @Validate(ValidEmitterPlan)
    readonly emitterPlan: string;

    @ApiModelProperty({
        required: true,
        type: EmitterRouting
    })    
    @ValidateNested()
    @Type(() => EmitterRouting)
    readonly emitterRouting: EmitterRouting;

    @ApiModelProperty()
    @ValidateIf(o => o.emitter === EmitterStorageType.OCS)
    @IsNotEmpty()
    readonly emitterOcsUser: string;

    @ApiModelProperty()
    @ValidateIf(o => o.emitter === EmitterStorageType.OCS)
    @IsNotEmpty()
    readonly emitterOcsPassword: string;
}
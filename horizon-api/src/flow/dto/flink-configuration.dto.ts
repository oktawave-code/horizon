import { ApiModelProperty } from "@nestjs/swagger";
import { IsNumber, Min, Max, IsIn } from "class-validator";
import { ProcessorPlansNames } from "../constants";
import { IsGreaterOrEqualThan } from "../../utils/GreaterOrEqualThan.validator";

const MIN_REPLICAS = 1;
const MAX_REPLICAS = 10;

export class FlinkConfiguration {

    @ApiModelProperty({
        required: true,
        default: MIN_REPLICAS,
        minimum: MIN_REPLICAS,
        maximum: MAX_REPLICAS
    })
    @IsNumber()
    @Min(MIN_REPLICAS)
    @Max(MAX_REPLICAS)
    @IsGreaterOrEqualThan("minReplicas")
    readonly replicas: number;
    
    @ApiModelProperty({
        required: true,
        enum: ProcessorPlansNames
    })
    @IsIn(ProcessorPlansNames)
    readonly plan: string;
    
    @ApiModelProperty({
        required: true,
        default: MIN_REPLICAS,
        minimum: MIN_REPLICAS,
        maximum: MAX_REPLICAS
    })
    @IsNumber()
    @Min(MIN_REPLICAS)
    @Max(MAX_REPLICAS)
    readonly minReplicas: number;

    @ApiModelProperty({
        required: true,
        default: MIN_REPLICAS,
        minimum: MIN_REPLICAS,
        maximum: MAX_REPLICAS
    })
    @IsNumber()
    @Min(MIN_REPLICAS)
    @Max(MAX_REPLICAS)
    @IsGreaterOrEqualThan("replicas")
    readonly maxReplicas: number;
}
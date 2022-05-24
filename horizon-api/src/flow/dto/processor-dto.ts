import { ApiModelProperty } from "@nestjs/swagger";
import { IsNotEmpty, IsUrl, IsNumber, Min, Max, IsAlphanumeric, IsLowercase, IsOptional, IsBoolean, IsBase64, IsIn } from "class-validator";
import { ProcessorPlansNames } from "../constants";
import { IsGreaterOrEqualThan } from "../../utils/GreaterOrEqualThan.validator";

const MIN_REPLICAS = 1;
const MAX_REPLICAS = 10;

export class Processor {
    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    @IsUrl()
    readonly imageUrl: string;

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
        required: true
    })
    @IsNotEmpty()
    @IsAlphanumeric()
    @IsLowercase()
    readonly name: string;

    @ApiModelProperty({
        required: false,
        default: false
    })
    @IsOptional()
    @IsBoolean()
    readonly sgx: boolean;

    @ApiModelProperty({
        required: false
    })
    @IsOptional()
    @IsBase64()
    readonly credentials: string;

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
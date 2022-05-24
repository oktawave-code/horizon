import { ApiModelProperty } from "@nestjs/swagger";
import { IsBoolean, ValidateNested, IsNotEmpty } from "class-validator";
import { Type } from "class-transformer";

class RoutingMetadataRule {

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    readonly meta: string;

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    readonly source: string;
}

class RoutingRule {

    @ApiModelProperty()
    readonly filter: string;

    @ApiModelProperty()
    readonly source: string;

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    readonly topic: string;

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    readonly final: boolean;
}

class Unrouted {

    @ApiModelProperty({
        required: false,
        default: true
    })
    @IsBoolean()
    readonly error: boolean;

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    readonly topic: string;
}

export class CollectorRouting {

    @ApiModelProperty({
        required: true,
        isArray: true,
        type: RoutingMetadataRule
    })
    @ValidateNested({
        each: true
    })
    @Type(() => RoutingMetadataRule)
    readonly meta: RoutingMetadataRule[];


    @ApiModelProperty({
        required: true,
        isArray: true,
        type: RoutingRule
    })
    @ValidateNested({
        each: true
    })
    @Type(() => RoutingRule)
    readonly routing: RoutingRule[];


    @ApiModelProperty({
        required: true,
        type: Unrouted
    })
    @ValidateNested()
    readonly unrouted: Unrouted;
}
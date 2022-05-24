import { ApiModelProperty } from "@nestjs/swagger";
import { ValidateNested, IsIn, IsNotEmpty, ArrayNotEmpty } from "class-validator";
import { Type } from "class-transformer";
import { EmitterStorageTypesNames } from "../constants";

class EmitterRoutingRule {

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    name: string;

    @ApiModelProperty({
        required: true,
        enum: EmitterStorageTypesNames
    })
    @IsIn(EmitterStorageTypesNames)
    type: string;

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    src: string;

    @ApiModelProperty({
        required: true
    })
    @IsNotEmpty()
    dst: string;
}

export class EmitterRouting {

    @ApiModelProperty({
        required: true,
        isArray: true,
        type: EmitterRoutingRule
    })
    @ValidateNested({
        each: true
    })
    @ArrayNotEmpty()
    @Type(() => EmitterRoutingRule)
    rules: EmitterRoutingRule[];   
}
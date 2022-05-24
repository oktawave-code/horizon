import { ApiModelProperty } from "@nestjs/swagger";
import { Min, IsNotEmpty, IsBoolean, IsInt, IsNumber } from "../../../node_modules/class-validator";

export class RunJar {
    
    @ApiModelProperty()
    @IsNotEmpty()
    readonly entryClass: string;

    @ApiModelProperty({
        required: true,
        minimum: 1
    })
    @IsNumber()
    @Min(1)
    readonly parallelism: Number;

    @ApiModelProperty()
    readonly programArgs: string;

    @ApiModelProperty()
    readonly savepointPath: string;

    @ApiModelProperty()
    readonly allowNonRestoredState: Boolean;
}
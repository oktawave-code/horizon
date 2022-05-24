import { ApiModelProperty } from "@nestjs/swagger";
import { IsNotEmpty, IsNumber, Min, Length, IsAlphanumeric } from "../../node_modules/class-validator";

const TOPIC_MIN_LENGTH = 1;
const TOPIC_MAX_LENGTH = 200;

export class TopicDto {
    @ApiModelProperty({
        required: true,
        type: String,
        minLength: TOPIC_MIN_LENGTH,
        maxLength: TOPIC_MIN_LENGTH
    })
    @IsNotEmpty()
    @Length(TOPIC_MIN_LENGTH, TOPIC_MAX_LENGTH)
    @IsAlphanumeric()
    readonly name: string;

    @ApiModelProperty({
        required: true,
        type: Number,
        minimum: 1
    })
    @IsNumber()
    @Min(1)
    readonly partitionsNumber: Number;
}
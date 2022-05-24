import { Type } from "class-transformer";
import { ApiModelProperty } from "@nestjs/swagger";

export class EntryDetails {

    @ApiModelProperty()
    readonly name: string;

    @ApiModelProperty()
    readonly description: string;
}

export class JarFileDetails {

    @ApiModelProperty()
    readonly id: string;

    @ApiModelProperty()
    readonly name: string;

    @ApiModelProperty()
    readonly uploaded: Number;

    @ApiModelProperty({
        isArray: true,
        type: EntryDetails
    })
    @Type(() => EntryDetails)
    readonly entry: EntryDetails[];
}
import { ApiModelProperty } from "@nestjs/swagger";

export class GraphDto {
  
  @ApiModelProperty()
  readonly id: Number;

  @ApiModelProperty()
  readonly name: String;

  @ApiModelProperty()
  readonly created: Date;

  @ApiModelProperty()
  readonly edited: Date;
}
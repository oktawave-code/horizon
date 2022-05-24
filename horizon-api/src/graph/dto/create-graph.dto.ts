import { ApiModelProperty } from "@nestjs/swagger";

export class CreateGraphDto {

  @ApiModelProperty()
  readonly name: String;
}
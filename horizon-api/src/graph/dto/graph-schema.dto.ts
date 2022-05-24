import { ApiModelProperty } from "@nestjs/swagger";

export class GraphSchemaDto {

  // FIXME Swagger generates object in array, wchich is incorrect,
  // correct value is array
  @ApiModelProperty({
    type: [Object]
  })
  readonly graph: Object[];
}
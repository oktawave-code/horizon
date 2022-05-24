import { ApiModelProperty } from "@nestjs/swagger";
import { GraphDto } from "./graph.dto";

export class GraphDetailsDto extends GraphDto {
  
  @ApiModelProperty()
  readonly graph: String;

}
import { ApiModelProperty } from "@nestjs/swagger";

export class FlowStatus {
    
    @ApiModelProperty()
    readonly status: Boolean;

    @ApiModelProperty()
    readonly initializing: Number;
    
    @ApiModelProperty()
    readonly ready: Number;
    
    @ApiModelProperty()
    readonly failed: Number;
    
    @ApiModelProperty()
    readonly expected: Number;
}
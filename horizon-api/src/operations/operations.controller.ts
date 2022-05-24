import { UseGuards, Get, Controller } from '@nestjs/common';
import { ApiBearerAuth, ApiExcludeEndpoint} from '@nestjs/swagger';
import { AuthorizationGuard } from '../guard/AuthorizationGuard';
import { OperationsService } from './operations.service';

@ApiBearerAuth()
@UseGuards(AuthorizationGuard)
@Controller('operations')
export class OperationsController {

  constructor(private readonly operationsService: OperationsService) {}
  
  @ApiExcludeEndpoint()
  @Get()
  async get() {
    return await this.operationsService.get();
  }
}
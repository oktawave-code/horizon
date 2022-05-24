import { Test } from '@nestjs/testing';
import { FlowService } from './flow.service';

describe('FlowService', () => {
    let flowService: FlowService;
    const CLIENT_ID = '1';

    beforeEach(async () => {
        const module = await Test.createTestingModule({
            providers: [FlowService]
        }).compile();

        flowService = module.get<FlowService>(FlowService);
    });

    describe('getAll', () => {
        it('should return array of flows', async () => {
            const result = ['test'];
            jest.spyOn(flowService, 'getAll').mockImplementation(() => result);

            expect(await flowService.getAll(CLIENT_ID)).toBe(result);
        });
    });

    describe('get', () => {
        it('should return flow by id');
    });

    describe('create', () => {
        it('should create flow');
    });

    describe('delete', () => {
        it('should remove flow');
    });

});
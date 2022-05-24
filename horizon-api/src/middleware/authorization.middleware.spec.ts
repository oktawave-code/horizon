import { Test } from '@nestjs/testing';
import { AuthorizationMiddleware } from './authorization.middleware';
import nock from 'nock';
import axios from 'axios';
import sinon from 'sinon';
// todo use nock


describe('Request authorization', () => {
    let authorization: Function;
    const next = () => {};
    const res = {};
    let spy = sinon.spy(axios, 'get');

    beforeEach(async () => {
        spy.resetHistory();
        process.env.AUTHORIZATION_URL = 'http://localhost/validate';
        authorization = await new AuthorizationMiddleware().resolve();
    });

    it('Should authorize user with correct token', async () => {
        const req = {
            get: () => 'VALID_TOKEN'
        };
        
        nock(process.env.AUTHORIZATION_URL)
            .get('')
            .query({token: 'VALID_TOKEN'})
            .reply(200, {sub: 'VALID_USER_ID'});
        
        await authorization(req, res, next);
        
        expect(spy.called).toBeTruthy();
        expect(req['User']['Id']).toBe('VALID_USER_ID');
    });

    it('Should skip token validation if no token provided', async () => {
        const req = {
            get: () => null
        };

        await authorization(req, res, next);

        expect(spy.called).toBeFalsy();
        expect(!!req['User']['Id']).toBeFalsy();
    });

    it('Should leave empty user id when incorrect token', async () => {
        const req = {
            get: () => 'INVALID_TOKEN'
        };
        
        nock(process.env.AUTHORIZATION_URL)
            .get('')
            .query({token: 'INVALID_TOKEN'})
            .reply(401, {message: 'ERROR'});

        await authorization(req, res, next);

        expect(spy.called).toBeTruthy();
        expect(req['User']['Id']).toBeFalsy();
    });
});
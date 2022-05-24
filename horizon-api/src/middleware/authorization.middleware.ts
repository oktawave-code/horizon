import { NestMiddleware, Injectable, MiddlewareFunction, HttpService } from "@nestjs/common";
import Axios from 'axios';
import winston from 'winston';
import https from 'https';

@Injectable()
export class AuthorizationMiddleware implements NestMiddleware {
    async resolve(...args: any[]): Promise<MiddlewareFunction> {
        return async (req, res, next) => {
            const authorizationUrl = process.env.AUTHORIZATION_URL || 'http://localhost/validate';
            const token = req.get('Bearer');
            let userdata = {};

            // Validate request only if token is provided
            if (!!token) {
                try {
                    const response = await Axios.get(authorizationUrl + '?token=' + token, {
                        httpsAgent: new https.Agent({rejectUnauthorized: false})
                    });
                    userdata = response.data;
                } catch(e) {
                    winston.debug('Authorization error', e.message);
                    userdata = {};
                }
            }

            req.User = {
                /* Id is used for naming namespaces, so it must meet validation requrements for namespace names. It has to be lowercase string 
                 * containing only DNS name save characters.
                 */
                Id: !!userdata['sub'] ? new String(userdata['sub']).toLowerCase() : undefined,
                Token: token
            };
            next();
        }
    }
}
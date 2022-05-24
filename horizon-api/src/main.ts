import dotenv from 'dotenv';
dotenv.config();

import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import helmet from 'helmet';
import { AppModule } from './app.module';

import express from 'express';
import winston from 'winston';
import Axios from 'axios';

import { ValidationPipe } from '@nestjs/common';
import { HandleAxiosError } from './utils/AxiosUtils';

const followRedirects = require('follow-redirects');
followRedirects.maxBodyLength = 100 * 1024 * 1024;

async function bootstrap() {

    winston.level = process.env.LOGLEVEL || 'info';

    const server = express();
    const app = await NestFactory.create(AppModule, server, {});
    app.use(helmet({
        contentSecurityPolicy: false,
    }));
    app.enableCors();
    app.useGlobalPipes(new ValidationPipe({
        validationError: { 
            target: false,
            value: false
        }
    }));
    
    Axios.interceptors.response.use(function (response) {
        return response;
    }, HandleAxiosError);

    const options = new DocumentBuilder()
        .setTitle('Horizon Client API')
        .setVersion('1.0')
        .addBearerAuth('Bearer', 'header')
        .setSchemes('http', 'https')
        .build();

    const document = SwaggerModule.createDocument(app, options);
    SwaggerModule.setup('/api', app, document);
    
    server.get('/api-docs/swagger.json', (req, res) => res.json(document));

    const port = process.env.APPLICATION_PORT || '80';
    await app.listen(port);
    winston.info(`Server is listening on port ${port}.`);
}

bootstrap();

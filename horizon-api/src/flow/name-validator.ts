import { Injectable, PipeTransform, ArgumentMetadata, BadRequestException } from "@nestjs/common";
import { Validator } from "class-validator";


@Injectable()
export class NameValidator implements PipeTransform<any> {

    validate = new Validator();

    async transform(value: any, { metatype }: ArgumentMetadata) {
        const MIN_LEN = 1;
        const MAX_LEN = 100;
        const isString = this.validate.isString(value);
        const isAlphanumeric = this.validate.isAlphanumeric(value);
        const isLowercase = this.validate.isLowercase(value);
        const isLengthInRange = this.validate.length(value, MIN_LEN, MAX_LEN);

        if (!isString) {
            throw new BadRequestException('Name must be string');
        }

        if (!isAlphanumeric) {
            throw new BadRequestException('Name must be alphanumeric');
        }

        if (!isLowercase) {
            throw new BadRequestException('Name must contain onlu lowercase letters');
        }

        if (!isLengthInRange) {
            throw new BadRequestException(`Name length must be between ${MIN_LEN} and ${MAX_LEN}`);
        }

        return value;
    }
}
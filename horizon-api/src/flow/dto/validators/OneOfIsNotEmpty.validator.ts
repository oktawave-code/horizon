import {ValidatorConstraint, ValidatorConstraintInterface, ValidationArguments} from "class-validator";

@ValidatorConstraint({ name: "oneOfIsNotEmpty", async: false })
export class OneOfIsNotEmpty implements ValidatorConstraintInterface {

    validate(property: any, args: ValidationArguments) {
        const definedProperties = args.constraints.filter(prop => {
            if (Array.isArray(args.object[prop])) {
                return !!args.object[prop].length;
            }
            return args.object[prop] !== '' && args.object[prop] !== null && args.object[prop] !== undefined;
        });
        return definedProperties.length === 1; // for async validations you must return a Promise<boolean> here
    }

    defaultMessage(args: ValidationArguments) {
        return `One and only one of [${args.constraints.join(', ')}] properties must not be empty.`;
    }
}
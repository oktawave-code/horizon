import {registerDecorator, ValidationOptions, ValidationArguments} from "class-validator";

export function IsGreaterOrEqualThan(property: string, validationOptions?: ValidationOptions) {
   return function (object: Object, propertyName: string) {
        registerDecorator({
            name: "isGreaterOrEqualThan",
            target: object.constructor,
            propertyName: propertyName,
            constraints: [property],
            options: validationOptions,
            validator: {
                validate(value: any, args: ValidationArguments) {
                    const [relatedPropertyName] = args.constraints;
                    const relatedValue = (args.object as any)[relatedPropertyName];
                    return  typeof value === "number" &&
                           typeof relatedValue === "number" &&
                           value >= relatedValue;
                },

                defaultMessage(args: ValidationArguments) {
                    const [relatedPropertyName] = args.constraints;
                    return `Value of ${propertyName} must be greater than ${relatedPropertyName}`;
                }
            }
        });
   };
}
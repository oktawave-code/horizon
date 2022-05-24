import {ValidatorConstraint, ValidatorConstraintInterface, ValidationArguments} from "class-validator";
import FlowDetailsDto from "../flow-details-dto";
import { EmitterPlans } from "../../constants";

@ValidatorConstraint({ name: "validEmitterPlan", async: false })
export class ValidEmitterPlan implements ValidatorConstraintInterface {

    validate(plan: string, args: ValidationArguments) {
        const emitterType = (args.object as FlowDetailsDto).emitter;
        const storagePlans = (EmitterPlans[emitterType] || []).map(plan => plan.name);
        return storagePlans.find(p => p === plan); // for async validations you must return a Promise<boolean> here
    }

    defaultMessage(args: ValidationArguments) {
        const emitterType = (args.object as FlowDetailsDto).emitter;
        const storagePlans = (EmitterPlans[emitterType] || []).map(plan => plan.name);
        return `Incorrect plan for emitter type ${emitterType}. Available plans: ${storagePlans.join(', ')}.`;
    }

}
import {validate, Validate} from "class-validator";
import { OneOfIsNotEmpty } from "./OneOfIsNotEmpty.validator";

export class Post {

    @Validate(OneOfIsNotEmpty, ["object", "array"])
    array: string[];

    @Validate(OneOfIsNotEmpty, ["object", "array"])
    object: Object;

}

describe('IsDefinedIfEmpty validation', () => {

    it('both unedfined', async () => {
        let testObject = new Post();
        testObject.array = null;
        testObject.object = null;

        const errors = await validate(testObject);
        expect(errors.length).toBe(2);
    });

    it('array empty and object set', async () => {
        let testObject = new Post();
        testObject.array = [];
        testObject.object = {};
        
        const errors = await validate(testObject);
        expect(errors.length).toBe(0);
    });

    it('array empty and object not set', async () => {
        let testObject = new Post();
        testObject.array = [];
        testObject.object = null;
        
        const errors = await validate(testObject);
        expect(errors.length).toBe(2);
    });
    
    it('array undefined, and object set', async () => {
        let testObject = new Post();
        testObject.array = null;
        testObject.object = {};
        
        const errors = await validate(testObject);
        expect(errors.length).toBe(0);
    });
    
    it('array not empty, and object not set', async () => {
        let testObject = new Post();
        testObject.array = ["x"];
        testObject.object = null;
        
        const errors = await validate(testObject);
        expect(errors.length).toBe(0);
    });
    
    it('both set', async () => {
        let testObject = new Post();
        testObject.array = ['a'];
        testObject.object = {a:1};
        
        const errors = await validate(testObject);
        expect(errors.length).toBe(2);
    });
});


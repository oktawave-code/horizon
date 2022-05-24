package horizon;

import org.junit.Test;

public class FlinkOpStringTransformTest extends FlinkOperationTestBase {

    @Test
    public void testInvalid() throws Exception {
        Tester tester = new Tester(new FlinkOpStringTransform());

        tester.property("inputField", "txt");
        tester.property("operation", "Uppercase");

        tester.packet("{}");
        tester.packet("{\"txt\":\"123\"}");
        tester.packet("{\"txt\":123}");

        tester.execute();

        tester.verify(0, "{}");
        tester.verify(1, "{\"txt\":\"123\"}");
        tester.verify(2, "{\"txt\":\"123\"}"); // Undefined case?
    }

    @Test
    public void testUppercase() throws Exception {
        Tester tester = new Tester(new FlinkOpStringTransform());

        tester.property("inputField", "txt");
        tester.property("operation", "Uppercase");

        tester.packet("{\"txt\":\"abc\"}");
        tester.packet("{\"txt\":\"aBc7\", \"x\":\"a\"}");

        tester.execute();

        tester.verify(0, "{\"txt\":\"ABC\"}");
        tester.verify(1, "{\"txt\":\"ABC7\",\"x\":\"a\"}");
    }

    @Test
    public void testLowercase() throws Exception {
        Tester tester = new Tester(new FlinkOpStringTransform());

        tester.property("inputField", "txt");
        tester.property("operation", "Lowercase");

        tester.packet("{\"txt\":\"ABC\"}");
        tester.packet("{\"txt\":\"aBc7\", \"x\":\"a\"}");

        tester.execute();

        tester.verify(0, "{\"txt\":\"abc\"}");
        tester.verify(1, "{\"txt\":\"abc7\",\"x\":\"a\"}");
    }

    @Test
    public void testCapitalize() throws Exception {
        Tester tester = new Tester(new FlinkOpStringTransform());

        tester.property("inputField", "txt");
        tester.property("operation", "Capitalize");

        tester.packet("{\"txt\":\"ABC\"}");
        tester.packet("{\"txt\":\"aBc7\", \"x\":\"a\"}");

        tester.execute();

        tester.verify(0, "{\"txt\":\"Abc\"}");
        tester.verify(1, "{\"txt\":\"Abc7\",\"x\":\"a\"}");
    }
}

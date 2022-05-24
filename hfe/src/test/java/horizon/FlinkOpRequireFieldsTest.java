package horizon;

import org.junit.Test;

public class FlinkOpRequireFieldsTest extends FlinkOperationTestBase {

    @Test
    public void testFields() throws Exception {
        Tester tester = new Tester(new FlinkOpRequireFields());

        tester.property("requiredFields", "a,b");

        tester.packet("{}");
        tester.packet("{\"x\":\"123\"}");
        tester.packet("{\"a\":\"123\", \"b\":\"123\", \"x\":\"123\"}");
        tester.packet("{\"a\":\"123\", \"x\":\"123\"}");
        tester.packet("{\"b\":\"123\", \"c\":\"1234\"}");
        tester.packet("{\"a\":\"123\", \"b\":\"1234\"}");

        tester.execute();

        tester.verify(0, "{\"a\":\"123\", \"b\":\"123\", \"x\":\"123\"}");
        tester.verify(1, "{\"a\":\"123\", \"b\":\"1234\"}");
    }
}


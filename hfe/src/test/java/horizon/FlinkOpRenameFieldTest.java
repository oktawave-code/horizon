package horizon;

import org.junit.Test;

public class FlinkOpRenameFieldTest extends FlinkOperationTestBase {

    @Test
    public void testFields() throws Exception {
        Tester tester = new Tester(new FlinkOpRenameField());

        tester.property("inputField", "a");
        tester.property("outputField", "b");

        tester.packet("{}");
        tester.packet("{\"a\":\"123\"}");
        tester.packet("{\"b\":\"123\"}");
        tester.packet("{\"a\":123, \"b\":\"q\"}");
        tester.packet("{\"a\":{}, \"c\":7}");

        tester.execute();

        tester.verify(0, "{}");
        tester.verify(1, "{\"b\":\"123\"}");
        tester.verify(2, "{\"b\":\"123\"}");
        tester.verify(3, "{\"b\":123}");
        tester.verify(4, "{\"b\":{}, \"c\":7}");
    }
}

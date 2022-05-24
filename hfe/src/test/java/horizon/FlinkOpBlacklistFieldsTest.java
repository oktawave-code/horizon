package horizon;

import org.junit.Test;

public class FlinkOpBlacklistFieldsTest extends FlinkOperationTestBase {

    @Test
    public void testFields() throws Exception {
        Tester tester = new Tester(new FlinkOpBlacklistFields());

        tester.property("removedFields", "a,b,c");

        tester.packet("{}");
        tester.packet("{\"x\":\"123\"}");
        tester.packet("{\"a\":\"123\", \"x\":\"123\"}");
        tester.packet("{\"b\":\"123\", \"c\":\"123\"}");

        tester.execute();

        tester.verify(0, "{}");
        tester.verify(1, "{\"x\":\"123\"}");
        tester.verify(2, "{\"x\":\"123\"}");
        tester.verify(3, "{}");
    }
}


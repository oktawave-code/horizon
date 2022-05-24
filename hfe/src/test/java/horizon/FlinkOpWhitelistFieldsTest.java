package horizon;

import org.junit.Test;

public class FlinkOpWhitelistFieldsTest extends FlinkOperationTestBase {

    @Test
    public void testFields() throws Exception {
        Tester tester = new Tester(new FlinkOpWhitelistFields());

        tester.property("passedFields", "a,b,c");

        tester.packet("{}");
        tester.packet("{\"x\":\"123\"}");
        tester.packet("{\"a\":\"123\", \"x\":\"123\"}");
        tester.packet("{\"b\":\"123\", \"c\":\"123\"}");

        tester.execute();

        tester.verify(0, "{}");
        tester.verify(1, "{}");
        tester.verify(2, "{\"a\":\"123\"}");
        tester.verify(3, "{\"b\":\"123\", \"c\":\"123\"}");
    }
}

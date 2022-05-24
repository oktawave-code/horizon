package horizon;

import org.junit.Test;

public class FlinkOpAddConstTest extends FlinkOperationTestBase {

    @Test
    public void testFields() throws Exception {
        Tester tester = new Tester(new FlinkOpAddConst());

        tester.property("outputField", "c");
        tester.property("constValue", "ccc");

        tester.packet("{}");
        tester.packet("{\"a\":\"123\"}");
        tester.packet("{\"c\":123}");

        tester.execute();

        tester.verify(0, "{\"c\":\"ccc\"}");
        tester.verify(1, "{\"a\":\"123\", \"c\":\"ccc\"}");
        tester.verify(2, "{\"c\":\"ccc\"}");
    }
}

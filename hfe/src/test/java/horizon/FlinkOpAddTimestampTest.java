package horizon;

import org.junit.Test;
import static org.junit.Assert.assertTrue;

public class FlinkOpAddTimestampTest extends FlinkOperationTestBase {

    @Test
    public void testFields() throws Exception {
        Tester tester = new Tester(new FlinkOpAddTimestamp());

        tester.property("outputField", "ts");

        tester.packet("{}");
        tester.packet("{\"value\":\"123\"}");
        tester.packet("{\"ts\":\"123\"}");

        long t0 = System.currentTimeMillis();
        tester.execute();
        long t1 = System.currentTimeMillis();

        long t = tester.getResultField(0, "ts").asLong();
        assertTrue((t>=t0) && (t<=t1));
        t = tester.getResultField(1, "ts").asLong();
        assertTrue((t>=t0) && (t<=t1));
        t = tester.getResultField(2, "ts").asLong();
        assertTrue((t>=t0) && (t<=t1));
    }
}

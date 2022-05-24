package horizon;

import org.junit.Test;

public class FlinkOpCountTest extends FlinkOperationTestBase {

    @Test
    public void countSuccessful() throws Exception {
        Tester tester = new Tester(new FlinkOpCount());

        tester.property("time", (double)1);
        tester.property("outputField", "processedValue");

        tester.packet("{}",300);
        tester.packet("{\"value\":\"123\"}",800);
        tester.packet("{}",1200);
        tester.packet("{\"test\":1}",2000);
        tester.packet("{\"a\":\"a\", \"b\":7}",2999);
        tester.packet("{}",3000);
        tester.packet("{}",8000);

        tester.execute();

        tester.verify(0, "{\"processedValue\":2}");
        tester.verify(1, "{\"processedValue\":1}");
        tester.verify(2, "{\"processedValue\":2}");
        tester.verify(3, "{\"processedValue\":1}");
        tester.verify(4, "{\"processedValue\":1}");
    }
}

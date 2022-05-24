package horizon;

import org.junit.Test;

public class FlinkOpStringWordCountTest extends FlinkOperationTestBase {

    @Test
    public void countSuccessful() throws Exception {
        Tester tester = new Tester(new FlinkOpStringWordCount());

        tester.property("inputField", "value");
        tester.property("word", "test");
        tester.property("outputField", "processedValue");

        tester.packet("{\"value\":\"\"}");
        tester.packet("{\"value\":\"This is test\"}");
        tester.packet("{\"value\":\"This is test test\"}");

        tester.execute();

        tester.verify(0, "{\"processedValue\":0}");
        tester.verify(1, "{\"processedValue\":1}");
        tester.verify(2, "{\"processedValue\":2}");
    }
}

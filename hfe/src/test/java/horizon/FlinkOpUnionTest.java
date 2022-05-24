package horizon;

import org.junit.Test;

public class FlinkOpUnionTest extends FlinkOperationTestBase {

    @Test
    public void testUnionA() throws Exception {
        Tester tester = new Tester(new FlinkOpUnion());

        tester.packet(0, "{\"s\":\"a\"}");

        tester.execute();

        tester.verify(0, "{\"s\":\"a\"}");
    }

    @Test
    public void testUnionB() throws Exception {
        Tester tester = new Tester(new FlinkOpUnion());

        tester.packet(1, "{\"s\":\"b\"}");

        tester.execute();

        tester.verify(0, "{\"s\":\"b\"}");
    }

    @Test
    public void testUnionBoth() throws Exception {
        Tester tester = new Tester(new FlinkOpUnion());

        tester.packet(0, "{\"s\":\"x\"}");
        tester.packet(1, "{\"s\":\"x\"}");

        tester.execute();

        tester.verify(0, "{\"s\":\"x\"}");
        tester.verify(1, "{\"s\":\"x\"}");
    }
}

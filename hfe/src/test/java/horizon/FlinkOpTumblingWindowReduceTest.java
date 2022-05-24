package horizon;

import org.junit.Test;

public class FlinkOpTumblingWindowReduceTest extends FlinkOperationTestBase {

    @Test
    public void testNop() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowReduce());

        tester.property("time", (double)1);
        tester.property("field", "v");
        tester.property("operation", "Sum");

        tester.packet("{}", 1000);

        tester.packet("{\"v\":\"\"}", 2000);

        tester.packet("{\"v\":{}}", 3000);

        tester.execute();

        tester.verify(0, "{}");
        tester.verify(1, "{\"v\":\"\"}");
        tester.verify(2, "{\"v\":{}}");
    }

    @Test
    public void testSum() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowReduce());

        tester.property("time", (double)1);
        tester.property("field", "v");
        tester.property("operation", "Sum");

        tester.packet("{\"v\":1}", 1000);

        tester.packet("{\"v\":1}", 2000);
        tester.packet("{\"v\":2}", 2001);
        tester.packet("{\"v\":3}", 2002);

        tester.execute();

        tester.verify(0, "{\"v\":1}");
        tester.verify(1, "{\"v\":6}");
    }

    @Test
    public void testMax() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowReduce());

        tester.property("time", (double)1);
        tester.property("field", "v");
        tester.property("operation", "Max");

        tester.packet("{\"v\":1}", 1000);

        tester.packet("{\"v\":1}", 2000);
        tester.packet("{\"v\":2}", 2001);
        tester.packet("{\"v\":3}", 2002);

        tester.execute();

        tester.verify(0, "{\"v\":1}");
        tester.verify(1, "{\"v\":3}");
    }

    @Test
    public void testMin() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowReduce());

        tester.property("time", (double)1);
        tester.property("field", "v");
        tester.property("operation", "Min");

        tester.packet("{\"v\":1}", 1000);

        tester.packet("{\"v\":1}", 2000);
        tester.packet("{\"v\":2}", 2001);
        tester.packet("{\"v\":3}", 2002);

        tester.execute();

        tester.verify(0, "{\"v\":1}");
        tester.verify(1, "{\"v\":1}");
    }

    @Test
    public void testErr() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowReduce());

        tester.property("time", (double)1);
        tester.property("field", "v");
        tester.property("operation", "Min");

        tester.packet("{\"v\":1}", 1000);
        tester.packet("{}", 1001);

        tester.packet("{\"v\":{}}", 2000);
        tester.packet("{\"v\":1}", 2001);

        tester.execute();

        tester.verify(0, "{\"v\":0}");
        tester.verify(1, "{\"v\":0}");
    }
}

package horizon;

import org.junit.Test;

public class FlinkOpTumblingWindowAverageTest extends FlinkOperationTestBase {

    @Test
    public void testInvalid() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowAverage());

        tester.property("time", 1);
        tester.property("averagedField", "v");
        tester.property("weightField", "w");
        tester.property("outputField", "out");

        tester.packet("{}", 1000);

        tester.packet("{\"v\":\"\"}", 2000);

        tester.packet("{\"v\":{}}", 3000);

        tester.packet("{\"v\":1, \"w\":\"bob\"}", 4000);

        tester.packet("{\"v\":5, \"w\":0}", 5000);

        tester.packet("{\"v\":5, \"w\":1}", 6000);
        tester.packet("{\"v\":5, \"w\":-1}", 6001);

        tester.execute();

        tester.verify(0, "{\"out\":\"NaN\"}");
        tester.verify(1, "{\"out\":0.0}");
        tester.verify(2, "{\"out\":0.0}");
        tester.verify(3, "{\"out\":\"NaN\"}");
        tester.verify(4, "{\"out\":\"NaN\"}");
        tester.verify(5, "{\"out\":\"NaN\"}");
    }

    @Test
    public void testAvg() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowAverage());

        tester.property("time", 1);
        tester.property("averagedField", "v");
        tester.property("weightField", "w");
        tester.property("outputField", "out");

        tester.packet("{\"v\":1}", 1000);

        tester.packet("{\"v\":2, \"q\":7}", 2000);
        tester.packet("{\"q\":8}", 2001);

        tester.packet("{\"v\":3}", 3000);
        tester.packet("{\"v\":5}", 3001);

        tester.execute();

        tester.verify(0, "{\"out\":1.0}");
        tester.verify(1, "{\"out\":2.0}");
        tester.verify(2, "{\"out\":4.0}");
    }

    @Test
    public void testWeightAvg() throws Exception {
        Tester tester = new Tester(new FlinkOpTumblingWindowAverage());

        tester.property("time", 1);
        tester.property("averagedField", "v");
        tester.property("weightField", "w");
        tester.property("outputField", "out");

        tester.packet("{\"v\":1, \"w\":5}", 1000);

        tester.packet("{\"v\":1, \"w\":2}", 2000);
        tester.packet("{\"v\":4}", 2001);

        tester.packet("{\"v\":13, \"w\":1}", 3000);
        tester.packet("{\"v\":2, \"w\":10}", 3001);

        tester.packet("{\"v\":7, \"w\":1}", 4000);
        tester.packet("{\"v\":2, \"w\":0}", 4001);

        tester.execute();

        tester.verify(0, "{\"out\":1.0}");
        tester.verify(1, "{\"out\":2.0}");
        tester.verify(2, "{\"out\":3.0}");
        tester.verify(3, "{\"out\":7.0}");
    }

}

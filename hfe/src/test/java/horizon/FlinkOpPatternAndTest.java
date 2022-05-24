package horizon;

import org.junit.Test;

public class FlinkOpPatternAndTest extends FlinkOperationTestBase {

    @Test
    public void testOrder() throws Exception {
        Tester tester = new Tester(new FlinkOpPatternAnd());

        tester.property("time", (double)1);
        tester.property("leftMappings", "");
        tester.property("rightMappings", "");

        tester.packet(0, "{\"s1\":\"1\", \"s\":\"1\"}", 1);
        tester.packet(1, "{\"s2\":\"2\", \"s\":\"2\"}", 2);

        tester.packet(0, "{\"s1\":\"1\", \"s\":\"1\"}", 1002);
        tester.packet(1, "{\"s2\":\"2\", \"s\":\"2\"}", 1001);

        tester.packet(1, "{\"s1\":\"1\", \"s\":\"1\"}", 2002);
        tester.packet(0, "{\"s2\":\"2\", \"s\":\"2\"}", 2001);

        tester.execute();

        tester.verify(0, "{\"s\":\"2\", \"s1\":\"1\", \"s2\":\"2\"}");
        tester.verify(1, "{\"s\":\"2\", \"s1\":\"1\", \"s2\":\"2\"}");
        tester.verify(2, "{\"s\":\"1\", \"s1\":\"1\", \"s2\":\"2\"}");
    }

    @Test
    public void testNonMatching() throws Exception {
        Tester tester = new Tester(new FlinkOpPatternAnd());

        tester.property("time", (double)1);
        tester.property("leftMappings", "a");
        tester.property("rightMappings", "b");

        tester.packet(0, "{\"a\":1, \"t\":1000}", 1001);
        tester.packet(1, "{\"s\":\"2\", \"t\":1000}", 1002);

        tester.packet(0, "{\"a\":1, \"t\":2000}", 2001);
        tester.packet(1, "{\"a\":1, \"t\":2000}", 2002);

        tester.packet(0, "{\"b\":7, \"t\":3000}", 3001);
        tester.packet(1, "{\"b\":1, \"t\":3000}", 3002);

        tester.packet(0, "{\"a\":7, \"t\":4000}", 4001);
        tester.packet(1, "{\"b\":1, \"t\":4000}", 4002);

        tester.execute();

        tester.checkResultsCount(0);
    }

    @Test
    public void testMatching() throws Exception {
        Tester tester = new Tester(new FlinkOpPatternAnd());

        tester.property("time", (double)1);
        tester.property("leftMappings", "a");
        tester.property("rightMappings", "b");

        tester.packet(0, "{\"a\":4, \"t\":1000}", 1001);
        tester.packet(1, "{\"b\":4, \"t\":1000}", 1002);

        tester.packet(0, "{\"b\":7, \"t\":2000}", 2001);
        tester.packet(1, "{\"a\":7, \"t\":2000}", 2002);

        tester.packet(0, "{\"a\":\"3\", \"t\":3000}", 3001);
        tester.packet(1, "{\"b\":3, \"t\":3000}", 3002);

        tester.packet(0, "{\"t\":4000}", 4001);
        tester.packet(1, "{\"t\":4000}", 4002);

        tester.packet(0, "{\"a\":\"\", \"t\":5000}", 5001); // not well defined case
        tester.packet(1, "{\"t\":5000}", 5002);

        tester.execute();

        tester.verify(0, "{\"a\":4, \"b\":4, \"t\":1000}");
        tester.verify(1, "{\"a\":7, \"b\":7, \"t\":2000}");
        tester.verify(2, "{\"a\":\"3\", \"b\":3, \"t\":3000}");
        tester.verify(3, "{\"t\":4000}");
        tester.verify(4, "{\"a\":\"\", \"t\":5000}");
    }

    @Test
    public void testMulti() throws Exception {
        Tester tester = new Tester(new FlinkOpPatternAnd());

        tester.property("time", (double)1);
        tester.property("leftMappings", "a");
        tester.property("rightMappings", "b");

        tester.packet(0, "{\"a\":4, \"x\":0, \"t\":1000}", 1001);
        tester.packet(1, "{\"b\":4, \"y\":0, \"t\":1000}", 1002);
        tester.packet(1, "{\"b\":4, \"y\":1, \"t\":1000}", 1003);

        tester.packet(0, "{\"a\":4, \"x\":0, \"t\":2000}", 2001);
        tester.packet(0, "{\"a\":4, \"x\":1, \"t\":2000}", 2002);
        tester.packet(1, "{\"b\":4, \"y\":0, \"t\":2000}", 2003);

        tester.packet(0, "{\"a\":4, \"x\":0, \"t\":3000}", 3001);
        tester.packet(0, "{\"a\":4, \"x\":1, \"t\":3000}", 3002);
        tester.packet(1, "{\"b\":4, \"y\":0, \"t\":3000}", 3003);
        tester.packet(1, "{\"b\":4, \"y\":1, \"t\":3000}", 3004);

        tester.execute();

        tester.verify(0, "{\"a\":4, \"b\":4, \"t\":1000, \"x\":0, \"y\":0}");
        tester.verify(1, "{\"a\":4, \"b\":4, \"t\":1000, \"x\":0, \"y\":1}");

        tester.verify(2, "{\"a\":4, \"b\":4, \"t\":2000, \"x\":0, \"y\":0}");
        tester.verify(3, "{\"a\":4, \"b\":4, \"t\":2000, \"x\":1, \"y\":0}");

        tester.verify(4, "{\"a\":4, \"b\":4, \"t\":3000, \"x\":0, \"y\":0}");
        tester.verify(5, "{\"a\":4, \"b\":4, \"t\":3000, \"x\":0, \"y\":1}");
        tester.verify(6, "{\"a\":4, \"b\":4, \"t\":3000, \"x\":1, \"y\":0}");
        tester.verify(7, "{\"a\":4, \"b\":4, \"t\":3000, \"x\":1, \"y\":1}");
    }

    @Test
    public void testStitch() throws Exception {
        Tester tester = new Tester(new FlinkOpPatternAnd());

        tester.property("time", (double)1);
        tester.property("leftMappings", "a,b");
        tester.property("rightMappings", "c,d");

        tester.packet(0, "{\"a\":1, \"b\":2, \"t\":1000}", 1001);
        tester.packet(1, "{\"c\":1, \"d\":2, \"t\":1000}", 1002);

        tester.packet(0, "{\"a\":1, \"b\":\"2\", \"t\":2000}", 2001);
        tester.packet(1, "{\"c\":1, \"d\":2, \"t\":2000}", 2002);

        tester.packet(0, "{\"a\":12, \"t\":3000}", 3001);
        tester.packet(1, "{\"c\":1, \"d\":2, \"t\":3000}", 3002);

        tester.packet(0, "{\"a\":12, \"t\":4000}", 4001);
        tester.packet(1, "{\"d\":\"12\", \"t\":4000}", 4002);

        tester.execute();

        tester.verify(0, "{\"a\":1, \"b\":2, \"c\":1, \"d\":2, \"t\":1000}");
        tester.verify(1, "{\"a\":1, \"b\":\"2\", \"c\":1, \"d\":2, \"t\":2000}");
        tester.verify(2, "{\"a\":12, \"c\":1, \"d\":2, \"t\":3000}");
        tester.verify(3, "{\"a\":12, \"d\":\"12\", \"t\":4000}");
    }
}

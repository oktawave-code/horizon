package horizon;

import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.MapperFeature;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.SinkFunction;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.junit.Before;
import org.junit.BeforeClass;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import static org.junit.Assert.*;

public class FlinkOperationTestBase {

    static StreamExecutionEnvironment env;

    @BeforeClass
    public static void setUpClass() {
        env = StreamExecutionEnvironment.getExecutionEnvironment();

        // configure your test environment
        env.setParallelism(1);
    }

    @Before
    public void setUp() {
        // values are collected in a static variable
        FlinkOpStringWordCountTest.CollectSink.values.clear();
    }

    // create a testing sink
    static class CollectSink implements SinkFunction<ObjectNode> {

        // must be static
        public static final List<ObjectNode> values = new ArrayList<>();

        @Override
        public synchronized void invoke(ObjectNode value) throws Exception {
            values.add(value);
        }
    }

    public static ObjectNode buildPacket(String message) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode json = mapper.readTree(message);
        return (ObjectNode)json;
    }

    class TestSourceFunction implements SourceFunction<ObjectNode> {

        private final List<String> items;
        private final List<Long> times;

        TestSourceFunction() {
            this.items = new ArrayList<>();
            this.times = new ArrayList<>();
        }

        public void packet(String json, long time) {
            this.items.add(json);
            this.times.add(time);
        }

        @Override
        public void run(SourceContext<ObjectNode> sourceContext) throws Exception {
            for (int i=0; i<items.size(); i++) {
                sourceContext.collectWithTimestamp(buildPacket(items.get(i)), times.get(i));
            }
        }

        @Override
        public void cancel() {}
    }

    class Tester {

        private final List<TestSourceFunction> src;
        private final FlinkOp program;
        private final HashMap<String, Object> properties;
        private long lastTime;

        Tester(FlinkOp program) {
            this.program = program;
            int inputsCnt = program.getDef().requiredStreams.size();
            properties = new HashMap<>();
            src = new ArrayList<>();
            for (int i=0; i<inputsCnt; i++) {
                src.add(new TestSourceFunction());
            }
            lastTime = 7;
        }

        public void property(String key, String value) {
            properties.put(key, value);
        }

        public void property(String key, int value) {
            properties.put(key, value);
        }

        public void property(String key, double value) {
            properties.put(key, value);
        }

        public void packet(String json, long time) {
            packet(0, json, time);
        }

        public void packet(String json) {
            packet(0, json);
        }

        public void packet(int inputStreamNr, String json, long time) {
            lastTime = time;
            src.get(inputStreamNr).packet(json, time);
        }

        public void packet(int inputStreamNr, String json) {
            lastTime += 1;
            src.get(inputStreamNr).packet(json, lastTime);
        }

        public void execute() throws Exception {
            env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
            ArrayList<DataStream<ObjectNode>> inputs = new ArrayList<>();
            for (TestSourceFunction input : src) {
                DataStream<ObjectNode> stream = env.addSource(input);
                inputs.add(stream);
            }

            program.build(env, inputs, properties)
                    .addSink(new CollectSink());

            env.execute();
        }

        public JsonNode getResultField(int index, String field) throws Exception {
            ObjectNode node = CollectSink.values.get(index);
            assertTrue(node.has(field));
            return node.get(field);
        }

        public void checkResultsCount(int cnt) throws Exception {
            assertEquals(cnt, CollectSink.values.size());
        }

        public void verify(int index, String json) throws Exception {
            ObjectMapper mapper = new ObjectMapper();
            mapper.configure(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY, true);
            mapper.configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true);
            String actual = mapper.writeValueAsString(mapper.treeToValue(CollectSink.values.get(index), Object.class));
            String expected = mapper.writeValueAsString(mapper.treeToValue(buildPacket(json), Object.class));
            assertEquals(expected, actual);
        }

        public void dumpResults() throws Exception {
            ObjectMapper mapper = new ObjectMapper();
            mapper.configure(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY, true);
            mapper.configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true);
            for (ObjectNode node : CollectSink.values) {
                final Object obj = mapper.treeToValue(node, Object.class);
                System.out.println(mapper.writeValueAsString(obj));
            }
        }
    }

}

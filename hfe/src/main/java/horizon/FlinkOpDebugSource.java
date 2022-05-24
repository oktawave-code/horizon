package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.stream.IntStream;
import java.util.stream.Stream;

@FlinkOperation
public class FlinkOpDebugSource extends FlinkOp {


    class DebugSourceFunction implements SourceFunction<ObjectNode> {

        private volatile boolean isRunning = true;
        private int count;
        private String line;
        private String outputField;

        DebugSourceFunction(int count, String line, String outputField) {
            this.count = count;
            this.line = line;
            this.outputField = outputField;
        }

        @Override
        public void run(SourceContext<ObjectNode> sourceContext) throws Exception {
            try (Stream<String> stream = getStream()) {
                final ObjectMapper mapper = new ObjectMapper();
                Iterator<String> iterator = stream.iterator();
                while (isRunning && iterator.hasNext()) {
                    ObjectNode element = mapper.createObjectNode();
                    element.put(outputField, iterator.next());
                    sourceContext.collect(element);
                }
            }
        }

        @Override
        public void cancel() {
            isRunning = false;
        }

        private Stream<String> getStream() {
            return IntStream.range(1, count).mapToObj(n -> n + " " + line);
        }
    }

    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        DataStream<ObjectNode> stream = env.addSource(new DebugSourceFunction((int) ((double)properties.get("count")), (String) properties.get("line"), (String) properties.get("outputField")));
        return stream;
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeSource(
                "debugSource",
                "Debug source",
                "Data source, repeating predefined text line");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "line",
                "Line",
                "Line to generate"));
        def.staticProperties.add(ElementDefStaticProperty.makeInt(
                "count",
                "Count",
                "How many times line will be repeated",
                1,
                1000));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "outputField",
                "Output field",
                "Field name for generated lines"));

        return def;
    }
}

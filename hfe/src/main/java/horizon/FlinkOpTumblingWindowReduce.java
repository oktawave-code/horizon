package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows ;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpTumblingWindowReduce extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
//            String key = (String)fNode.getProperty("key");
        final String operation = (String) properties.get("operation");
        final int time = (int) ((double)properties.get("time"));
        final String field = (String) properties.get("field");
        return inputStreams.get(0)
                .windowAll(TumblingEventTimeWindows.of(Time.seconds(time)))
                .reduce(new ReduceFunction<ObjectNode>() {
                    public ObjectNode reduce(ObjectNode v1, ObjectNode v2) {
                        long v1val = 0;
                        long v2val = 0;
                        JsonNode jsonNode1 = v1.get(field);
                        JsonNode jsonNode2 = v2.get(field);
                        if (jsonNode1!=null) {
                            v1val = jsonNode1.asLong();
                        }
                        if (jsonNode2!=null) {
                            v2val = jsonNode2.asLong();
                        }
                        switch (operation) {
                            case "Sum":
                                v1.put(field, v1val + v2val);
                                break;
                            case "Max":
                                v1.put(field, Long.max(v1val, v2val));
                                break;
                            case "Min":
                                v1.put(field, Long.min(v1val, v2val));
                                break;
                        }
                        return v1;
                    }
                });
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "tumblingWindowsReduce",
                "Tumbling windows reduce",
                "Partition stream into tumbling windows and reduce it by using selected operation",
                "PROCESS");

        /*
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "key",
                "Key",
                "Key to partition input stream"));
*/
        def.staticProperties.add(ElementDefStaticProperty.makeInt(
                "time",
                "Time",
                "Time window size",
                1,
                3600));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "field",
                "Field",
                "Field to aggregate"));
        def.staticProperties.add(ElementDefStaticProperty.makeOptions(
                "operation",
                "Operation",
                "Operation to use on reduced values",
                Arrays.asList("Sum", "Max", "Min")));

        return def;
    }
}

package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpCount extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final int time = (int) ((double)properties.get("time"));
        final String outputField = (String) properties.get("outputField");
        final ObjectMapper mapper = new ObjectMapper();
        return inputStreams.get(0)
                .windowAll(TumblingEventTimeWindows.of(Time.seconds(time)))
                .aggregate(new AggregateFunction<ObjectNode, Long, ObjectNode>() {
                    @Override
                    public Long createAccumulator() {
                        return new Long(0);
                    }

                    @Override
                    public Long add(ObjectNode jsonNodes, Long acc) {
                        return acc + 1;
                    }

                    @Override
                    public ObjectNode getResult(Long l) {
                        ObjectNode result = mapper.createObjectNode();
                        result.put(outputField, l);
                        return result;
                    }

                    @Override
                    public Long merge(Long a, Long b) {
                        return a + b;
                    }
                });
    }


    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "count",
                "Events counter",
                "Count events in every time window",
                "PROCESS");

        def.staticProperties.add(ElementDefStaticProperty.makeInt(
                "time",
                "Time",
                "Time window size",
                1,
                3600));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "outputField",
                "Output field",
                "Field name for generated counter"));

        return def;
    }
}

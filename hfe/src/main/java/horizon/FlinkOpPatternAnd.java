package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.JoinFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

@FlinkOperation
public class FlinkOpPatternAnd extends FlinkOp {

    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final List<String> leftMappings = Arrays.asList(((String)properties.get("leftMappings")).split(","));
        final List<String> rightMappings = Arrays.asList(((String)properties.get("rightMappings")).split(","));
        final int time = (int) ((double)properties.get("time"));
        final ObjectMapper mapper = new ObjectMapper();
        return inputStreams.get(0).join(inputStreams.get(1))
                .where(new KeySelector<ObjectNode, String>() {
                    @Override
                    public String getKey(ObjectNode value) throws Exception {
                        StringBuilder builder = new StringBuilder();
                        for (String key : leftMappings) {
                            JsonNode node = value.get(key);
                            if (node!=null) {
                                builder.append(node.asText());
                            }
                        }
                        return builder.toString();
                    }
                })
                .equalTo(new KeySelector<ObjectNode, String>() {
                    @Override
                    public String getKey(ObjectNode value) throws Exception {
                        StringBuilder builder = new StringBuilder();
                        for (String key : rightMappings) {
                            JsonNode node = value.get(key);
                            if (node!=null) {
                                builder.append(node.asText());
                            }
                        }
                        return builder.toString();
                    }
                })
                .window(TumblingEventTimeWindows.of(Time.seconds(time)))
                .apply(new JoinFunction<ObjectNode, ObjectNode, ObjectNode>() {
                    @Override
                    public ObjectNode join(ObjectNode e1, ObjectNode e2) throws Exception {
                        ObjectNode result = mapper.createObjectNode();
                        result.setAll(e1);
                        result.setAll(e2);
                        return result;
                    }
                });

    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "patternAnd",
                "Pattern detection - and",
                "Detects whether an event co-occurs with another event within a given time.",
                "PATTERNS",
                2);

        def.staticProperties.add(ElementDefStaticProperty.makeInt(
                "time",
                "Time",
                "Time window size (seconds)",
                1,
                3600));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "leftMappings",
                "Left Mappings",
                ""));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "rightMappings",
                "Right Mappings",
                ""));

        return def;
    }
}

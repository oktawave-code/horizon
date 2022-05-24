package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import java.util.ArrayList;
import java.util.HashMap;

class AverageAccumulator {
    long count = 0;
    double sum = 0;
}

class Aggregator implements AggregateFunction<ObjectNode, AverageAccumulator, ObjectNode> {
    private String averagedField;
    private String weightField;
    private String outputField;
    private ObjectMapper mapper;

    Aggregator(HashMap<String, Object> properties) {
        mapper = new ObjectMapper();
        averagedField = (String) properties.get("averagedField");
        weightField = (String) properties.get("weightField");
        outputField = (String) properties.get("outputField");
    }

    @Override
    public AverageAccumulator createAccumulator() {
        return new AverageAccumulator();
    }

    @Override
    public AverageAccumulator add(ObjectNode jsonNodes, AverageAccumulator acc) {
        double weight = 1;
        if (!weightField.equals("")) {
            JsonNode jsonNode = jsonNodes.get(weightField);
            if (jsonNode != null) {
                weight = jsonNode.asDouble();
            }
        }
        JsonNode jsonNode = jsonNodes.get(averagedField);
        if (jsonNode!=null) {
            acc.sum += jsonNode.asDouble()*weight;
            acc.count += weight;
        }
        return acc;
    }

    @Override
    public ObjectNode getResult(AverageAccumulator acc) {
        ObjectNode result = mapper.createObjectNode();
        result.put(outputField, acc.sum / (double) acc.count);
        return result;
    }

    @Override
    public AverageAccumulator merge(AverageAccumulator a, AverageAccumulator b) {
        a.count += b.count;
        a.sum += b.sum;
        return a;
    }
}

@FlinkOperation
public class FlinkOpTumblingWindowAverage extends FlinkOp {
    
    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final int time = (Integer) properties.get("time");
        return inputStreams.get(0)
                .windowAll(TumblingEventTimeWindows.of(Time.seconds(time)))
                .aggregate(new Aggregator(properties));
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "tumblingWindowsAverage",
                "Tumbling windows average",
                "Partition stream into tumbling windows and reduce it by averaging",
                "PROCESS");

        def.staticProperties.add(ElementDefStaticProperty.makeInt(
                "time",
                "Time",
                "Time window size",
                1,
                3600));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "averagedField",
                "Averaged field",
                "Field to average"));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "weightField",
                "Weight field",
                "Field with weight of averaged values. Leave empty for uniform weight of 1"));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "outputField",
                "Output field",
                "Field name for generated averages"));

        return def;
    }
}

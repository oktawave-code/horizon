package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.util.Collector;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpRequireFields extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final String[] requiredFields = ((String) properties.get("requiredFields")).split(",");
        return inputStreams.get(0).flatMap(new FlatMapFunction<ObjectNode, ObjectNode>() {
            @Override
            public void flatMap(ObjectNode value, Collector<ObjectNode> out) {
                for (String field : requiredFields) {
                    if (!value.has(field)) {
                        return;
                    }
                }
                out.collect(value);
            }
        });
    }


    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "requireFields",
                "Require fields",
                "Pass only records having all required fields",
                "FILTER");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "requiredFields",
                "Required fields",
                "Comma separated list of fields that must be present in all passed stream records"));

        return def;
    }
}

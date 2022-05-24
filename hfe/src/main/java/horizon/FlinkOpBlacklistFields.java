package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpBlacklistFields extends FlinkOp {

    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final String[] removedFields = ((String) properties.get("removedFields")).split(",");
        return inputStreams.get(0).map(new MapFunction<ObjectNode, ObjectNode>() {
            @Override
            public ObjectNode map(ObjectNode value) {
                for (String field : removedFields) {
                    if (value.has(field)) {
                        value.remove(field);
                    }
                }
                return value;
            }
        });
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "blacklistFields",
                "Blacklist fields",
                "Pass all fields except blacklisted ones",
                "TRANSFORM");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "removedFields",
                "Removed fields",
                "Comma separated list of fields that will be removed from output"));

        return def;
    }
}

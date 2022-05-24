package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpRenameField extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final String inputField = (String) properties.get("inputField");
        final String outputField = (String) properties.get("outputField");
        return inputStreams.get(0).map(new MapFunction<ObjectNode, ObjectNode>() {
            @Override
            public ObjectNode map(ObjectNode value) {
                JsonNode jsonNode = value.get(inputField);
                if (jsonNode!=null) {
                    value.replace(outputField, jsonNode);
                    value.remove(inputField);
                }
                return value;
            }
        });
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "renameField",
                "Rename field",
                "Rename field in each passing record. Do nothing if it was not in input data",
                "TRANSFORM");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "inputField",
                "Input field",
                "Source field name"));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "outputField",
                "Output field",
                "Target field name"));

        return def;
    }
}

package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpStringTransform extends FlinkOp {

    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final String inputField = (String) properties.get("inputField");
        final String operation = (String) properties.get("operation");
        return inputStreams.get(0).map(new MapFunction<ObjectNode, ObjectNode>() {
            @Override
            public ObjectNode map(ObjectNode value) {
                JsonNode jsonNode = value.get(inputField);
                if (jsonNode!=null) {
                    String src = jsonNode.asText();
                    switch (operation) {
                        case "Capitalize":
                            value.put(inputField, src.substring(0, 1).toUpperCase() + src.substring(1).toLowerCase());
                            break;
                        case "Uppercase":
                            value.put(inputField, src.toUpperCase());
                            break;
                        case "Lowercase":
                            value.put(inputField, src.toLowerCase());
                            break;
                    }
                }
                return value;
            }
        });
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "stringTransform",
                "String transform",
                "Apply one of selected string operations to passing strings",
                "TRANSFORM");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "inputField",
                "Input field",
                "Field name where processed strings are"));
        def.staticProperties.add(ElementDefStaticProperty.makeOptions(
                "operation",
                "Operation",
                "Operation to use",
                Arrays.asList("Capitalize", "Uppercase", "Lowercase")));

        return def;
    }
}

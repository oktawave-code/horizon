package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpWhitelistFields extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final String[] passedFields = ((String) properties.get("passedFields")).split(",");
        final ObjectMapper mapper = new ObjectMapper();
        return inputStreams.get(0).map(new MapFunction<ObjectNode, ObjectNode>() {
            @Override
            public ObjectNode map(ObjectNode value) {
                ObjectNode element = mapper.createObjectNode();
                for (String field : passedFields) {
                    if (value.has(field)) {
                        element.replace(field, value.get(field));
                    }
                }
                return element;
            }
        });
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "whitelistFields",
                "Whitelist fields",
                "Pass only whitelisted fields",
                "TRANSFORM");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "passedFields",
                "Passed fields",
                "Comma separated list of fields that will be passed to output"));

        return def;
    }
}

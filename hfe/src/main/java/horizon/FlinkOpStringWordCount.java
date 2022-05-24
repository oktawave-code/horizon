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
public class FlinkOpStringWordCount extends FlinkOp {

    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final String inputField = (String) properties.get("inputField");
        final String searchedWord = (String) properties.get("word");
        final String outputField = (String) properties.get("outputField");
        final ObjectMapper mapper = new ObjectMapper();
        return inputStreams.get(0).map(new MapFunction<ObjectNode, ObjectNode>() {
            @Override
            public ObjectNode map(ObjectNode value) {
                int cnt = 0;
                for (String word : value.get(inputField).asText().split(" ")) {
                    if (word.equals(searchedWord)) {
                        cnt += 1;
                    }
                }
                ObjectNode element = mapper.createObjectNode();
                element.put(outputField, cnt);
                return element;
            }
        });
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "stringWordCount",
                "String word counter",
                "Count specific words in each incoming line",
                "PROCESS");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "inputField",
                "Input field",
                "Field name where counted words are"));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "word",
                "Word to count",
                "Exact word to look for and count"));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "outputField",
                "Output field",
                "Field name for generated counter"));

        return def;
    }
}

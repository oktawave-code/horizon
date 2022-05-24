package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpAddConst extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        final String outputField = (String) properties.get("outputField");
        final String constValue = (String) properties.get("constValue");
        return inputStreams.get(0).map(new MapFunction<ObjectNode, ObjectNode>() {
            @Override
            public ObjectNode map(ObjectNode value) {
                value.put(outputField, constValue);
                return value;
            }
        });
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "addConst",
                "Add constant field",
                "Add new field with constant value",
                "ENRICH");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "outputField",
                "Output field",
                "New field to add"));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "constValue",
                "Const value",
                "Constant value to use in every record"));

        return def;
    }
}

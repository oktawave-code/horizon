package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpNop extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        return inputStreams.get(0);
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "nop",
                "No operation",
                "Dummy operator, does nothing",
                "TRANSFORM");

        return def;
    }
}

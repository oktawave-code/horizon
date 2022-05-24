package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpUnion extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        return inputStreams.get(0).union(inputStreams.get(1));
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "union",
                "Union",
                "Union of two data streams creating a new stream containing all the elements from all the streams. Note: If you union a data stream with itself you will get each element twice in the resulting stream",
                "MERGE",
                2);

        return def;
    }
}

package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.HashMap;

@FlinkOperation
public class FlinkOpDebugPrinter extends FlinkOp {


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        DataStream<ObjectNode> stream = inputStreams.get(0);
        stream.print("Debug printer");
        return stream;
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeFilter(
                "debugPrint",
                "Debug printer",
                "Output stream data to process log",
                "TRANSFORM"
                );

        return def;
    }
}

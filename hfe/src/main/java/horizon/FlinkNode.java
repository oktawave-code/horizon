package horizon;

import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;

import java.util.ArrayList;
import java.util.HashMap;

public class FlinkNode {
    private FlinkBuilder builder;
    GraphNode node;
    private DataStream<ObjectNode> output;

    FlinkNode(FlinkBuilder builder, GraphNode node) {
        this.builder = builder;
        this.node = node;
        output = null;
    }

    public DataStream<ObjectNode> getInputStream(int nr) {
        FlinkNode fNode = builder.getNode(node.inputs.get(nr));
        return fNode.output;
    }

    public ArrayList<DataStream<ObjectNode>> getInputStreams() {
        ArrayList<DataStream<ObjectNode>> inputs = new ArrayList<>();
        for (String input : node.inputs) {
            inputs.add(builder.getNode(input).output);
        }
        return inputs;
    }

    void setOutput(DataStream<ObjectNode> output) {
        this.output = output;
    }

    DataStream<ObjectNode> getOutputStream() {
        return output;
    }

    public Object getProperty(String id) {
        return node.getStaticProperty(id);
    }

    public HashMap<String, Object> getProperties() {
        return node.staticProperties;
    }
}

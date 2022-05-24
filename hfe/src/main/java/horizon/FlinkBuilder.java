package horizon;

import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.HashMap;
import java.util.Map;

public class FlinkBuilder {

    private Map<String, FlinkOp> registeredOperators;
    private ElementDefs elementDefs;
    private Graph graph;
    private Map<String, FlinkNode> nodes;
    private StreamExecutionEnvironment env;

    public FlinkBuilder() {
        registeredOperators = new HashMap<>();
        elementDefs = new ElementDefs();
        graph = null;
    }

    public void registerOperator(FlinkOp operator) {
        ElementDef def = operator.getDef();
        registeredOperators.put(def.elementId, operator);
        elementDefs.add(def);
    }

    public void registerDefinition(ElementDef definition) {
        elementDefs.add(definition);
    }

    public ElementDefs getElementDefs() {
        return elementDefs;
    }

    FlinkNode getNode(String id) {
        return nodes.get(id);
    }

    public void useGraph(Graph graph) {
        this.graph = graph;
    }

    public void build() {
        System.out.printf("Building graph: %s\n", graph.graphName);
        nodes = new HashMap<>();
        env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        boolean noAction;
        do {
            noAction = true;
            for (GraphNode node : graph.nodes.values()) {
                if (!nodes.containsKey(node.id)) {
                    boolean leader = true;
                    for (String inputId : node.inputs) {
                        if (!nodes.containsKey(inputId)) {
                            leader = false;
                            break;
                        }
                    }
                    if (leader) {
                        System.out.printf(" %s \"%s\" (id:%s)\n", node.elementId, node.name, node.id);
                        FlinkOp operatorBuilder = registeredOperators.get(node.elementId);
                        FlinkNode fNode = new FlinkNode(this, node);
                        DataStream<ObjectNode> output = operatorBuilder.build(env, fNode.getInputStreams(), fNode.getProperties());
                        fNode.setOutput(output);
                        nodes.put(node.id, fNode);
                        noAction = false;
                    }
                }
            }
        } while (!noAction);
    }

    public void execute() throws Exception {
        System.out.println("Executing graph");
        env.execute(graph.graphName);
    }

}

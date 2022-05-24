package horizon;

import com.google.gson.*;

import java.util.*;

class GraphException extends RuntimeException {

    String message;

    GraphException(String msg) {
        message = msg;
    }

}

class GraphNode {

    String id;
    String name;
    String elementId;
    String category;
    HashMap<String, Object> staticProperties;
    ArrayList<String> inputs;
    ArrayList<String> outputs;

    GraphNode(String nodeId) {
        id = nodeId;
        inputs = new ArrayList<>();
        outputs = new ArrayList<>();
    }

    Object getStaticProperty(String elementId) {
        return staticProperties.get(elementId);
    }

}

class Graph {

    String graphName;
    Map<String, GraphNode> nodes;

    Graph(String jsonStr) throws horizon.GraphException {
        graphName = null;
        nodes = new HashMap<>();
        if (jsonStr == null) {
            throw new horizon.GraphException("Missing graph");
        }
        parse(jsonStr);
    }

    private void parse(String jsonStr) throws horizon.GraphException {
        JsonElement jsonElement;
        JsonObject jsonObject;

        // Parse JSON string, verify base objects
        try {
            jsonElement = new JsonParser().parse(jsonStr);
        } catch (JsonParseException e) {
            throw new horizon.GraphException("Invalid JSON string");
        }
        try {
            jsonObject = jsonElement.getAsJsonObject();
        } catch (IllegalStateException e) {
            throw new horizon.GraphException("JSON is valid, but not an object");
        }
        graphName = parseStr(jsonObject, "name", "");
        JsonArray graphArray = parseArray(jsonObject, "graph", "");

        // First graph pass - nodes only
        Set<String> checkedIds = new HashSet<>();
        int elemNr = 0;
        for (JsonElement elem : graphArray) {
            String path = String.format("graph[%d]", elemNr);
            try {
                jsonObject = elem.getAsJsonObject();
            } catch (IllegalStateException e) {
                throw new horizon.GraphException(String.format("\"%s\" is not an object", path));
            }
            if (!checkFlag(jsonObject, "edge", path)) {
                String id = parseStr(jsonObject, "id", path);
                if (checkedIds.contains(id)) {
                    throw new horizon.GraphException(String.format("\"%s.id\" is not unique: %s", path, id));
                }
                checkedIds.add(id);
                horizon.GraphNode node = new horizon.GraphNode(id);
                jsonObject = parseObj(jsonObject, "value", path);
                path = String.format("%s.%s", path, "value");
                node.name = parseStr(jsonObject, "name", path);
                node.elementId = parseStr(jsonObject, "elementId", path);
                node.category = parseStr(jsonObject, "category", path);
                node.staticProperties = new HashMap<>();
                JsonArray props = parseArray(jsonObject, "staticProperties", path);
                int propNr = 0;
                for (JsonElement propElem : props) {
                    String pPath = String.format("%s.staticProperties[%d]", path, propNr);
                    JsonObject propObj;
                    try {
                        propObj = propElem.getAsJsonObject();
                    } catch (IllegalStateException e) {
                        throw new horizon.GraphException(String.format("\"%s\" is not an object", pPath));
                    }
                    String elementId = parseStr(propObj, "elementId", pPath);
                    Object value = parseValueObject(propObj, "value", pPath);
                    node.staticProperties.put(elementId, value);
                    propNr += 1;
                }

                //...
                nodes.put(node.id, node);
            }
            elemNr += 1;
        }

        // Second graph pass - edges only
        elemNr = 0;
        for (JsonElement elem : graphArray) {
            String path = String.format("graph[%d]", elemNr);
            jsonObject = elem.getAsJsonObject();
            if (checkFlag(jsonObject, "edge", path)) {
                String source = parseStr(jsonObject, "source", path);
                String target = parseStr(jsonObject, "target", path);
                horizon.GraphNode sourceNode = nodes.get(source);
                if (sourceNode == null) {
                    throw new horizon.GraphException(String.format("\"%s.source\" points to unknown node id", path));
                }
                horizon.GraphNode targetNode = nodes.get(target);
                if (targetNode == null) {
                    throw new horizon.GraphException(String.format("\"%s.target\" points to unknown node id", path));
                }
                sourceNode.outputs.add(target);
                targetNode.inputs.add(source);
            }
            elemNr += 1;
        }

    }

    private static String parseStr(JsonObject obj, String property, String path) throws horizon.GraphException {
        String val;
        try {
            val = obj.get(property).getAsString();
        } catch (NullPointerException e) {
            throw new horizon.GraphException(String.format("Missing \"%s.%s\" property", path, property));
        } catch (ClassCastException | IllegalStateException | UnsupportedOperationException e) {
            throw new horizon.GraphException(String.format("\"%s.%s\" is not a string", path, property));
        }
        return val;
    }

    private static JsonObject parseObj(JsonObject obj, String property, String path) throws horizon.GraphException {
        JsonObject val;
        try {
            val = obj.get(property).getAsJsonObject();
        } catch (NullPointerException e) {
            throw new horizon.GraphException(String.format("Missing \"%s.%s\" property", path, property));
        } catch (ClassCastException | IllegalStateException | UnsupportedOperationException e) {
            throw new horizon.GraphException(String.format("\"%s.%s\" is not an object", path, property));
        }
        return val;
    }

    private static JsonArray parseArray(JsonObject obj, String property, String path) throws horizon.GraphException {
        JsonArray val;
        try {
            val = obj.get(property).getAsJsonArray();
        } catch (NullPointerException e) {
            throw new horizon.GraphException(String.format("Missing \"%s.%s\" property", path, property));
        } catch (ClassCastException | IllegalStateException | UnsupportedOperationException e) {
            throw new horizon.GraphException(String.format("\"%s.%s\" is not an array", path, property));
        }
        return val;
    }

    private static Object parseValueObject(JsonObject obj, String property, String path) throws horizon.GraphException {
        JsonElement elem = obj.get(property);
        if (elem == null) {
            throw new horizon.GraphException(String.format("Missing \"%s.%s\" property", path, property));
        }
        try {
            return elem.getAsDouble();
        } catch (ClassCastException | IllegalStateException | UnsupportedOperationException | NumberFormatException e2) {
            try {
                return elem.getAsString();
            } catch (ClassCastException | IllegalStateException | UnsupportedOperationException e3) {
                try {
                    return elem.getAsJsonArray();
                } catch (ClassCastException | IllegalStateException | UnsupportedOperationException e4) {
                    throw new horizon.GraphException(String.format("\"%s.%s\" is not a valid value type: %s", path, property, elem.toString()));
                }
            }
        }
    }

    private static boolean checkFlag(JsonObject obj, String property, String path) throws horizon.GraphException {
        boolean val;
        try {
            val = obj.get(property).getAsBoolean();
        } catch (NullPointerException e) {
            return false; // not found is the same as "false" in this case
        } catch (ClassCastException | IllegalStateException | UnsupportedOperationException e) {
            throw new horizon.GraphException(String.format("\"%s.%s\" is not a boolean", path, property));
        }
        return val;
    }

    void validate(ElementDefs elementDefs) throws horizon.GraphException {
        if (nodes.size() == 0) {
            throw new horizon.GraphException("Graph is empty");
        }
        // Check for graph cycles
        Set<String> allVisited;
        Queue<String> queue;
        Set<String> visited;
        allVisited = new HashSet<>();
        for (String id : nodes.keySet()) {
            if (!allVisited.contains(id)) {
                queue = new LinkedList<>();
                queue.add(id);
                visited = new HashSet<>();
                while (true) {
                    String qId = queue.poll();
                    if (qId == null) {
                        break; // no more nodes - entire subtree traversed
                    }
                    if (visited.contains(qId)) {
                        throw new horizon.GraphException(String.format("Node[%s]: Cycle detected", qId));
                    }
                    visited.add(qId);
                    allVisited.add(qId);
                    horizon.GraphNode n = nodes.get(qId);
                    queue.addAll(n.outputs);
                }
            }
        }
        // Validate elements
        for (horizon.GraphNode node : nodes.values()) {
            ElementDef elemDef = elementDefs.getDef(node.elementId);
            if (elemDef == null) {
                throw new horizon.GraphException(String.format("Node[%s]: Unknown elementId: %s", node.id, node.elementId));
            }
            Set<String> checked = new HashSet<>();
            for (Map.Entry<String, Object> prop : node.staticProperties.entrySet()) {
                if (checked.contains(prop.getKey())) {
                    throw new horizon.GraphException(String.format("Node[%s]: Duplicate static property: %s", node.id, prop.getKey()));
                }
                checked.add(prop.getKey());
                ElementDefStaticProperty propertyDef = elemDef.getStaticProperty(prop.getKey());
                if (propertyDef == null) {
                    throw new horizon.GraphException(String.format("Node[%s]: Unknown static property: %s", node.id, prop.getKey()));
                }
                switch (propertyDef.staticPropertyType) {
                    case "integer":
                        int vi;
                        try {
                            vi = (int) ((double) prop.getValue());
                        } catch (NumberFormatException | ClassCastException | NullPointerException e) {
                            throw new horizon.GraphException(String.format("Node[%s].staticProperty[%s]: Integer expected: %s", node.id, prop.getKey(), prop.getValue()));
                        }
                        if ((vi < propertyDef.minValue) || (vi > propertyDef.maxValue)) {
                            throw new horizon.GraphException(String.format("Node[%s].staticProperty[%s]: Value out of range: %s", node.id, prop.getKey(), prop.getValue()));
                        }
                        break;
                    case "float":
                        double vf;
                        try {
                            vf = (double) prop.getValue();
                        } catch (NumberFormatException | ClassCastException | NullPointerException e) {
                            throw new horizon.GraphException(String.format("Node[%s].staticProperty[%s]: Double expected: %s", node.id, prop.getKey(), prop.getValue()));
                        }
                        if ((vf < propertyDef.minValue) || (vf > propertyDef.maxValue)) {
                            throw new horizon.GraphException(String.format("Node[%s].staticProperty[%s]: Value out of range: %s", node.id, prop.getKey(), prop.getValue()));
                        }
                        break;
                    case "singleValueSelection":
                        String vs;
                        try {
                            vs = (String) prop.getValue();
                        } catch (ClassCastException | NullPointerException e) {
                            throw new horizon.GraphException(String.format("Node[%s].staticProperty[%s]: String expected: %s", node.id, prop.getKey(), prop.getValue()));
                        }
                        boolean found = false;
                        for (ElementDefStaticPropertyOptions opt : propertyDef.options) {
                            if (opt.internalName.equals(vs)) {
                                found = true;
                                break;
                            }
                        }
                        if (!found) {
                            throw new horizon.GraphException(String.format("Node[%s].staticProperty[%s]: Unknown option selected: %s", node.id, prop.getKey(), prop.getValue()));
                        }
                        break;
                }
            }
            for (ElementDefStaticProperty prop : elemDef.staticProperties) {
                if (!checked.contains(prop.elementId)) {
                    throw new horizon.GraphException(String.format("Node[%s]: Missing required property: %s", node.id, prop.elementId));
                }
            }
        }
    }

    void dump() throws horizon.GraphException {
        System.out.printf("Graph name: %s\n", graphName);
        for (horizon.GraphNode n : nodes.values()) {
            System.out.printf("GraphNode \"%s\": %s %s (%d inputs)\n", n.name, n.category, n.elementId, n.inputs.size());
            if (n.outputs.size() > 0) {
                for (String oId : n.outputs) {
                    System.out.printf("  Out: %s\n", nodes.get(oId).name);
                }
            } else {
                System.out.print("  No outs\n");
            }
        }
    }

}

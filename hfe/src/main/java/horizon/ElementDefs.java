package horizon;

import com.google.gson.Gson;

import java.util.ArrayList;
import java.util.List;

class ElementDefRequiredStream {
    int staticPropertyId;
    int runtimeType;
    boolean required;
}

class ElementDefStaticPropertyOptions {
    String name;
    boolean selected;
    String internalName;
}

class ElementDefStaticProperty {
    String label;
    String description;
    String internalName;
    boolean required;
    boolean predefined;
    String elementId;
    String staticPropertyType;
    String requiredDataType;
    boolean multiline;
    boolean htmlAllowed;
    float minValue;
    float maxValue;
    float step;
    ArrayList<ElementDefStaticPropertyOptions> options;
    String mapsTo;

    static public ElementDefStaticProperty makeString(String id, String label, String description) {
        ElementDefStaticProperty prop = new ElementDefStaticProperty();
        prop.label = label;
        prop.description = description;
        prop.internalName = id;
        prop.required = true;
        prop.predefined = false;
        prop.elementId = id;
        prop.staticPropertyType = "text";
        prop.requiredDataType = "String";
        prop.multiline = false;
        prop.htmlAllowed = false;
        prop.minValue = 0;
        prop.maxValue = 0;
        prop.step = 0;
        prop.options = null;
        prop.mapsTo = "String";
        return prop;
    }

    static public ElementDefStaticProperty makeInt(String id, String label, String description, int minValue, int maxValue) {
        ElementDefStaticProperty prop = new ElementDefStaticProperty();
        prop.label = label;
        prop.description = description;
        prop.internalName = id;
        prop.required = true;
        prop.predefined = false;
        prop.elementId = id;
        prop.staticPropertyType = "integer";
        prop.requiredDataType = "Integer";
        prop.multiline = false;
        prop.htmlAllowed = false;
        prop.minValue = minValue;
        prop.maxValue = maxValue;
        prop.step = 1;
        prop.options = null;
        prop.mapsTo = "Integer";
        return prop;
    }

    static public ElementDefStaticProperty makeOptions(String id, String label, String description, List<String> options) {
        ElementDefStaticProperty prop = new ElementDefStaticProperty();
        prop.label = label;
        prop.description = description;
        prop.internalName = id;
        prop.required = true;
        prop.predefined = false;
        prop.elementId = id;
        prop.staticPropertyType = "singleValueSelection";
        prop.requiredDataType = null;
        prop.multiline = false;
        prop.htmlAllowed = false;
        prop.minValue = 0;
        prop.maxValue = 0;
        prop.step = 0;
        prop.options = new ArrayList<>();
        for (String optionValue : options) {
            ElementDefStaticPropertyOptions option = new ElementDefStaticPropertyOptions();
            option.internalName = optionValue;
            option.name = optionValue;
            prop.options.add(option);
        }
        prop.mapsTo = null;
        return prop;
    }
}

class ElementDef {
    String name;
    String description;
    String iconUri;
    String elementId;
    String category;
    ArrayList<ElementDefRequiredStream> requiredStreams;
    Boolean noOutputs;
    ArrayList<ElementDefStaticProperty> staticProperties;

    ElementDef(String id, String name, String description, String category) {
        this.name = name;
        this.description = description;
        this.iconUri = "mocks/"+id+".png";
        this.elementId = "horizon.flink.filter."+id;
        this.category = category;
        this.staticProperties = new ArrayList<>();
        this.requiredStreams = new ArrayList<>();
    }

    static public ElementDef makeSource(String id, String name, String description) {
        return new ElementDef(id, name, description, "SOURCE");
    }

    static public ElementDef makeFilter(String id, String name, String description, String category) {
        return makeFilter(id, name, description, category, 1);
    }

    static public ElementDef makeFilter(String id, String name, String description, String category, int inputStreams) {
        ElementDef def = new ElementDef(id, name, description, category);

        for (int i=0; i<inputStreams; i++) {
            ElementDefRequiredStream stream = new ElementDefRequiredStream();
            stream.staticPropertyId = 0;
            stream.runtimeType = 0;
            stream.required = true;
            def.requiredStreams.add(stream);
        }

        return def;
    }

    static public ElementDef makeSink(String id, String name, String description) {
        ElementDef def = new ElementDef(id, name, description, "SINK");
        def.noOutputs = true;

        ElementDefRequiredStream stream = new ElementDefRequiredStream();
        stream.staticPropertyId = 0;
        stream.runtimeType = 0;
        stream.required = true;
        def.requiredStreams.add(stream);

        return def;
    }

    ElementDefStaticProperty getStaticProperty(String elementId) {
        for (ElementDefStaticProperty p : staticProperties) {
            if (p.elementId.equals(elementId)) {
                return p;
            }
        }
        return null;
    }
}

public class ElementDefs {

    private ArrayList<ElementDef> elements;

    ElementDefs() {
        elements = new ArrayList<>();
    }

    void add(ElementDef def) {
        elements.add(def);
    }

    ElementDef getDef(String elementId) {
        for (ElementDef e : elements) {
            if (e.elementId.equals(elementId)) {
                return e;
            }
        }
        return null;
    }

    String serialize() {
        Gson gson = new Gson();
        return gson.toJson(elements);
    }
}

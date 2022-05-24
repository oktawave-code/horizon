package horizon.utils;

import org.reflections.Reflections;

import java.util.Set;

public class FlinkOperationsRegistry {

    private Set<Class<?>> operations;

    public FlinkOperationsRegistry(String packageName) {
        Reflections reflections = new Reflections(packageName);
        operations = reflections.getTypesAnnotatedWith(FlinkOperation.class);
    }

    public Set<Class<?>> getOperationsClasses() {
        return operations;
    }
}

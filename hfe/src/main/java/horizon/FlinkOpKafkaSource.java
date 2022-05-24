package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.annotation.PublicEvolving;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.TypeExtractor;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.timestamps.AscendingTimestampExtractor;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer011;
import org.apache.flink.streaming.util.serialization.KeyedDeserializationSchema;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Properties;

@FlinkOperation
public class FlinkOpKafkaSource extends FlinkOp {

    @PublicEvolving
    public static class JSONDeserializationSchema implements KeyedDeserializationSchema<ObjectNode> {
        private ObjectMapper mapper;

        public JSONDeserializationSchema() {
            this.mapper = new ObjectMapper();
        }

        public ObjectNode deserialize(byte[] messageKey, byte[] message, String topic, int partition, long offset) {
            try {
                if (message != null) {
                    JsonNode json = this.mapper.readTree(message);
                    if (json.isObject()) {
                        return (ObjectNode)json;
                    }
                }
                return this.mapper.createObjectNode(); //  if something's not right - return empty object
            } catch (Exception e) {
                return this.mapper.createObjectNode().put("malformedData", message);
            }
        }

        public boolean isEndOfStream(ObjectNode nextElement) {
            return false;
        }

        public TypeInformation<ObjectNode> getProducedType() {
            return TypeExtractor.getForClass(ObjectNode.class);
        }
    }

    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        Properties kafkaProperties = new Properties();
        kafkaProperties.setProperty("bootstrap.servers", System.getenv("KAFKA_HOSTNAME") + ":" + System.getenv("KAFKA_PORT"));
        kafkaProperties.setProperty("group.id", "flink-consumer");
        FlinkKafkaConsumer011 consumer = new FlinkKafkaConsumer011(
                (String) (properties.get("topic")),
                new JSONDeserializationSchema(),
                kafkaProperties);
        consumer.assignTimestampsAndWatermarks(new AscendingTimestampExtractor() {

            @Override
            public long extractAscendingTimestamp(Object element) {
                return System.currentTimeMillis();
            }
        });
        return env.addSource(consumer);
    }


    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeSource(
                "kafkaSource",
                "Kafka source",
                "Data source, using stream provided in Kafka topic");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "topic",
                "Topic",
                "Kafka topic name"));

        return def;
    }
}

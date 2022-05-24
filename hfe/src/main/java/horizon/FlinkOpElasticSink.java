package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.api.common.functions.RuntimeContext;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.elasticsearch.ElasticsearchSinkFunction;
import org.apache.flink.streaming.connectors.elasticsearch.RequestIndexer;
import org.apache.flink.streaming.connectors.elasticsearch6.ElasticsearchSink;
import org.apache.http.HttpHost;
import org.elasticsearch.action.index.IndexRequest;

import java.util.*;

@FlinkOperation
public class FlinkOpElasticSink extends FlinkOp {

    private static class ElasticsearchSinkFunctionBuilder implements ElasticsearchSinkFunction<ObjectNode> {
        ObjectMapper mapper = new ObjectMapper();

        String index;
        String type;

        ElasticsearchSinkFunctionBuilder(String index, String type) {
            this.index = index;
            this.type = type;
        }

        IndexRequest createIndexRequest(ObjectNode element) {
            Map<String, String> json = mapper.convertValue(element, Map.class);

            return org.elasticsearch.client.Requests.indexRequest()
                    .index(this.index)
                    .type(this.type)
                    .source(json);
        }

        @Override
        public void process(ObjectNode element, RuntimeContext ctx, RequestIndexer indexer) {
            indexer.add(createIndexRequest(element));
        }
    }


    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        DataStream<ObjectNode> stream = inputStreams.get(0);

        String index = (String) properties.get("index");
        String type = (String) properties.get("type");

        String hostname = System.getenv("ELASTICSEARCH_HOSTNAME");
        Integer port = Integer.parseInt(System.getenv("ELASTICSEARCH_PORT"));
        String protocol = System.getenv("ELASTICSEARCH_PROTOCOL");
        List<HttpHost> httpHosts = Arrays.asList(new HttpHost(hostname, port, protocol));

        ElasticsearchSinkFunction<ObjectNode> sinkFunction = new ElasticsearchSinkFunctionBuilder(index, type);

        // use a ElasticsearchSink.Builder to create an ElasticsearchSink
        ElasticsearchSink.Builder<ObjectNode> builder = new ElasticsearchSink.Builder<>(httpHosts, sinkFunction);
        // configuration for the bulk requests; this instructs the sink to emit after every element, otherwise they would be buffered
        builder.setBulkFlushMaxActions(1);

        stream.addSink(builder.build());
        return null;
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeSink(
                "elasticSink",
                "Elasticsearch sink",
                "Data sink, using Elasticsearch base");

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "index",
                "Index",
                "Elasticsearch index"));

        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "type",
                "Type",
                "Elasticsearch type"));

        return def;
    }
}

package topics;

import java.util.*;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;

import javax.inject.Inject;
import javax.inject.Singleton;

import com.typesafe.config.Config;

import org.apache.kafka.clients.admin.*;

@Singleton
public class KafkaClientService {
    
    private AdminClient client;

    private final Config config;

    @Inject
    KafkaClientService(Config config) {
        this.config = config;
        String kafkaUrl = this.config.getString("flowapi.kafkaurl");
        Properties props = new Properties();
        props.setProperty(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaUrl);
        client = AdminClient.create(props);
    }

    public Topic[] getAll() throws InterruptedException, ExecutionException, TimeoutException {
        Set<String> names = client
            .listTopics()
            .names()
            .get();

        Map<String, TopicDescription> describedTopicsMap = client.describeTopics(names)
                .all()
                .get();

        ArrayList<Topic> topics = new ArrayList<Topic>();
        describedTopicsMap.forEach((name, description) -> topics.add(new Topic(name, description.partitions().size())));

        return topics.toArray(new Topic[topics.size()]);
    }

    public Topic[] createTopics(Topic[] topics) throws InterruptedException, ExecutionException, TimeoutException {

        List<NewTopic> newTopics = Arrays.asList(topics).stream().map(topic -> {
            return new NewTopic(topic.getName(), topic.getPartitionsNumber(), (short) 1);
        }).collect(Collectors.toList());

        client
            .createTopics(newTopics)
            .all()
            .get();
        
        return topics;
    }

    public String[] deleteTopics(String[] names) throws InterruptedException, ExecutionException, TimeoutException {

        client.deleteTopics(Arrays.asList(names))
            .all()
            .get();

        return names;
    }
    
}
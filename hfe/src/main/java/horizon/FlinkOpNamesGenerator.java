package horizon;

import horizon.utils.FlinkOperation;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.node.ObjectNode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Random;
import java.util.stream.IntStream;
import java.util.stream.Stream;

@FlinkOperation
public class FlinkOpNamesGenerator extends FlinkOp {


    class NamesSourceFunction implements SourceFunction<ObjectNode> {

        private String[] names = {
                "Oliver", "Jack", "Harry", "Jacob", "Charlie", "Thomas", "George", "Oscar", "James", "William", "Noah", "Alfie", "Joshua",
                "Muhammad", "Henry", "Leo", "Archie", "Ethan", "Joseph", "Freddie", "Samuel", "Alexander", "Logan", "Daniel", "Isaac",
                "Max", "Mohammed", "Benjamin", "Mason", "Lucas", "Edward", "Harrison", "Jake", "Dylan", "Riley", "Finley", "Theo",
                "Sebastian", "Adam", "Zachary", "Arthur", "Toby", "Jayden", "Luke", "Harley", "Lewis", "Tyler", "Harvey", "Matthew",
                "David", "Reuben", "Michael", "Elijah", "Kian", "Tommy", "Mohammad", "Blake", "Luca", "Theodore", "Stanley", "Jenson",
                "Nathan", "Charles", "Frankie", "Jude", "Teddy", "Louie", "Louis", "Ryan", "Hugo", "Bobby", "Elliott", "Dexter", "Ollie",
                "Alex", "Liam", "Kai", "Gabriel", "Connor", "Aaron", "Frederick", "Callum", "Elliot", "Albert", "Leon", "Ronnie", "Rory",
                "Jamie", "Austin", "Seth", "Ibrahim", "Owen", "Caleb", "Ellis", "Sonny", "Robert", "Joey", "Felix", "Finlay", "Jackson"};
        private String[] surnames = {
                "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas",
                "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis",
                "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams",
                "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker",
                "Evans", "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy",
                "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James",
                "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins",
                "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons", "Foster", "Gonzales",
                "Bryant", "Alexander", "Russell", "Griffin", "Diaz", "Hayes"};

        private volatile boolean isRunning = true;
        private Random rand = new Random();
        private int count;
        private String outputField;

        NamesSourceFunction(int count, String outputField) {
            this.count = count;
            this.outputField = outputField;
        }

        @Override
        public void run(SourceContext<ObjectNode> sourceContext) throws Exception {
            try (Stream<String> stream = getStream()) {
                final ObjectMapper mapper = new ObjectMapper();
                Iterator<String> iterator = stream.iterator();
                while (isRunning && iterator.hasNext()) {
                    ObjectNode element = mapper.createObjectNode();
                    element.put(outputField, iterator.next());
                    sourceContext.collect(element);
                }
            }
        }

        @Override
        public void cancel() {
            isRunning = false;
        }

        private Stream<String> getStream() {
            return IntStream.range(1, count).mapToObj(n -> names[rand.nextInt(names.length)] + " " + surnames[rand.nextInt(surnames.length)]);
        }
    }

    @Override
    public DataStream<ObjectNode> build(StreamExecutionEnvironment env, ArrayList<DataStream<ObjectNode>> inputStreams, HashMap<String, Object> properties) {
        DataStream<ObjectNode> stream = env.addSource(new NamesSourceFunction((int) ((double)properties.get("count")), (String) properties.get("outputField")));
        return stream;
    }

    @Override
    public ElementDef getDef() {
        ElementDef def = ElementDef.makeSource(
                "namesGenerator",
                "Names generator",
                "Data source, generating random names");

        def.staticProperties.add(ElementDefStaticProperty.makeInt(
                "count",
                "Count",
                "How many names will be generated",
                1,
                1000));
        def.staticProperties.add(ElementDefStaticProperty.makeString(
                "outputField",
                "Output field",
                "Field name for generated lines"));

        return def;
    }
}

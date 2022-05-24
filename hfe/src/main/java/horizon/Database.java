package horizon;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import org.bson.Document;
import org.bson.types.ObjectId;

import static com.mongodb.client.model.Filters.eq;

public class Database {

    private MongoCollection<Document> collection;

    public Database(String connectionString, String databaseName, String collectionName) {
        MongoClient mongoClient = MongoClients.create(connectionString);
        MongoDatabase database = mongoClient.getDatabase(databaseName);
        collection = database.getCollection(collectionName);
    }

    public String getGraph(String id) {
        System.out.printf("Getting graph: %s\n", id);
        ObjectId objId;
        try {
            objId = new ObjectId(id);
        } catch (IllegalArgumentException e) {
            System.out.println(" Invalid id");
            return null;
        }
        Document doc = collection.find(eq("_id", objId)).first();
        if (doc == null) {
            System.out.println(" Not found");
            return null;
        }
        System.out.printf(" Found: %s\n", doc.getString("name"));
        return doc.toJson();
    }
}

package controllers;

import java.io.IOException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeoutException;

import javax.inject.Inject;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;

import play.libs.Json;
import play.mvc.Controller;
import play.mvc.Result;
import play.mvc.With;
import security.VerifyTokenAction;
import topics.KafkaClientService;
import topics.Topic;

public class TopicsController extends Controller {

	KafkaClientService service;

    @Inject
    public TopicsController(KafkaClientService service) {
        this.service = service;
    } 

    @With(VerifyTokenAction.class)
    public Result list() throws InterruptedException, ExecutionException, TimeoutException {
    	return ok(Json.toJson(this.service.getAll()));
    }
    
    @With(VerifyTokenAction.class)
    public Result create() throws InterruptedException, ExecutionException, TimeoutException, JsonParseException, JsonMappingException, IOException {
    	JsonNode json = request().body().asJson();
    	if (json == null) {
    		return badRequest("Bad request.");
    	}
    	Topic[] topics = Json.fromJson(json, Topic[].class);
        return ok(Json.toJson(this.service.createTopics(topics)));
    }
    
    @With(VerifyTokenAction.class)
    public Result delete() throws InterruptedException, ExecutionException, TimeoutException {
    	JsonNode json = request().body().asJson();
    	if (json == null) {
    		return badRequest("Bad request.");
    	}
    	String[] names = Json.fromJson(json, String[].class);
        return ok(Json.toJson(this.service.deleteTopics(names)));
    }
}
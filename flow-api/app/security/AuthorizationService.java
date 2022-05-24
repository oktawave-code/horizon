package security;

import play.libs.ws.*;
import javax.inject.Inject;
import javax.inject.Singleton;
import java.util.concurrent.CompletionStage;
import com.typesafe.config.Config;


@Singleton
public class AuthorizationService implements WSBodyReadables, WSBodyWritables {

    private final WSClient ws;

    private final Config config;

    @Inject
    public AuthorizationService(WSClient ws, Config config) {
        this.ws = ws;
        this.config = config;
    }

    public CompletionStage<? extends WSResponse> validateToken(String token) {
        String url = this.config.getString("flowapi.authorization.url");
        WSRequest request = ws.url(url + token);
        return request.get();
    }
}
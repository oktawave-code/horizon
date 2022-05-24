package security;

import java.util.concurrent.CompletionStage;
import java.util.concurrent.CompletableFuture;
import play.mvc.Http;
import play.mvc.Result;
import play.mvc.Results;
import javax.inject.Inject;
import security.AuthorizationService;
import javax.inject.Singleton;

@Singleton
public class VerifyTokenAction extends play.mvc.Action.Simple {

    AuthorizationService auth;

    @Inject
    public VerifyTokenAction(AuthorizationService auth) {
        this.auth = auth;
    }

    public CompletionStage<Result> call(Http.Context ctx) {
        String token = ctx.request().header("Bearer").orElseGet(() -> "");
        return auth.validateToken(token).thenCompose(response -> {
            if (response.getStatus() == 200) {
                return delegate.call(ctx);
            } else {
                return CompletableFuture.completedFuture(Results.status(401, "Authorization error."));
            }
        });
    }

}
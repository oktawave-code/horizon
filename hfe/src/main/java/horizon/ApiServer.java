package horizon;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import horizon.utils.FlinkOperationsRegistry;
import org.apache.commons.io.IOUtils;

import java.io.IOException;
import java.io.OutputStream;
import java.io.StringWriter;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;

public class ApiServer {

    private static FlinkBuilder builder;

    private static String unescape(String str) {
        StringBuffer newStr = new StringBuffer(str.length());
        boolean backslashed = false;
        for (int i = 0; i < str.length(); i++) {
            int cp = str.codePointAt(i);
            if (!backslashed) {
                if (cp == '\\') {
                    backslashed = true;
                } else {
                    newStr.append(Character.toChars(cp));
                }
            } else {
                backslashed = false;
                if (cp == '\\') {
                    newStr.append("\\");
                } else {
                    // backslash sequences switch may be put here
                    newStr.append(Character.toChars(cp));
                }
            }
        }
        return newStr.toString();
    }

    private static String unbase64(String str) {
        byte[] bytes = Base64.getDecoder().decode(str);
        return new String(bytes, StandardCharsets.UTF_8);
    }

    private static void initBuilder() throws Exception {
        builder = new FlinkBuilder();
        FlinkOperationsRegistry registry = new FlinkOperationsRegistry("horizon");
        for (Class<?> operation : registry.getOperationsClasses()) {
            builder.registerOperator((FlinkOp) operation.newInstance());
        }
    }

    public static void main(String[] args) throws Exception {
        initBuilder();

        String dbConnectString = System.getenv("MONGODB_CONNECTION_URL");
        Database db = null;
        if (dbConnectString != null) {
            db = new Database(dbConnectString, "graphs", "graphs");
        }

        String envMode = System.getenv("MODE");
        if ((envMode != null) && (envMode.equals("SERVER"))) {
            startServer(db);
        } else {
            if (args.length == 0) {
                System.out.println("Missing arguments!");
                return;
            }
            System.out.printf("Arguments:\n%s\n", Arrays.toString(args));
            if (args[0].equals("-e")) {
                startBuilder(unescape(args[1]));
            } else if (args[0].equals("-b")) {
                startBuilder(unbase64(args[1]));
            } else if (args[0].equals("-db")) {
                if (db == null) {
                    throw new RuntimeException("DB connection not present");
                }
                startBuilder(db.getGraph(args[1]));
            } else {
                startBuilder(args[0]);
            }
        }
    }

    private static void startBuilder(String json) throws Exception {
        Graph graph;
        System.out.printf("Input string:\n%s\n", json);
        try {
            graph = new Graph(json);
            graph.validate(builder.getElementDefs());
        } catch (horizon.GraphException e) {
            System.out.printf("Error\n%s\n\n", e.message);
            return;
        }
        System.out.print("Graph verified\n\n");
        builder.useGraph(graph);
        builder.build();
        builder.execute();
    }

    private static void startServer(Database db) throws IOException {
        System.out.println("HFE server booting");

        HttpServer server = HttpServer.create(new InetSocketAddress(8000), 0);
        server.createContext("/form", new FormHandler());
        server.createContext("/validator", new ValidatorHandler());
        if (db != null) {
            server.createContext("/dbvalidator", new DBValidatorHandler(db));
        }
        server.createContext("/defs", new DefsHandler());
        server.setExecutor(null); // creates a default executor
        server.start();
    }

    private static void out(HttpExchange t, int code, String msg) throws IOException {
        t.sendResponseHeaders(code, msg.length());
        OutputStream os = t.getResponseBody();
        os.write(msg.getBytes());
        os.close();
    }

    static class FormHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            String response =
                    "<html>" +
                            "<body>" +
                            "<form action=\"/validator\" method=\"post\">" +
                            "Enter serialized graph here:<br>" +
                            "<input type=\"text\" name=\"json\"><br>" +
                            "<input type=\"submit\"><br>" +
                            "</form>" +
                            "<form action=\"/dbvalidator\" method=\"post\">" +
                            "Enter graph id here:<br>" +
                            "<input type=\"text\" name=\"id\"><br>" +
                            "<input type=\"submit\"><br>" +
                            "</form>" +
                            "</body>" +
                            "</html>";
            out(t, 200, response);
        }
    }

    static class DBValidatorHandler implements HttpHandler {
        private Database db;

        DBValidatorHandler(Database db) {
            this.db = db;
        }

        @Override
        public void handle(HttpExchange t) throws IOException {
            StringWriter writer = new StringWriter();
            IOUtils.copy(t.getRequestBody(), writer, StandardCharsets.UTF_8);
            String params = writer.toString();
            String content;
            System.out.printf("DB Validation request: %s %s %s\n", t.getRequestMethod(), t.getRequestHeaders().getFirst("Content-Type"), params);
            if (t.getRequestHeaders().getFirst("Content-Type").equals("application/x-www-form-urlencoded")) {
                String[] pParts = params.split("=", 2);
                if (!pParts[0].equals("id")) {
                    out(t, 400, "Missing data\n");
                    return;
                }
                content = pParts[1];
            } else {
                content = params;
            }
            String decoded = java.net.URLDecoder.decode(content, "UTF-8");
            Graph graph;
            try {
                graph = new Graph(db.getGraph(decoded));
                graph.validate(builder.getElementDefs());
            } catch (horizon.GraphException e) {
                out(t, 400, "Error: " + e.message + "\n");
                return;
            }
            out(t, 200, "Okay\n");
        }
    }

    static class ValidatorHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            StringWriter writer = new StringWriter();
            IOUtils.copy(t.getRequestBody(), writer, StandardCharsets.UTF_8);
            String params = writer.toString();
            String content;
            System.out.printf("Validation request: %s %s %s\n", t.getRequestMethod(), t.getRequestHeaders().getFirst("Content-Type"), params);
            if (t.getRequestHeaders().getFirst("Content-Type").equals("application/x-www-form-urlencoded")) {
                String[] pParts = params.split("=", 2);
                if (!pParts[0].equals("json")) {
                    out(t, 400, "Missing data\n");
                    return;
                }
                content = pParts[1];
            } else {
                content = params;
            }
            String decoded = java.net.URLDecoder.decode(content, "UTF-8");
            Graph graph;
            try {
                graph = new Graph(decoded);
                graph.validate(builder.getElementDefs());
            } catch (horizon.GraphException e) {
                out(t, 400, "Error: " + e.message + "\n");
                return;
            }
            out(t, 200, "Okay\n");
        }
    }

    static class DefsHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            t.getResponseHeaders().add("Content-Type", "application/json");
            out(t, 200, builder.getElementDefs().serialize());
        }
    }

}

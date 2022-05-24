## Flow API

Horizon PaaS REST API.

### Configuration

Environment variables

- APPLICATION_SECRET - mandatory for application security(see Playframework docs for production deployment)
- KAFKA_API_URL - hostname and port for kafka client
- SKIP_SSL_CERT_VALIDATION - skipping jvm security for CA certificates
- AUTHORIZATION_URL - endpoint for token validation
# Operations & Observability

## Messaging
- Broker: RabbitMQ (docker-compose service `edupath-rabbitmq`)
- Exchange: `learning-events` (topic)
- Routing keys:
  - `course.upsert`
  - `enrollment.link`
  - `grade.insert`
  - `activity.completion`
  - `activity.access`
- Env:
  - `MQ_TYPE=rabbitmq`
  - `MQ_URL=amqp://localhost`
  - `MQ_EXCHANGE=learning-events`

## Rate Limiting
- Global limit: 60 req/min via `express-rate-limit`.
- Adjust policy in `src/index.js` if needed.

## Logging
- Structured JSON via `pino`.
- Configure level with `LOG_LEVEL=debug|info|warn|error`.

## OpenTelemetry
- Enable with `OTEL_ENABLE=true`.
- Optional OTLP HTTP exporter: `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces`.
- Auto-instrumentations enabled for Node.

## API Docs
- Swagger UI available at `/docs` if `openapi/openapi.yaml` is present.

## Tests
- Run `npm test`.
- Includes unit tests for health/admin and a basic E2E sync test with mocked Moodle client.

## CI
- GitHub Actions workflow under `.github/workflows/ci.yml` builds, runs migrations (Postgres service), and executes tests.

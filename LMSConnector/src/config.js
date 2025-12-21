import dotenv from 'dotenv';
dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3001', 10),
  apiKey: process.env.API_KEY || '',
  db: {
    disable: (process.env.DISABLE_DB || 'false').toLowerCase() === 'true',
    host: process.env.PGHOST || 'localhost',
    port: parseInt(process.env.PGPORT || '5432', 10),
    user: process.env.PGUSER || 'postgres',
    password: process.env.PGPASSWORD || 'postgres',
    database: process.env.PGDATABASE || 'edupath',
  },
  moodle: {
    baseUrl: process.env.MOODLE_BASE_URL || '',
    token: process.env.MOODLE_TOKEN || '',
  },
  messaging: {
    type: (process.env.MQ_TYPE || 'rabbitmq'), // rabbitmq|none
    url: process.env.MQ_URL || 'amqp://localhost',
    exchange: process.env.MQ_EXCHANGE || 'learning-events',
  },
  otel: {
    enable: (process.env.OTEL_ENABLE || 'false').toLowerCase() === 'true',
    serviceName: process.env.OTEL_SERVICE_NAME || 'LMSConnector',
    otlpEndpoint: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || '',
  }
};

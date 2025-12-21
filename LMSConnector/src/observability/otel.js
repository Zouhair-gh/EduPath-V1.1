import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { config } from '../config.js';

let sdk;

export async function initOtel() {
  if (sdk) return;
  const exporter = config.otel.otlpEndpoint ? new OTLPTraceExporter({ url: config.otel.otlpEndpoint }) : undefined;
  sdk = new NodeSDK({
    traceExporter: exporter,
    instrumentations: [getNodeAutoInstrumentations()],
  });
  await sdk.start();
}

export async function shutdownOtel() {
  if (sdk) await sdk.shutdown();
}

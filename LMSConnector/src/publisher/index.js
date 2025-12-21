import amqp from 'amqplib';
import { config } from '../config.js';
import { logger } from '../common/logger.js';

let channel = null;

export async function initPublisher() {
  if (config.messaging.type !== 'rabbitmq') {
    logger.warn({ type: config.messaging.type }, 'Messaging disabled or unsupported');
    return;
  }
  try {
    const conn = await amqp.connect(config.messaging.url);
    channel = await conn.createChannel();
    await channel.assertExchange(config.messaging.exchange, 'topic', { durable: true });
    logger.info({ exchange: config.messaging.exchange }, 'RabbitMQ publisher initialized');
  } catch (e) {
    logger.error({ err: e }, 'Failed to initialize RabbitMQ');
  }
}

export function isPublisherReady() {
  return !!channel;
}

export async function publishEvent(routingKey, event) {
  if (!channel) return false;
  const payload = Buffer.from(JSON.stringify(event));
  try {
    return channel.publish(config.messaging.exchange, routingKey, payload, { persistent: true });
  } catch (e) {
    logger.error({ err: e }, 'Publish failed');
    return false;
  }
}

export function makeEvent({ actorId, verb, objectId, objectType, context = {}, occurredAt = new Date().toISOString(), sourceId }) {
  return {
    actor: { id: actorId },
    verb,
    object: { id: objectId, type: objectType },
    context,
    occurredAt,
    sourceId,
    schema: 'edupath.learning.v1',
  };
}

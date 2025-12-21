import fs from 'fs';
import path from 'path';
import yaml from 'yaml';
import swaggerUi from 'swagger-ui-express';

export function initSwagger(app) {
  try {
    const specPath = path.join(process.cwd(), 'openapi', 'openapi.yaml');
    if (!fs.existsSync(specPath)) return;
    const spec = yaml.parse(fs.readFileSync(specPath, 'utf8'));
    app.use('/docs', swaggerUi.serve, swaggerUi.setup(spec));
  } catch (_) {
    // ignore
  }
}

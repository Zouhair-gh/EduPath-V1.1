import express from 'express';

const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    service: 'LMSConnector',
    version: '0.1.0',
    endpoints: {
      public: ['/health', '/'],
      admin: ['/sources', '/sync/moodle', '/sync/moodle/:sourceId', '/jobs/:jobId'],
    },
    note: 'Admin endpoints require X-API-Key header',
  });
});

export default router;

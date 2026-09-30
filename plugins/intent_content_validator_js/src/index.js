/**
 * Intent Content Consistency Validator Service
 * Wraps @intentsolutionsio/000-jeremy-content-consistency-validator and exposes it via HTTP
 */
import express from 'express';
import cors from 'cors';
import ContentValidator from '@intentsolutionsio/000-jeremy-content-consistency-validator';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Initialize validator
const validator = new ContentValidator();

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'intent-content-validator' });
});

/**
 * Validate content for consistency
 * POST /validate
 * Body: { content: string, options?: object }
 */
app.post('/validate', async (req, res) => {
  try {
    const { content, options = {} } = req.body;

    if (!content) {
      return res.status(400).json({
        error: 'Missing required field: content',
      });
    }

    const result = await validator.validate(content, options);

    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    console.error('Validation error:', error);
    res.status(500).json({
      error: 'Validation failed',
      message: error.message,
    });
  }
});

/**
 * Batch validate multiple contents
 * POST /validate-batch
 * Body: { contents: string[], options?: object }
 */
app.post('/validate-batch', async (req, res) => {
  try {
    const { contents, options = {} } = req.body;

    if (!Array.isArray(contents) || contents.length === 0) {
      return res.status(400).json({
        error: 'Missing or invalid required field: contents (must be non-empty array)',
      });
    }

    const results = await Promise.all(
      contents.map((content) => validator.validate(content, options))
    );

    res.json({
      success: true,
      data: results,
    });
  } catch (error) {
    console.error('Batch validation error:', error);
    res.status(500).json({
      error: 'Batch validation failed',
      message: error.message,
    });
  }
});

/**
 * Get validator configuration/capabilities
 */
app.get('/config', (req, res) => {
  res.json({
    service: 'intent-content-validator',
    version: '0.1.0',
    package: '@intentsolutionsio/000-jeremy-content-consistency-validator@3.0.2',
    endpoints: {
      health: 'GET /health',
      validate: 'POST /validate',
      validateBatch: 'POST /validate-batch',
      config: 'GET /config',
    },
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message,
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`[IntentContentValidator] Service listening on port ${PORT}`);
  console.log(`[IntentContentValidator] Health check: http://localhost:${PORT}/health`);
});

export default app;

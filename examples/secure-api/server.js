// Secure API example showing best practices
const express = require('express');
const mysql = require('mysql2/promise');
const bcrypt = require('bcrypt');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const validator = require('validator');
require('dotenv').config();

const app = express();

// ✅ Security middleware
app.use(helmet());
app.use(express.json({ limit: '10kb' })); // Limit body size

// ✅ Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// ✅ Database connection with environment variables
const dbConfig = {
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

let pool;
(async () => {
  pool = mysql.createPool(dbConfig);
})();

// ✅ Authentication middleware
const authenticateToken = (req, res, next) => {
  const token = req.headers['authorization']?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  // In production, verify JWT token here
  // For example purposes, simplified
  req.userId = 1; // Would come from verified token
  next();
};

// ✅ Input validation middleware
const validateLoginInput = (req, res, next) => {
  const { email, password } = req.body;

  if (!email || !validator.isEmail(email)) {
    return res.status(400).json({ error: 'Valid email required' });
  }

  if (!password || password.length < 8) {
    return res.status(400).json({ error: 'Password must be at least 8 characters' });
  }

  next();
};

// ✅ Secure login with prepared statements and bcrypt
app.post('/login', validateLoginInput, async (req, res) => {
  try {
    const { email, password } = req.body;

    // Use prepared statement to prevent SQL injection
    const [users] = await pool.query(
      'SELECT id, email, password_hash FROM users WHERE email = ?',
      [email]
    );

    if (users.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = users[0];

    // Compare hashed password
    const isValid = await bcrypt.compare(password, user.password_hash);

    if (!isValid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // ✅ Only return non-sensitive data
    res.json({
      success: true,
      user: {
        id: user.id,
        email: user.email
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ✅ Secure ping with validation (or better: remove this endpoint entirely)
app.get('/ping', authenticateToken, (req, res) => {
  const { host } = req.query;

  // Whitelist validation
  const allowedHosts = ['8.8.8.8', '1.1.1.1', 'localhost'];

  if (!allowedHosts.includes(host)) {
    return res.status(400).json({ error: 'Invalid host' });
  }

  // Use safe library instead of exec
  // In production, consider removing this entirely or using a monitoring service
  res.json({ message: 'Ping functionality disabled for security' });
});

// ✅ XSS prevention with proper escaping
app.get('/search', (req, res) => {
  const { q } = req.query;

  if (!q || typeof q !== 'string') {
    return res.status(400).json({ error: 'Query required' });
  }

  // Sanitize input
  const sanitized = validator.escape(q);

  // Use JSON response instead of HTML
  res.json({
    query: sanitized,
    results: [] // Actual search logic here
  });
});

// ✅ IDOR protection with authorization check
app.get('/user/:id', authenticateToken, async (req, res) => {
  try {
    const requestedId = parseInt(req.params.id, 10);

    if (isNaN(requestedId)) {
      return res.status(400).json({ error: 'Invalid ID' });
    }

    // Authorization: user can only access their own data
    if (requestedId !== req.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const [users] = await pool.query(
      'SELECT id, email, created_at FROM users WHERE id = ?',
      [requestedId]
    );

    if (users.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(users[0]);
  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ✅ Protected delete with authentication and authorization
app.delete('/user/:id', authenticateToken, async (req, res) => {
  try {
    const requestedId = parseInt(req.params.id, 10);

    if (isNaN(requestedId)) {
      return res.status(400).json({ error: 'Invalid ID' });
    }

    // Authorization check
    if (requestedId !== req.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    await pool.query('DELETE FROM users WHERE id = ?', [requestedId]);

    res.json({ success: true });
  } catch (error) {
    console.error('Delete user error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ✅ Remove eval entirely - use safe alternatives
app.post('/calculate', (req, res) => {
  const { operation, a, b } = req.body;

  const numA = parseFloat(a);
  const numB = parseFloat(b);

  if (isNaN(numA) || isNaN(numB)) {
    return res.status(400).json({ error: 'Invalid numbers' });
  }

  const operations = {
    add: (x, y) => x + y,
    subtract: (x, y) => x - y,
    multiply: (x, y) => x * y,
    divide: (x, y) => (y !== 0 ? x / y : null)
  };

  if (!operations[operation]) {
    return res.status(400).json({ error: 'Invalid operation' });
  }

  const result = operations[operation](numA, numB);

  if (result === null) {
    return res.status(400).json({ error: 'Division by zero' });
  }

  res.json({ result });
});

// ✅ Secure error handler - no stack traces in production
app.use((err, req, res, next) => {
  console.error('Error:', err);

  const isDevelopment = process.env.NODE_ENV === 'development';

  res.status(err.status || 500).json({
    error: isDevelopment ? err.message : 'Internal server error',
    ...(isDevelopment && { stack: err.stack })
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  // ✅ No secrets in logs
});

// ✅ Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM signal received: closing HTTP server');
  await pool.end();
  process.exit(0);
});

// Vulnerable API example for Cyhber Deploy testing
const express = require('express');
const mysql = require('mysql');
const app = express();

app.use(express.json());

// ❌ CRITICO: Hardcoded database credentials
const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'admin123',
  database: 'users_db'
});

// ❌ CRITICO: SQL Injection vulnerability
app.post('/login', (req, res) => {
  const { email, password } = req.body;

  // No input validation
  const sql = `SELECT * FROM users WHERE email = '${email}' AND password = '${password}'`;

  db.query(sql, (err, results) => {
    if (err) return res.status(500).json({ error: err.message });

    if (results.length > 0) {
      // ❌ ALTO: Exposing full user data including sensitive fields
      res.json({ success: true, user: results[0] });
    } else {
      res.status(401).json({ success: false });
    }
  });
});

// ❌ CRITICO: Command injection vulnerability
app.get('/ping', (req, res) => {
  const { host } = req.query;
  const { exec } = require('child_process');

  // No input sanitization
  exec(`ping -c 4 ${host}`, (error, stdout, stderr) => {
    res.json({ output: stdout });
  });
});

// ❌ ALTO: XSS vulnerability
app.get('/search', (req, res) => {
  const { q } = req.query;

  // Reflecting user input without sanitization
  res.send(`<h1>Search results for: ${q}</h1>`);
});

// ❌ ALTO: Insecure direct object reference (IDOR)
app.get('/user/:id', (req, res) => {
  const { id } = req.params;

  // No authorization check
  db.query(`SELECT * FROM users WHERE id = ${id}`, (err, results) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(results[0]);
  });
});

// ❌ MEDIO: Missing authentication middleware
app.delete('/user/:id', (req, res) => {
  const { id } = req.params;

  db.query(`DELETE FROM users WHERE id = ${id}`, (err) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ success: true });
  });
});

// ❌ ALTO: Unsafe eval usage
app.post('/calculate', (req, res) => {
  const { expression } = req.body;

  try {
    const result = eval(expression);
    res.json({ result });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

// ❌ BAJO: Verbose error messages exposing stack traces
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API Key: sk-1234567890abcdef`); // ❌ CRITICO: Hardcoded API key in logs
});

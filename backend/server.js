const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const fs = require('fs');

const app = express();
app.use(express.json());
app.use(cors());

// --- CENTRALIZED ROXY CLOUD DATABASE CONNECTION ---
const pool = new Pool({
    connectionString: 'postgresql://neondb_owner:npg_rkY7hRqwG6HU@ep-tiny-rice-ao9pnffv.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require',
    ssl: { rejectUnauthorized: false }
});

pool.connect((err, client, release) => {
    if (err) return console.error('⚠️ Cloud database connection dropped:', err.stack);
    console.log('🚀 Successfully synchronized with central ROXY cloud database!');
    release();
});

// --- BOOK CATALOG ENDPOINTS ---

app.get('/api/books', async (req, res) => {
    const { search } = req.query;
    try {
        let query = 'SELECT * FROM books';
        let values = [];
        if (search) {
            query += ' WHERE title ILIKE $1 OR author ILIKE $1 OR category ILIKE $1';
            values.push(`%${search}%`);
        }
        const result = await pool.query(query, values);
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: 'Database network error reading catalog assets.' });
    }
});

app.post('/api/books/add', async (req, res) => {
    const { title, author, category, total_copies } = req.body;
    try {
        const query = 'INSERT INTO books (title, author, category, total_copies, available_copies) VALUES ($1, $2, $3, $4, $4)';
        await pool.query(query, [title, author, category, parseInt(total_copies)]);
        res.json({ message: 'Catalog entry appended successfully.' });
    } catch (err) {
        res.status(500).json({ error: 'Failed writing book to cloud cluster.' });
    }
});

app.put('/api/books/update', async (req, res) => {
    const { book_id, total_copies } = req.body;
    try {
        const currentCheck = await pool.query('SELECT total_copies, available_copies FROM books WHERE book_id = $1', [book_id]);
        if (currentCheck.rows.length === 0) return res.status(404).json({ error: 'Target index non-existent.' });
        
        const diff = parseInt(total_copies) - currentCheck.rows[0].total_copies;
        const newAvailable = currentCheck.rows[0].available_copies + diff;
        if (newAvailable < 0) return res.status(400).json({ error: 'Cannot lower copies below what is currently out on loan.' });

        await pool.query('UPDATE books SET total_copies = $1, available_copies = $2 WHERE book_id = $3', [parseInt(total_copies), newAvailable, book_id]);
        res.json({ message: 'Global supply adjusted successfully.' });
    } catch (err) {
        res.status(500).json({ error: 'Fault adjusting stock parameters.' });
    }
});

app.delete('/api/books/delete/:id', async (req, res) => {
    try {
        const result = await pool.query('DELETE FROM books WHERE book_id = $1', [req.params.id]);
        if (result.rowCount === 0) return res.status(404).json({ error: 'Book ID not found.' });
        res.json({ message: 'Element wiped from schema indexes permanently.' });
    } catch (err) {
        res.status(500).json({ error: 'Cannot delete book: It is currently linked to active loan records.' });
    }
});

// --- STUDENT REGISTRY ENDPOINTS (NEW) ---

// Get all students
app.get('/api/students', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM students ORDER BY student_id ASC');
        res.json(result.rows);
    } catch (err) {
        res.status(500).json({ error: 'Failed to retrieve student records from cloud.' });
    }
});

// Add a new student
app.post('/api/students/add', async (req, res) => {
    const { name, email } = req.body;
    try {
        await pool.query('INSERT INTO students (name, email) VALUES ($1, $2)');
        res.json({ message: 'New student successfully registered to the ROXY database!' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to register student. Email might already exist.' });
    }
});

// Delete a student
app.delete('/api/students/delete/:id', async (req, res) => {
    try {
        const result = await pool.query('DELETE FROM students WHERE student_id = $1', [req.params.id]);
        if (result.rowCount === 0) return res.status(404).json({ error: 'Student ID not found.' });
        res.json({ message: 'Student successfully removed from registry.' });
    } catch (err) {
        res.status(500).json({ error: 'Cannot delete student: They currently have outstanding books on loan.' });
    }
});

// --- CIRCULATION ENDPOINTS ---

app.post('/api/issue', async (req, res) => {
    const { book_id, student_id } = req.body;
    try {
        const bookCheck = await pool.query('SELECT available_copies FROM books WHERE book_id = $1', [book_id]);
        if (bookCheck.rows.length === 0) return res.status(404).json({ error: 'Book not found.' });
        if (bookCheck.rows[0].available_copies <= 0) return res.status(400).json({ error: 'Out of stock.' });

        await pool.query('BEGIN');
        await pool.query('INSERT INTO issue_records (book_id, student_id) VALUES ($1, $2)', [book_id, student_id]);
        await pool.query('UPDATE books SET available_copies = available_copies - 1 WHERE book_id = $1', [book_id]);
        await pool.query('COMMIT');
        res.json({ message: 'Circulation authorization recorded on cloud registry!' });
    } catch (err) {
        await pool.query('ROLLBACK');
        res.status(500).json({ error: 'Transaction failed. Verify Student ID and Book ID exist.' });
    }
});

app.post('/api/return', async (req, res) => {
    const { issue_id } = req.body;
    try {
        const recordCheck = await pool.query('SELECT * FROM issue_records WHERE issue_id = $1 AND return_date IS NULL', [issue_id]);
        if (recordCheck.rows.length === 0) return res.status(404).json({ error: 'No active transaction record found.' });

        const record = recordCheck.rows[0];
        const issueDate = new Date(record.issue_date);
        const today = new Date();
        const diffDays = Math.ceil(Math.abs(today - issueDate) / (1000 * 60 * 60 * 24));
        const fine = diffDays > 7 ? (diffDays - 7) * 2.00 : 0.00;

        await pool.query('BEGIN');
        await pool.query('UPDATE issue_records SET return_date = CURRENT_DATE, fine_amount = $1 WHERE issue_id = $2', [fine, issue_id]);
        await pool.query('UPDATE books SET available_copies = available_copies + 1 WHERE book_id = $1', [record.book_id]);
        await pool.query('COMMIT');
        res.json({ message: 'Asset recovered successfully.', fine_amount: fine });
    } catch (err) {
        await pool.query('ROLLBACK');
        res.status(500).json({ error: 'Cloud return processing failed.' });
    }
});

app.get('/api/reports', async (req, res) => {
    try {
        const availableBooks = await pool.query('SELECT sum(available_copies) FROM books');
        const borrowedBooks = await pool.query('SELECT count(*) FROM issue_records WHERE return_date IS NULL');
        const activeLoans = await pool.query(`
            SELECT i.issue_id, b.title AS book_title, s.name AS student_name, i.issue_date 
            FROM issue_records i JOIN books b ON i.book_id = b.book_id JOIN students s ON i.student_id = s.student_id
            WHERE i.return_date IS NULL ORDER BY i.issue_id DESC
        `);
        
        const total_avail = availableBooks.rows[0].sum || 0;
        const total_borrowed = borrowedBooks.rows[0].count || 0;

        const logContent = `=== ROXY LIVE SNAPSHOT LOG ===\nTimestamp: ${new Date().toISOString()}\nAvailable Copies: ${total_avail}\nLoans Out: ${total_borrowed}\n==============================\n`;
        fs.appendFile('library_report.txt', logContent, (err) => { if (err) console.error(err); });

        res.json({ total_available: total_avail, total_borrowed: total_borrowed, logs: activeLoans.rows });
    } catch (err) {
        res.status(500).json({ error: 'Reporting pipeline query failed.' });
    }
});

app.listen(3000, () => console.log('Cloud-Linked Backend engine active on local port 3000'));
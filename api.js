const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const path = require('path');

const app = express();
const port = 3008;

const connectionString = process.env.DATABASE_URL || (() => {
    const user = process.env.POSTGRES_USER || 'postgres';
    const password = process.env.POSTGRES_PASSWORD || 'root@123'; // Replace with your actual password
    const host = process.env.POSTGRES_HOST || 'localhost';
    const port = process.env.POSTGRES_PORT || '5432';
    const database = process.env.POSTGRES_DB || 'Maha-AASTHA'; // Replace with your actual database name
    // encode password for URL if necessary
    const encodedPassword = encodeURIComponent(password);
    return `postgresql://${user}:${encodedPassword}@${host}:${port}/${database}`;
})();
const pool = new Pool({ connectionString });

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Test database connection
pool.on('connect', () => {
    console.log('Connected to PostgreSQL database');
});

pool.on('error', (err) => {
    console.error('Database connection error:', err);
});

// API Routes

// Submit grievance
app.post('/api/grievances', async (req, res) => {
    try {
        const {
            employeeId, employeeName, mobileNumber, designation, department,
            officeName, districtName, officialEmail, userRole, priority,
            issueTimestamp, issueCategory, issueSubCategory, issueRelated,
            issueSection, issueSubSection, subject, description, filesCount
        } = req.body;

    // Generate ticket number in short format: MAA-###### (6 digits)
    // Ensure uniqueness by checking the DB and regenerating up to 5 times
let ticket = null;
for (let attempt = 0; attempt < 5; attempt++) {
    // generate 8-character alphanumeric (hex) string
    const randomPart = Math.random().toString(16).substring(2, 10); 
    const candidate = `TKT-${randomPart}`;

    try {
        const existsRes = await pool.query(
            'SELECT 1 FROM public.grievancess WHERE ticket = $1 LIMIT 1',
            [candidate]
        );
        if (existsRes.rowCount === 0) {
            ticket = candidate;
            break;
        }
    } catch (err) {
        console.error('Error checking ticket uniqueness:', err);
        // try another candidate
    }
}
    if (!ticket) {
        // fallback: append timestamp
        ticket = `MAA-${Date.now()}`;
        console.warn('Could not generate a guaranteed-unique 6-digit ticket; using fallback:', ticket);
    }

        // Use the same table name as in database.py: public.grievancess
        const query = `
            INSERT INTO public.grievancess (
                ticket, employee_id, employee_name, mobile_number, designation,
                department, office_name, district_name, official_email, user_role,
                priority, issue_timestamp, issue_category, issue_sub_category,
                issue_related, issue_section, issue_sub_section, subject,
                description, files_count, status, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, NOW(), NOW())
            RETURNING *
        `;

        // Handle timestamp - use current time if not provided or empty
        const timestamp = issueTimestamp && issueTimestamp.trim() !== '' 
            ? new Date(issueTimestamp).toISOString() 
            : new Date().toISOString();

        const values = [
            ticket, employeeId, employeeName, mobileNumber, designation,
            department, officeName, districtName, officialEmail, userRole,
            priority, timestamp, issueCategory, issueSubCategory,
            issueRelated, issueSection, issueSubSection, subject,
            description, filesCount || 0, 'Open'
        ];

        const result = await pool.query(query, values);
        if (result && result.rows && result.rows[0]) {
            console.log('Inserted grievance ticket:', result.rows[0].ticket, 'id:', result.rows[0].id);
        }
        
        res.json({
            success: true,
            data: result.rows[0],
            message: 'Grievance submitted successfully'
        });

    } catch (error) {
        console.error('Error submitting grievance:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to submit grievance',
            error: error.message
        });
    }
});

// Get grievances by mobile number
app.get('/api/grievances/mobile/:mobileNumber', async (req, res) => {
    try {
        const { mobileNumber } = req.params;
        
        const query = `
            SELECT * FROM public.grievancess
            WHERE mobile_number = $1 
            ORDER BY created_at DESC 
            LIMIT 5
        `;
        
        const result = await pool.query(query, [mobileNumber]);
        
        res.json({
            success: true,
            data: result.rows,
            total: result.rows.length
        });

    } catch (error) {
        console.error('Error fetching grievances:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch grievances',
            error: error.message
        });
    }
});

// Get grievance by ticket number
app.get('/api/grievances/ticket/:ticket', async (req, res) => {
    try {
        const { ticket } = req.params;
        
        const query = `
            SELECT * FROM public.grievancess
            WHERE ticket = $1
        `;
        
        const result = await pool.query(query, [ticket]);
        
        if (result.rows.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Grievance not found'
            });
        }
        
        res.json({
            success: true,
            data: result.rows[0]
        });

    } catch (error) {
        console.error('Error fetching grievance:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch grievance',
            error: error.message
        });
    }
});

// Update grievance status
app.put('/api/grievances/:id/status', async (req, res) => {
    try {
        const { id } = req.params;
        const { status } = req.body;
        
        const query = `
            UPDATE public.grievancess
            SET status = $1, updated_at = CURRENT_TIMESTAMP 
            WHERE id = $2 
            RETURNING *
        `;
        
        const result = await pool.query(query, [status, id]);
        
        if (result.rows.length === 0) {
            return res.status(404).json({
                success: false,
                message: 'Grievance not found'
            });
        }
        
        res.json({
            success: true,
            data: result.rows[0],
            message: 'Status updated successfully'
        });

    } catch (error) {
        console.error('Error updating status:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to update status',
            error: error.message
        });
    }
});

// Get all grievances (admin)
app.get('/api/grievances', async (req, res) => {
    try {
        const { page = 1, limit = 10, status, category } = req.query;
        const offset = (page - 1) * limit;
        
    let query = 'SELECT * FROM public.grievancess';
        let conditions = [];
        let values = [];
        let paramCount = 0;
        
        if (status) {
            paramCount++;
            conditions.push(`status = $${paramCount}`);
            values.push(status);
        }
        
        if (category) {
            paramCount++;
            conditions.push(`issue_category = $${paramCount}`);
            values.push(category);
        }
        
        if (conditions.length > 0) {
            query += ' WHERE ' + conditions.join(' AND ');
        }
        
        query += ` ORDER BY created_at DESC LIMIT $${paramCount + 1} OFFSET $${paramCount + 2}`;
        values.push(limit, offset);
        
        const result = await pool.query(query, values);
        
        // Get total count
    let countQuery = 'SELECT COUNT(*) FROM public.grievancess';
        if (conditions.length > 0) {
            countQuery += ' WHERE ' + conditions.join(' AND ');
        }
        
        const countResult = await pool.query(countQuery, values.slice(0, -2));
        const total = parseInt(countResult.rows[0].count);
        
        res.json({
            success: true,
            data: result.rows,
            pagination: {
                page: parseInt(page),
                limit: parseInt(limit),
                total,
                pages: Math.ceil(total / limit)
            }
        });

    } catch (error) {
        console.error('Error fetching grievances:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch grievances',
            error: error.message
        });
    }
});

// Serve static files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/grievance.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'grievance.html'));
});

// Start server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
    // Log database connection info (mask password if present)
    try {
        const maskPassword = (connStr) => {
            // mask password between : and @ in connection string
            return connStr.replace(/(postgres(?:ql)?:\/\/[^:]+:)([^@]+)(@)/, (_, a, b, c) => `${a}*****${c}`);
        };
        console.log('Database connection string:', maskPassword(connectionString));
    } catch (e) {
        console.log('Database connection info not available');
    }
});

module.exports = app;

import asyncpg
import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import hashlib
import time
import secrets
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseManager:

    def __init__(self):
        self.pool = None
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            user = os.getenv('POSTGRES_USER', '')
            password = os.getenv('POSTGRES_PASSWORD', '')
            host = os.getenv('POSTGRES_HOST', '')
            port = os.getenv('POSTGRES_PORT', '')
            database = os.getenv('POSTGRES_DB', '')
            self.database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def save_ticket(self, form_data: dict) -> bool:
        """Save ticket from main.py form submission"""
        if not self.pool:
            logger.error("Database pool not initialized")
            return False
        
        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    ticket = form_data.get('ticket', '')
                    employee_id = form_data.get('employee_id', '')
                    employee_name = form_data.get('employee_name', 'Unknown')
                    designation = form_data.get('designation', '')
                    department = form_data.get('department', '')
                    office_name = form_data.get('office_name', '')
                    district_name = form_data.get('district_name', '')
                    mobile_number = form_data.get('mobile_number', '')
                    official_email = form_data.get('official_email', '')
                    user_role = form_data.get('user_role', 'Employee')
                    issue_category = form_data.get('issue_category', 'Other')
                    issue_sub_category = form_data.get('issue_sub_category', '')
                    subject = form_data.get('subject', 'No subject')
                    description = form_data.get('description', 'No description')
                    priority = form_data.get('priority', 'Low')
                    status = form_data.get('status', 'Open')
                    phone_number = form_data.get('phone_number', mobile_number)
                    created_at = form_data.get('created_at', datetime.now())
                    
                    select_module = form_data.get('select_module', '')
                    select_section = form_data.get('select_section', '')
                    select_sub_section = form_data.get('select_sub_section', '')
                    
                    priority_map = {
                        'Low': 'Low', 'कमी': 'Low',
                        'Medium': 'Medium', 'मध्यम': 'Medium',
                        'High': 'High', 'उच्च': 'High',
                        'Urgent': 'Urgent', 'तातडीचे': 'Urgent'
                    }
                    priority_value = priority_map.get(priority, 'Low')
                    
                    full_description = description
                    if select_module:
                        full_description += f"\n\nModule: {select_module}"
                    if select_section:
                        full_description += f"\nSection: {select_section}"
                    if select_sub_section:
                        full_description += f"\nSub-Section: {select_sub_section}"
                    
                    ticket_query = """
                        INSERT INTO public.grievancess (
                            ticket, employee_id, employee_name, mobile_number, 
                            official_email, designation, department, office_name,
                            district_name, user_role, priority, issue_timestamp,
                            issue_category, issue_sub_category, issue_related,
                            issue_section, issue_sub_section, subject, description,
                            status, files_count, created_at, updated_at
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
                            $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, NOW()
                        ) RETURNING id, ticket
                    """
                    
                    ticket_result = await connection.fetchrow(
                        ticket_query,
                        ticket, employee_id, employee_name, mobile_number,
                        official_email, designation, department, office_name,
                        district_name or None, user_role, priority_value, created_at,
                        issue_category, issue_sub_category or None,
                        select_module or None, select_section or None,
                        select_sub_section or None, subject, full_description,
                        status, 0, created_at
                    )
                    
                    ticket_db_id = ticket_result['id']
                    returned_ticket = ticket_result['ticket']
                    
                    logger.info(f"✅ Ticket saved successfully: {returned_ticket} (DB ID: {ticket_db_id}, Role: {user_role}, Priority: {priority_value})")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Failed to save ticket: {e}", exc_info=True)
            return False
    
    async def save_whatsapp_ticket(self, form_data: dict, phone_number: str) -> str:
        """Save WhatsApp form submission to grievancess table - SHORT FORMAT"""
        if not self.pool:
            logger.error("❌ Database pool not initialized")
            raise Exception("Database not available")
        
        try:
            logger.info(f"📝 Starting WhatsApp ticket save for phone: {phone_number}")
            
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    # Generate unique ticket ID - SHORT FORMAT (8 chars)
                    unique_id = secrets.token_hex(4)  # Generates 8 hex characters
                    ticket = f"TKT-{unique_id}"
                    
                    logger.info(f"🎫 Generated ticket ID: {ticket}")
                    
                    # Prepare data
                    employee_name = form_data.get('employee_name', 'Unknown')
                    employee_id = form_data.get('employee_id', '')
                    mobile_number = form_data.get('mobile_number', phone_number)
                    official_email = form_data.get('official_email', '')
                    designation = form_data.get('designation', '')
                    department = form_data.get('department', '')
                    office_name = form_data.get('office_name', '')
                    district_name = form_data.get('district_name', '')
                    user_role = form_data.get('user_role', 'Employee')
                    issue_category = form_data.get('issue_category', 'Other')
                    issue_sub_category = form_data.get('issue_sub_category', '')
                    
                    select_module = form_data.get('select_module', '')
                    select_section = form_data.get('select_section', '')
                    select_sub_section = form_data.get('select_sub_section', '')
                    
                    subject = form_data.get('subject', 'No subject')
                    description = form_data.get('description', 'No description')
                    priority = form_data.get('priority', 'Medium')
                    
                    priority_map = {
                        'Low': 'Low', 'कमी': 'Low',
                        'Medium': 'Medium', 'मध्यम': 'Medium',
                        'High': 'High', 'उच्च': 'High',
                        'Urgent': 'Urgent', 'तातडीचे': 'Urgent'
                    }
                    priority_value = priority_map.get(priority, 'Medium')
                    
                    full_description = description
                    if select_module:
                        full_description += f"\n\nModule: {select_module}"
                    if select_section:
                        full_description += f"\nSection: {select_section}"
                    if select_sub_section:
                        full_description += f"\nSub-Section: {select_sub_section}"
                    
                    logger.info(f"📊 Ticket data prepared - Category: {issue_category}, SubCat: {issue_sub_category}, Module: {select_module}")
                    
                    # Insert into grievancess table
                    grievances_query = """
                        INSERT INTO public.grievancess (
                            ticket, employee_id, employee_name, mobile_number, 
                            official_email, designation, department, office_name,
                            district_name, user_role, priority, issue_timestamp,
                            issue_category, issue_sub_category, issue_related,
                            issue_section, issue_sub_section, subject, description,
                            status, files_count, created_at, updated_at
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
                            $13, $14, $15, $16, $17, $18, $19, $20, $21, NOW(), NOW()
                        ) RETURNING id, ticket
                    """
                    
                    logger.info(f"💾 Executing INSERT query...")
                    
                    ticket_result = await connection.fetchrow(
                        grievances_query,
                        ticket, employee_id, employee_name, mobile_number,
                        official_email, designation, department, office_name,
                        district_name or None, user_role, priority_value,
                        datetime.now(), issue_category, issue_sub_category or None,
                        select_module or None, select_section or None,
                        select_sub_section or None, subject, full_description,
                        'Open', 0
                    )
                    
                    ticket_db_id = ticket_result['id']
                    returned_ticket = ticket_result['ticket']
                    
                    logger.info(f"✅ WhatsApp ticket saved to grievancess table: {returned_ticket} (DB ID: {ticket_db_id}, Role: {user_role}, Priority: {priority_value})")
                    
                    return returned_ticket
                    
        except Exception as e:
            logger.error(f"❌ Failed to save WhatsApp ticket: {e}", exc_info=True)
            raise Exception(f"Database save failed: {str(e)}")
    
    async def get_ticket_by_id(self, ticket: str) -> Optional[Dict[str, Any]]:
        """Get ticket by unique ID from grievancess table"""
        if not self.pool:
            logger.error("Database pool not initialized")
            return None
        
        try:
            async with self.pool.acquire() as connection:
                query = """
                    SELECT * FROM public.grievancess 
                    WHERE ticket = $1 OR ticket ILIKE $2
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                
                result = await connection.fetchrow(query, ticket, f"%{ticket}%")
                
                if result:
                    logger.info(f"✅ Ticket found in grievancess table: {ticket}")
                    return dict(result)
                else:
                    logger.info(f"❌ Ticket not found: {ticket}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching ticket: {e}")
            return None

    async def get_ticket_by_mobile(self, mobile_number: str) -> Optional[Dict[str, Any]]:
        """Get latest ticket by mobile number from grievancess table"""
        if not self.pool:
            logger.error("Database pool not initialized")
            return None
        
        try:
            async with self.pool.acquire() as connection:
                query = """
                    SELECT * FROM public.grievancess 
                    WHERE mobile_number = $1
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                
                result = await connection.fetchrow(query, mobile_number)
                
                if result:
                    logger.info(f"✅ Ticket found for mobile in grievancess table: {mobile_number}")
                    return dict(result)
                else:
                    logger.info(f"❌ No ticket found for mobile: {mobile_number}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching ticket by mobile: {e}")
            return None

    async def get_ticket_status(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get ticket status using ticket ID or mobile_number from grievancess table"""
        if not self.pool:
            return None
        
        try:
            identifier = identifier.strip()
            
            async with self.pool.acquire() as connection:
                query = """
                    SELECT id, ticket, employee_id, employee_name, mobile_number,
                           official_email, designation, department, office_name,
                           district_name, user_role, priority, issue_timestamp, issue_category,
                           issue_sub_category, issue_related, issue_section, issue_sub_section,
                           subject, description, status, created_at, updated_at
                    FROM public.grievancess
                    WHERE (ticket = $1 OR ticket ILIKE $2 OR mobile_number = $1)
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                
                result = await connection.fetchrow(query, identifier, f"%{identifier}%")
                
                if not result:
                    return None
                
                ticket_data = dict(result)
                
                status_map = {
                    'Open': 'Open',
                    'In Progress': 'In Progress',
                    'Resolved': 'Resolved',
                    'Closed': 'Closed',
                    'Pending': 'Pending'
                }
                
                current_status = ticket_data.get('status', 'Open')
                ticket_data['status'] = status_map.get(current_status, current_status)
                
                return ticket_data
                
        except Exception as e:
            logger.error(f"Error in get_ticket_status: {str(e)}")
            return None
        
    async def get_tickets_by_phone(self, phone_number: str) -> List[Dict[str, Any]]:
        """Get all tickets for a phone number from grievancess table"""
        if not self.pool:
            logger.error("Database pool not initialized")
            return []
        
        try:
            async with self.pool.acquire() as connection:
                query = """
                    SELECT * FROM public.grievancess
                    WHERE mobile_number = $1
                    ORDER BY created_at DESC
                    LIMIT 50
                """
                
                results = await connection.fetch(query, phone_number)
                tickets = [dict(row) for row in results]
                logger.info(f"Found {len(tickets)} tickets for phone {phone_number}")
                
                return tickets
                
        except Exception as e:
            logger.error(f"Error fetching tickets by phone: {e}")
            return []

    async def get_ticket_stats(self) -> Dict[str, Any]:
        """Get comprehensive ticket statistics from grievancess table"""
        if not self.pool:
            return {"error": "Database not available"}
        
        try:
            async with self.pool.acquire() as connection:
                stats_query = """
                    SELECT 
                        COUNT(*) as total_tickets,
                        COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_tickets,
                        COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress_tickets,
                        COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_tickets,
                        COUNT(CASE WHEN status = 'Closed' THEN 1 END) as closed_tickets,
                        COUNT(CASE WHEN DATE(created_at) >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recent_7days
                    FROM public.grievancess
                """
    
                result = await connection.fetchrow(stats_query)
                stats = dict(result) if result else {}
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting ticket stats: {e}")
            return {"error": str(e)}

    async def get_whatsapp_ticket_stats(self) -> Dict[str, Any]:
        """Get WhatsApp specific ticket statistics from grievancess table"""
        if not self.pool:
            return {"error": "Database not available"}
        
        try:
            async with self.pool.acquire() as connection:
                whatsapp_stats_query = """
                    SELECT 
                        COUNT(*) as total_whatsapp_tickets,
                        COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_whatsapp,
                        COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress_whatsapp,
                        COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_whatsapp,
                        COUNT(CASE WHEN status = 'Closed' THEN 1 END) as closed_whatsapp,
                        COUNT(CASE WHEN DATE(created_at) >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recent_whatsapp_7days
                    FROM public.grievancess
                    WHERE ticket LIKE 'TKT-%'
                """
                
                result = await connection.fetchrow(whatsapp_stats_query)
                return dict(result) if result else {"total_whatsapp_tickets": 0}
                    
        except Exception as e:
            logger.error(f"Error getting WhatsApp ticket stats: {e}")
            return {"error": str(e)}

    async def init_pool(self):
        """Initialize asyncpg connection pool with enhanced logging"""
        try:
            logger.info("🔌 Initializing database connection pool...")
            logger.info(f"📍 Database URL: {self.database_url.split('@')[1] if '@' in self.database_url else 'Unknown'}")
            
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={'application_name': 'maha_aastha_chatbot'}
            )
            
            async with self.pool.acquire() as conn:
                # Get current database name
                current_db = await conn.fetchval("SELECT current_database()")
                version = await conn.fetchval("SELECT version()")
                
                logger.info(f"✅ Database connection pool initialized")
                logger.info(f"📊 PostgreSQL Version: {version.split(',')[0]}")
                logger.info(f"🗄️  Connected to database: {current_db}")
                
                # Test if grievancess table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'grievancess'
                    )
                """)
                
                if table_exists:
                    logger.info("✅ grievancess table exists and ready")
                    
                    # Count total columns
                    column_count = await conn.fetchval("""
                        SELECT COUNT(*) 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'grievancess'
                    """)
                    logger.info(f"✅ grievancess table has {column_count} columns")
                    
                    # Check if ticket column exists
                    ticket_column_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'grievancess' 
                            AND column_name = 'ticket'
                        )
                    """)
                    
                    if ticket_column_exists:
                        logger.info("✅ Ticket column exists in grievancess table")
                    else:
                        logger.error("❌ CRITICAL: Ticket column NOT found in grievancess table!")
                    
                    # Check if NEW subcategory columns exist
                    subcategory_columns = ['issue_related', 'issue_section', 'issue_sub_section']
                    for col in subcategory_columns:
                        col_exists = await conn.fetchval("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.columns 
                                WHERE table_schema = 'public' 
                                AND table_name = 'grievancess' 
                                AND column_name = $1
                            )
                        """, col)
                        
                        if col_exists:
                            logger.info(f"✅ Column '{col}' exists in grievancess table")
                        else:
                            logger.warning(f"⚠️  Column '{col}' NOT found in grievancess table! Creating it...")
                            try:
                                await conn.execute(f"""
                                    ALTER TABLE public.grievancess 
                                    ADD COLUMN IF NOT EXISTS {col} TEXT
                                """)
                                logger.info(f"✅ Column '{col}' created successfully")
                            except Exception as e:
                                logger.error(f"❌ Failed to create column '{col}': {e}")
                else:
                    logger.error("❌ CRITICAL: grievancess table NOT FOUND!")
                    logger.error(f"❌ Current database: {current_db}")
                    logger.error("❌ Please create the grievancess table or check DATABASE_URL")
                    
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}", exc_info=True)
            raise Exception("Database pool initialization failed")

    async def close_pool(self):
        """Close the connection pool gracefully"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def test_connection(self) -> bool:
        """Test database connectivity"""
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                return True
        except Exception as e:
            logger.error("Database connection test failed:", exc_info=True)
            return False

    async def get_database_info(self) -> Dict[str, Any]:
        """Get database and pool information"""
        if not self.pool:
            return {"connected": False}
        try:
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                db_name = await conn.fetchval("SELECT current_database()")
                user = await conn.fetchval("SELECT current_user")
                try:
                    conn_count = await conn.fetchval("SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'")
                except Exception:
                    conn_count = 0
                
                pool_info = {}
                try:
                    pool_info = {
                        "pool_max_size": getattr(self.pool, '_maxsize', 'unknown'),
                        "pool_min_size": getattr(self.pool, '_minsize', 'unknown'),
                        "pool_current_size": len(getattr(self.pool, '_con', []))
                            if hasattr(self.pool, '_con') else 'unknown'
                    }
                except Exception:
                    pool_info = {"pool_info": "unavailable"}
                
                return {
                    "connected": True,
                    "database_name": db_name,
                    "user": user,
                    "version": version,
                    "active_connections": conn_count,
                    **pool_info
                }
        except Exception as e:
            logger.error("Error getting database info:", exc_info=True)
            return {"connected": False, "error": str(e)}

    async def get_table_list(self) -> List[str]:
        """List all tables in public schema"""
        if not self.pool:
            return []
        try:
            async with self.pool.acquire() as conn:
                return [
                    row['table_name']
                    for row in await conn.fetch(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public' ORDER BY table_name"
                    )
                ]
        except Exception as e:
            logger.error("Error getting table list:", exc_info=True)
            return []

    async def check_table_structure(self, table_name: str) -> List[str]:
        """List columns in a table"""
        if not self.pool:
            return []
        try:
            async with self.pool.acquire() as conn:
                return [
                    row['column_name']
                    for row in await conn.fetch(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = $1 AND table_schema = 'public' "
                        "ORDER BY ordinal_position", table_name
                    )
                ]
        except Exception as e:
            logger.error(f"Error checking structure for {table_name}:", exc_info=True)
            return []

# Global Singleton Manager
db_manager = DatabaseManager()

async def init_database():
    """Initialize the database connection pool"""
    await db_manager.init_pool()

async def close_database():
    """Close the database connection pool"""
    await db_manager.close_pool()

async def get_ticket_status(identifier: str) -> Optional[Dict[str, Any]]:
    """Get ticket status by either ticket ID or mobile_number"""
    return await db_manager.get_ticket_status(identifier)

async def test_db_connection() -> bool:
    """Test database connection (wrapper)"""
    return await db_manager.test_connection()

async def get_db_info() -> Dict[str, Any]:
    """Get database info (wrapper)"""
    return await db_manager.get_database_info()

async def get_db_tables() -> List[str]:
    """Get list of tables (wrapper)"""
    return await db_manager.get_table_list()

async def check_table_columns(table_name: str) -> List[str]:
    """Get table columns (wrapper)"""
    return await db_manager.check_table_structure(table_name)

async def save_whatsapp_ticket(form_data: dict, phone_number: str) -> str:
    """Save WhatsApp form submission (wrapper)"""
    return await db_manager.save_whatsapp_ticket(form_data, phone_number)

async def get_whatsapp_stats() -> Dict[str, Any]:
    """Get WhatsApp ticket statistics (wrapper)"""
    return await db_manager.get_whatsapp_ticket_stats()

async def get_ticket_by_id(ticket: str) -> Optional[Dict[str, Any]]:
    """Get ticket by unique ID (wrapper)"""
    return await db_manager.get_ticket_by_id(ticket)

async def get_ticket_by_mobile(mobile_number: str) -> Optional[Dict[str, Any]]:
    """Get latest ticket by mobile number (wrapper)"""
    return await db_manager.get_ticket_by_mobile(mobile_number)

async def get_tickets_by_phone(phone_number: str) -> List[Dict[str, Any]]:
    """Get all tickets for a phone number (wrapper)"""
    return await db_manager.get_tickets_by_phone(phone_number)
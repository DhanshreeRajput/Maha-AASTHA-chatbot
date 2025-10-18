from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional, List, Dict, Any
import time
import os
import logging
import re
import csv
import io
from datetime import datetime
from contextlib import asynccontextmanager
from database import (
    db_manager,
    init_database,
    close_database,
    get_ticket_status,
    get_tickets_by_phone,
    test_db_connection,
    get_db_info
)

# === CONFIGURATION ===
LOG_FILENAME = os.path.join(os.path.dirname(__file__), 'chatbot.log')

# Configure root logger with both console and rotating file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Rotating file handler (keeps logs in chatbot.log)
try:
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as e:
    # Fallback to simple FileHandler if RotatingFileHandler not available for some reason
    fh = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logger.propagate = False

# Helper to log chat interactions in a consistent format
def log_chat(session_id: Optional[str], user_input: str, assistant_reply: str, language: str = 'en', endpoint: str = '/query/'):
    """Write a concise single-line log for each chat interaction."""
    try:
        sid = session_id if session_id else 'N/A'
        # Keep the logged lines compact but informative
        logger.info(f"[CHAT] endpoint={endpoint} session_id={sid} language={language} user_input={user_input} assistant_reply={assistant_reply}")
    except Exception as e:
        logger.error(f"Failed to write chat log: {e}")

RATE_LIMIT_SECONDS = 2
SUPPORTED_LANGUAGES = ["en", "mr"]

SYSTEM_STATUS = {
    "startup_time": time.time(),
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "last_error": None,
    "supported_languages": SUPPORTED_LANGUAGES,
    "database_connected": False
}

# Global in-memory stores (in production, use Redis or similar)
CHAT_HISTORY = {}
USER_SESSION_STATE = {}
RATINGS_DATA = []
RATE_LIMIT_TRACKER = {}

# === MODELS & VALIDATION ===
class QueryRequest(BaseModel):
    input_text: str
    session_id: Optional[str] = None
    language: str = "en"

    @field_validator('input_text')
    @classmethod
    def validate_input_text(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Input text cannot be empty')
        if len(v) > 500:
            raise ValueError('Input text too long (max 500 characters)')
        return v

    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f'Language must be one of: {SUPPORTED_LANGUAGES}')
        return v

class RatingRequest(BaseModel):
    rating: int
    session_id: Optional[str] = None
    language: str = "en"
    ticket_id: Optional[str] = None
    feedback_text: Optional[str] = None

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v not in [1, 2, 3, 4, 5]:
            raise ValueError('Rating must be between 1 and 5')
        return v

class TicketStatusRequest(BaseModel):
    ticket_id: str
    language: str = "en"

    @field_validator('ticket_id')
    @classmethod
    def validate_ticket_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Ticket ID cannot be empty')
        return v.strip()

class UserSearchRequest(BaseModel):
    user_identifier: str
    language: str = "en"

    @field_validator('user_identifier')
    @classmethod
    def validate_user_identifier(cls, v):
        if not v or not v.strip():
            raise ValueError('User identifier cannot be empty')
        return v.strip()

# === LANGUAGE RESOURCES ===
RATING_LABELS = {
    "en": {1: "Poor", 2: "Fair", 3: "Good", 4: "Very Good", 5: "Excellent"},
    "mr": {1: "खराब", 2: "सामान्य", 3: "चांगले", 4: "खूप चांगले", 5: "उत्कृष्ट"}
}

MAHA_AASTHA_KNOWLEDGE_BASE = {
    "en": {
        "welcome_message": "Welcome to Maha Aastha Grievance Redressal System AI-ChatBot.",
        "initial_question": "Would you like to register a Ticket on the Maha Aastha Grievance Redressal System?",
        "check_existing_question": "Has a Ticket already been registered on the Maha Aastha Grievance Redressal System?",
        "status_check_question": "Would you like to check the status of the ticket which you have registered on the Maha Aastha Grievance Redressal System?",
        "ticket_id_prompt": "Please enter your Ticket ID (For example: \"TKT-12345678\")",
        "feedback_question": "Would you like to provide feedback regarding the resolution of your ticket addressed through the Maha Aastha Grievance Redressal System?",
        "rating_question": "Please rate your experience with the Maha Aastha Grievance Redressal System:",
        "rating_request": "Rate from 1 (Poor) to 5 (Excellent)",
        "invalid_rating": "The information you have entered is invalid. Please try again.",
        "rating_thank_you": "Thank you for your feedback. Your rating has been recorded.",
        "ticket_not_found": "Sorry, no ticket found with the provided ID. Please check your Ticket ID and try again.",
        "database_error": "Unable to fetch ticket information at the moment. Please try again later.",
        "invalid_ticket_id": "Please provide a valid Ticket ID in the correct format (For example: \"TKT-12345678\")",
        "options": {"yes": "YES", "no": "NO"},
        "yes_response": {
            "intro": "You can register your Ticket on the Maha Aastha Grievance Redressal System through below link:",
            "link": "#grievance"
        },
        "no_response": "Thank you for using the Maha Aastha Grievance Redressal System.",
        "help_text": "Please type 'YES' or 'NO' to proceed with your query.",
        "track_ticket_help": "You can also track your ticket status at: #view-ticket"
    },
    "mr": {
        "welcome_message": "नमस्कार, महा आस्था तक्रार निवारण प्रणाली एआय-चॅटबॉटमध्ये आपले स्वागत आहे.",
        "initial_question": "महा आस्था तक्रार निवारण प्रणालीमध्ये आपण तिकीट नोंदवू इच्छिता का?",
        "check_existing_question": "महा आस्था तक्रार निवारण प्रणालीमध्ये नोंदविण्यात आलेली तिकीट आहे का?",
        "status_check_question": "आपण महा आस्था तक्रार निवारण प्रणालीमध्ये नोंदवलेल्या तिकीटची स्थिती तपासू इच्छिता का?",
        "ticket_id_prompt": "कृपया आपला तिकीट क्रमांक प्रविष्ट करा (उदाहरणार्थ: \"TKT-12345678\")",
        "feedback_question": "महा आस्था तक्रार निवारण प्रणालीद्वारे सोडविण्यात आलेल्या आपल्या तिकीटच्या निराकरणाबाबत अभिप्राय द्यायला इच्छिता का?",
        "rating_question": "कृपया महा आस्था तक्रार निवारण प्रणालीच्या अनुभवाला रेटिंग द्या:",
        "rating_request": "१ (खराब) ते ५ (उत्कृष्ट) पर्यंत रेटिंग द्या",
        "invalid_rating": "आपण दिलेली माहिती अवैध आहे. कृपया पुन्हा प्रयत्न करा.",
        "rating_thank_you": "आपल्या अभिप्रायाबद्दल धन्यवाद. आपले रेटिंग नोंदवले गेले आहे.",
        "ticket_not_found": "माफ करा, दिलेल्या क्रमांकाशी कोणतीही तिकीट आढळली नाही. कृपया आपला तिकीट क्रमांक तपासा आणि पुन्हा प्रयत्न करा.",
        "database_error": "सध्या तिकीट माहिती मिळवता येत नाही. कृपया नंतर प्रयत्न करा.",
        "invalid_ticket_id": "कृपया योग्य तिकीट क्रमांक प्रदान करा (उदाहरणार्थ: \"TKT-12345678\")",
        "options": {"yes": "होय", "no": "नाही"},
        "yes_response": {
            "intro": "आपण महा आस्था तक्रार निवारण प्रणालीमध्ये आपली तिकीट खालील लिंकद्वारे नोंदवू शकता:",
            "link": "#grievance"
        },
        "no_response": "महा आस्था तक्रार निवारण प्रणालीचा वापर केल्याबद्दल आपले धन्यवाद.",
        "help_text": "कृपया 'होय' किंवा 'नाही' टाइप करून आपल्या प्रश्नासह पुढे जा.",
        "track_ticket_help": "आपण आपल्या तिकीटची स्थिती येथे देखील तपासू शकता: #view-ticket"
    }
}

def generate_session_id() -> str:
    """Generate a unique session ID"""
    import random
    adjectives = ["sharp", "sleepy", "fluffy", "dazzling", "crazy", "bold", "happy", "silly"]
    animals = ["lion", "swan", "tiger", "elephant", "zebra", "giraffe", "panda", "koala"]
    return f"{random.choice(adjectives)}_{random.choice(animals)}_{os.urandom(2).hex()}_{int(time.time())}"

def add_to_chat_history(session_id: str, user_msg: str, bot_msg: str, language: str = "en"):
    """Add message to chat history with language support."""
    try:
        if session_id not in CHAT_HISTORY:
            CHAT_HISTORY[session_id] = []
        CHAT_HISTORY[session_id].insert(0, {
            "user": user_msg,
            "assistant": bot_msg,
            "language": language,
            "timestamp": time.strftime("%H:%M:%S"),
            "session_id": session_id,
            "created_at": time.time()
        })
        CHAT_HISTORY[session_id] = CHAT_HISTORY[session_id][:50]
    except Exception as e:
        logger.error(f"Failed to add to chat history: {e}")

def save_rating_data(rating: int, session_id: str, language: str, ticket_id: str = None, feedback_text: str = None) -> bool:
    """Save rating data for CSV export with proper UTF-8 handling."""
    try:
        ratings_dir = os.path.join(os.path.dirname(__file__), 'ratings_data')
        try:
            os.makedirs(ratings_dir, mode=0o755, exist_ok=True)
        except PermissionError:
            ratings_dir = os.path.dirname(__file__)
            logger.warning("Could not create ratings_data directory, using current directory")

        timestamp_str = datetime.now().strftime("%Y%m%d")
        csv_filename = f'ratings_log_{timestamp_str}.csv'
        csv_path = os.path.join(ratings_dir, csv_filename)

        rating_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": session_id,
            "rating": rating,
            "Feedback": RATING_LABELS[language][rating],
            "language": language,
            "ticket_id": ticket_id or "N/A"
        }

        file_exists = os.path.exists(csv_path)
        try:
            with open(csv_path, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=rating_entry.keys())
                if not file_exists or os.path.getsize(csv_path) == 0:
                    writer.writeheader()
                writer.writerow(rating_entry)
        except (PermissionError, OSError) as file_error:
            import tempfile
            temp_dir = tempfile.gettempdir()
            alternative_path = os.path.join(temp_dir, f'maha_aastha_ratings_{timestamp_str}.csv')
            alt_file_exists = os.path.exists(alternative_path)
            with open(alternative_path, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=rating_entry.keys())
                if not alt_file_exists or os.path.getsize(alternative_path) == 0:
                    writer.writeheader()
                writer.writerow(rating_entry)
            logger.info(f"Rating saved to alternative location: {alternative_path}")

        RATINGS_DATA.append(rating_entry)
        logger.info(f"Rating saved successfully: {rating}/5 ({RATING_LABELS[language][rating]}) for session {session_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving rating data: {e}")
        try:
            rating_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "session_id": session_id,
                "rating": rating,
                "Feedback": RATING_LABELS[language][rating],
                "language": language,
                "ticket_id": ticket_id or "N/A"
            }
            RATINGS_DATA.append(rating_entry)
            logger.info(f"Rating saved to memory only: {rating}/5 for session {session_id}")
            return True
        except Exception as memory_error:
            logger.error(f"Failed to save rating even to memory: {memory_error}")
            return False

def detect_greeting(text: str) -> tuple[bool, str]:
    """Detect greeting intent and return a normalized key."""
    try:
        t = text.strip().lower()
        t = re.sub(r"[!.,🙂🙏✨⭐️]+", "", t)
        patterns = [
            (r"\bgood\s*morning\b|\bशुभ\s*सकाळ\b", "good_morning"),
            (r"\bgood\s*afternoon\b|\bशुभ\s*दुपार\b", "good_afternoon"),
            (r"\bgood\s*evening\b|\bशुभ\s*संध्याकाळ\b", "good_evening"),
            (r"\bhello\b|\bhey+\b|\bhii+\b|\bhi\b|\bनमस्ते\b|\bनमस्कार\b|\bहॅलो\b|\bहेलो\b|\bहाय\b", "hello"),
            (r"\bgood\s*night\b|\bशुभ\s*रात्री\b", "good_night"),
        ]
        for regex, key in patterns:
            if re.search(regex, t):
                return True, key
        return False, ""
    except Exception:
        return False, ""

def detect_ticket_id(text: str) -> Optional[str]:
    """Detect potential ticket ID in text."""
    patterns = [
        r'\b(TKT-[a-zA-Z0-9]+)\b',
        r'\b(TKT[0-9a-zA-Z]+)\b',
        r'\b([0-9]{6,})\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def validate_ticket_id_format(ticket_id: str) -> bool:
    """Validate if the ticket ID matches expected Maha Aastha format."""
    valid_patterns = [
        r'^TKT-[a-zA-Z0-9]{6,}$',
        r'^TKT[0-9a-zA-Z]{6,}$',
        r'^[0-9]{6,}$'
    ]
    for pattern in valid_patterns:
        if re.match(pattern, ticket_id.strip(), re.IGNORECASE):
            return True
    return False

def detect_mobile_number(text: str) -> Optional[str]:
    """Detect Indian mobile number patterns in text."""
    clean_text = re.sub(r'[^\d+\s]', '', text)
    
    patterns = [
        r'\b(\+91[\s-]?)?([6-9]\d{9})\b',
        r'\b([6-9]\d{9})\b',
        r'\b(0\d{10})\b'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, clean_text)
        for match in matches:
            if match.group(1) and match.group(2):
                mobile = match.group(2)
            elif match.group(1):
                mobile = match.group(1)
            else:
                mobile = match.group(0)[1:]
            
            if len(mobile) == 10 and mobile[0] in '6789':
                return mobile
    
    return None

def validate_mobile_number_format(mobile_number: str) -> bool:
    """Validate if the mobile number matches Indian format."""
    digits_only = re.sub(r'\D', '', mobile_number)
    
    if len(digits_only) == 10 and digits_only[0] in '6789':
        return True
    
    if len(digits_only) == 12 and digits_only.startswith('91') and digits_only[2] in '6789':
        return True
    
    if len(digits_only) == 11 and digits_only.startswith('0') and digits_only[1] in '6789':
        return True
        
    return False

def detect_ticket_id_or_mobile(text: str) -> tuple[Optional[str], str]:
    """
    Detect either ticket ID or mobile number and return the type
    Returns: (identifier, type) where type is 'ticket_id', 'mobile_number', or None
    """
    ticket_id = detect_ticket_id(text)
    if ticket_id and validate_ticket_id_format(ticket_id):
        return ticket_id, 'ticket_id'
    
    mobile_number = detect_mobile_number(text)
    if mobile_number and validate_mobile_number_format(mobile_number):
        return mobile_number, 'mobile_number'
    
    return None, None

def detect_exact_status_question(text: str, language: str) -> bool:
    """Detect the exact status check question."""
    text_lower = text.lower().strip()
    if language == "en":
        return "would you like to check the status of your ticket" in text_lower or "check status" in text_lower
    else:
        status_patterns = [
            "आपण महा आस्था तक्रार निवारण प्रणालीमध्ये नोंदवलेल्या तिकीटची स्थिती तपासू इच्छिता का",
            "तिकीटची स्थिती तपासू इच्छिता का",
            "स्थिती तपासू इच्छिता का",
            "तिकीटची स्थिती",
            "स्थिती तपासा"
        ]
        return any(pattern in text for pattern in status_patterns)

def greeting_reply(language: str, key: str) -> str:
    """Return a specific greeting reply per detected key and language."""
    KB = MAHA_AASTHA_KNOWLEDGE_BASE[language]
    replies = {
        "en": {
            "good_morning": f"Good Morning! {KB['welcome_message']}",
            "good_afternoon": f"Good Afternoon! {KB['welcome_message']}",
            "good_evening": f"Good Evening! {KB['welcome_message']}",
            "good_night": f"Good Night! {KB['welcome_message']}",
            "hello": f"Hello! {KB['welcome_message']}",
        },
        "mr": {
            "good_morning": f"शुभ सकाळ! {KB['welcome_message']}",
            "good_afternoon": f"शुभ दुपार! {KB['welcome_message']}",
            "good_evening": f"शुभ संध्याकाळ! {KB['welcome_message']}",
            "good_night": f"शुभ रात्री! {KB['welcome_message']}",
            "hello": KB["welcome_message"],
        }
    }
    return replies.get(language, {}).get(key, replies["en"]["hello"])

def detect_yes_no_response(text: str, language: str) -> str:
    """Detect yes/no responses in both languages."""
    text = text.strip().lower()
    yes_patterns_en = [r'\byes\b', r'\by\b', r'\byeah\b', r'\byep\b']
    no_patterns_en = [r'\bno\b', r'\bn\b', r'\bnope\b']
    yes_patterns_mr = [r'\bहोय\b', r'\bहो\b']
    no_patterns_mr = [r'\bनाही\b', r'\bना\b']
    for pattern in yes_patterns_en + yes_patterns_mr:
        if re.search(pattern, text):
            return "yes"
    for pattern in no_patterns_en + no_patterns_mr:
        if re.search(pattern, text):
            return "no"
    return "unknown"

def format_simple_ticket_status(ticket_data: dict, language: str) -> str:
    """Format ticket status data into a readable message."""
    if not ticket_data:
        return "Ticket not found" if language == "en" else "तिकीट आढळले नाही"

    created_date = (
        ticket_data["created_at"].strftime("%d-%b-%Y")
        if ticket_data.get("created_at")
        else "Not available"
    )
    updated_date = (
        ticket_data["updated_at"].strftime("%d-%b-%Y")
        if ticket_data.get("updated_at")
        else None
    )

    if language == "en":
        status_message = f"""The current status of your Ticket is as follows:
Ticket ID: {ticket_data['ticket']}
Status: {ticket_data['status']}
Created: {created_date}
Employee Name: {ticket_data.get('employee_name', 'N/A')}
Category: {ticket_data.get('issue_category', 'N/A')}"""
        if ticket_data.get('district_name'):
            status_message += f"\nDistrict: {ticket_data['district_name']}"
        if ticket_data.get('office_name'):
            status_message += f"\nOffice: {ticket_data['office_name']}"
        if ticket_data.get('subject'):
            status_message += f"\nSubject: {ticket_data['subject']}"
        if updated_date:
            status_message += f"\nLast Updated: {updated_date}"
    else:
        status_message = f"""आपल्या तिकीटची सद्यस्थिती खालीलप्रमाणे आहे:
तिकीट क्रमांक: {ticket_data['ticket']}
स्थिती: {ticket_data['status']}
दाखल दिनांक: {created_date}
कर्मचारी नाव: {ticket_data.get('employee_name', 'निर्दिष्ट नाही')}
श्रेणी: {ticket_data.get('issue_category', 'निर्दिष्ट नाही')}"""
        if ticket_data.get('district_name'):
            status_message += f"\nजिल्हा: {ticket_data['district_name']}"
        if ticket_data.get('office_name'):
            status_message += f"\nकार्यालय: {ticket_data['office_name']}"
        if ticket_data.get('subject'):
            status_message += f"\nविषय: {ticket_data['subject']}"
        if updated_date:
            status_message += f"\nशेवटचा अद्यतन: {updated_date}"

    return status_message

def get_initial_response_with_status_option(language: str) -> str:
    """Get enhanced initial response with status check option."""
    kb = MAHA_AASTHA_KNOWLEDGE_BASE[language]
    if language == "mr":
        return f"""{kb['welcome_message']}
प्रश्न क्र. १: {kb['initial_question']}
उत्तर १ - "{kb['options']['yes']}"
उत्तर २ - "{kb['options']['no']}"
प्रश्न क्र. २: {kb['status_check_question']}
उत्तर - "स्थिती तपासा" किंवा आपला तिकीट क्रमांक टाइप करा
उदाहरण: TKT-12345678"""
    else:
        return f"""{kb['welcome_message']}
Question 1: {kb['initial_question']}
Answer 1: "{kb['options']['yes']}"
Answer 2: "{kb['options']['no']}"
Question 2: {kb['status_check_question']}
Answer: Type "Check Status" or enter your Ticket ID
Example: TKT-12345678"""

def get_feedback_question(language: str) -> str:
    """Get the feedback question."""
    kb = MAHA_AASTHA_KNOWLEDGE_BASE[language]
    if language == "mr":
        return f"""प्रश्न क्र. २.२: {kb['feedback_question']}
उत्तर १ - "{kb['options']['yes']}"
उत्तर २ - "{kb['options']['no']}\""""
    else:
        return f"""Question 2.2: {kb['feedback_question']}
Answer 1: "{kb['options']['yes']}"
Answer 2: "{kb['options']['no']}\""""

def get_rating_request(language: str) -> str:
    """Get the rating request message."""
    kb = MAHA_AASTHA_KNOWLEDGE_BASE[language]
    if language == "mr":
        return f"""{kb['rating_question']}
{kb['rating_request']}
१ - {RATING_LABELS['mr'][1]}
२ - {RATING_LABELS['mr'][2]}
३ - {RATING_LABELS['mr'][3]}
४ - {RATING_LABELS['mr'][4]}
५ - {RATING_LABELS['mr'][5]}"""
    else:
        return f"""{kb['rating_question']}
{kb['rating_request']}
1 - {RATING_LABELS['en'][1]}
2 - {RATING_LABELS['en'][2]}
3 - {RATING_LABELS['en'][3]}
4 - {RATING_LABELS['en'][4]}
5 - {RATING_LABELS['en'][5]}"""

async def process_maha_aastha_query(input_text: str, session_id: str, language: str) -> str:
    """Process user queries for the Maha Aastha system."""
    logger.info(f"Processing query: {input_text} for session: {session_id} in language: {language}")

    identifier, identifier_type = detect_ticket_id_or_mobile(input_text)
    
    if identifier and identifier_type:
        logger.info(f"Detected {identifier_type}: {identifier}")
        try:
            ticket_data = await db_manager.get_ticket_status(identifier)
            if ticket_data:
                logger.info(f"Found ticket data for {identifier_type}: {ticket_data}")
                status_response = format_simple_ticket_status(ticket_data, language)
                
                if identifier_type == 'mobile_number':
                    if language == "mr":
                        status_response += f"\n\n📱 मोबाइल नंबरद्वारे शोधले गेले: {identifier}"
                    else:
                        status_response += f"\n\n📱 Found using mobile number: {identifier}"
                
                status_response += f"\n\n🔗 {MAHA_AASTHA_KNOWLEDGE_BASE[language]['track_ticket_help']}"
                return status_response
            else:
                if identifier_type == 'mobile_number':
                    if language == "mr":
                        return f"माफ करा, {identifier} या मोबाइल नंबरसाठी कोणतीही तिकीट आढळली नाही. कृपया आपला तिकीट क्रमांक किंवा नोंदणीकृत मोबाइल नंबर तपासा."
                    else:
                        return f"Sorry, no ticket found for mobile number {identifier}. Please check your ticket ID or registered mobile number."
                else:
                    return MAHA_AASTHA_KNOWLEDGE_BASE[language]["ticket_not_found"]
        except Exception as e:
            logger.error(f"Error fetching ticket status: {e}")
            return MAHA_AASTHA_KNOWLEDGE_BASE[language]["database_error"]

    if session_id not in USER_SESSION_STATE:
        USER_SESSION_STATE[session_id] = {"stage": "initial", "language": language}
    session_state = USER_SESSION_STATE[session_id]

    response_type = detect_yes_no_response(input_text, language)

    if detect_exact_status_question(input_text, language):
        identifier, identifier_type = detect_ticket_id_or_mobile(input_text)
        
        if identifier and (validate_ticket_id_format(identifier) or validate_mobile_number_format(identifier)):
            try:
                ticket_data = await get_ticket_status(identifier)
                if ticket_data:
                    session_state["stage"] = "status_shown"
                    status_response = format_simple_ticket_status(ticket_data, language)
                    
                    if identifier_type == 'mobile_number':
                        if language == "mr":
                            status_response += f"\n\n📱 मोबाइल नंबरद्वारे शोधले गेले: {identifier}"
                        else:
                            status_response += f"\n\n📱 Found using mobile number: {identifier}"
                    
                    status_response += f"\n\n🔗 {MAHA_AASTHA_KNOWLEDGE_BASE[language]['track_ticket_help']}"
                    return status_response
                else:
                    if identifier_type == 'mobile_number':
                        if language == "mr":
                            return f"माफ करा, {identifier} या मोबाइल नंबरसाठी कोणतीही तिकीट आढळली नाही."
                        else:
                            return f"Sorry, no ticket found for mobile number {identifier}."
                    else:
                        return MAHA_AASTHA_KNOWLEDGE_BASE[language]["ticket_not_found"]
            except Exception as e:
                logger.error(f"Error fetching ticket status: {e}")
                return MAHA_AASTHA_KNOWLEDGE_BASE[language]["database_error"]
        else:
            session_state["stage"] = "waiting_for_ticket_id"
            if language == "mr":
                return f"""{MAHA_AASTHA_KNOWLEDGE_BASE[language]["ticket_id_prompt"]}
किंवा आपला नोंदणीकृत मोबाइल नंबर प्रविष्ट करा (उदाहरणार्थ: 9876543210)"""
            else:
                return f"""{MAHA_AASTHA_KNOWLEDGE_BASE[language]["ticket_id_prompt"]}
Or enter your registered mobile number (Example: 9876543210)"""

    if session_state.get("stage") == "waiting_for_ticket_id":
        identifier, identifier_type = detect_ticket_id_or_mobile(input_text)
        
        if identifier and (validate_ticket_id_format(identifier) or validate_mobile_number_format(identifier)):
            try:
                ticket_data = await get_ticket_status(identifier)
                if ticket_data:
                    session_state["stage"] = "status_shown"
                    status_response = format_simple_ticket_status(ticket_data, language)
                    
                    if identifier_type == 'mobile_number':
                        if language == "mr":
                            status_response += f"\n\n📱 मोबाइल नंबरद्वारे शोधले गेले: {identifier}"
                        else:
                            status_response += f"\n\n📱 Found using mobile number: {identifier}"
                    
                    status_response += f"\n\n🔗 {MAHA_AASTHA_KNOWLEDGE_BASE[language]['track_ticket_help']}"
                    return status_response
                else:
                    if identifier_type == 'mobile_number':
                        if language == "mr":
                            return f"माफ करा, {identifier} या मोबाइल नंबरसाठी कोणतीही तिकीट आढळली नाही."
                        else:
                            return f"Sorry, no ticket found for mobile number {identifier}."
                    else:
                        return MAHA_AASTHA_KNOWLEDGE_BASE[language]["ticket_not_found"]
            except Exception as e:
                logger.error(f"Error fetching ticket status: {e}")
                return MAHA_AASTHA_KNOWLEDGE_BASE[language]["database_error"]
        else:
            if language == "mr":
                return "कृपया योग्य तिकीट क्रमांक किंवा 10-अंकी मोबाइल नंबर प्रदान करा."
            else:
                return "Please provide a valid Ticket ID or 10-digit mobile number."

    if "feedback" in input_text.lower() or "अभिप्राय" in input_text.lower():
        session_state["stage"] = "feedback_question"
        return get_feedback_question(language)

    if session_state.get("stage") == "feedback_question":
        if response_type == "yes":
            session_state["stage"] = "rating_request"
            return get_rating_request(language)
        elif response_type == "no":
            session_state["stage"] = "completed"
            return MAHA_AASTHA_KNOWLEDGE_BASE[language]["no_response"]
        else:
            return MAHA_AASTHA_KNOWLEDGE_BASE[language]["help_text"]

    if (
        session_state["stage"] == "initial"
        or any(
            kw in input_text.lower()
            for kw in ["register", "ticket", "complaint", "तिकीट", "नोंदवू", "शिकायत"]
        )
    ):
        if response_type == "yes":
            session_state["stage"] = "registration_info"
            kb = MAHA_AASTHA_KNOWLEDGE_BASE[language]
            return f"{kb['yes_response']['intro']}\n\n{kb['yes_response']['link']}"
        elif response_type == "no":
            session_state["stage"] = "feedback_question"
            return get_feedback_question(language)
        else:
            session_state["stage"] = "awaiting_response"
            return get_initial_response_with_status_option(language)

    return get_initial_response_with_status_option(language)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("=" * 70)
    print("🚀 STARTING MAHA AASTHA FASTAPI CHATBOT")
    print("=" * 70)
    print("🌐 Languages:", SUPPORTED_LANGUAGES)
    print("💡 Mode: Q&A with PostgreSQL Database Integration")
    print("⭐ Features: Ticket Status, 5-star rating system")
    print("=" * 70)
    try:
        await init_database()
        connection_test = await test_db_connection()
        SYSTEM_STATUS["database_connected"] = connection_test
        if connection_test:
            print("✅ Database connection: SUCCESS")
            db_info = await get_db_info()
            if db_info.get("connected"):
                print(f"📊 Database: {db_info.get('database_name', 'N/A')}")
                print(f"👤 User: {db_info.get('user', 'N/A')}")
                print(f"🔢 Pool size: {db_info.get('pool_current_size', '?')}")
        else:
            print("❌ Database connection: FAILED")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        SYSTEM_STATUS["database_connected"] = False
    print("=" * 70)
    print("🎯 Backend ready! Access the API at:")
    print(" • Docs: http://localhost:8000/docs")
    print(" • Health: http://localhost:8000/health/")
    print(" • Ticket Status Check: http://localhost:8000/ticket/status/")
    print("=" * 70)
    yield
    print("🔥 Shutting down...")
    await close_database()
    print("👋 Goodbye!")

# Initialize FastAPI app
app = FastAPI(
    title="Maha Aastha Chatbot Backend",
    description="Grievance Redressal System Chatbot with bilingual support, PostgreSQL database integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    """Additional CORS handling."""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.options("/{full_path:path}")
async def preflight_handler(request: Request, full_path: str):
    """Handle preflight OPTIONS requests."""
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/")
async def root():
    try:
        uptime = time.time() - SYSTEM_STATUS["startup_time"]
        db_info = await get_db_info() if SYSTEM_STATUS["database_connected"] else {"connected": False}
        return {
            "message": "Maha Aastha Chatbot Backend is running",
            "system": "Grievance Redressal System with Database Integration",
            "version": "1.0.0",
            "uptime_seconds": round(uptime, 2),
            "system_status": {
                "active_sessions": len(CHAT_HISTORY),
                "total_queries": SYSTEM_STATUS["total_queries"],
                "total_ratings": len(RATINGS_DATA),
                "supported_languages": SYSTEM_STATUS["supported_languages"],
                "database_connected": SYSTEM_STATUS["database_connected"],
                "database_info": db_info
            }
        }
    except Exception as e:
        logger.error(f"Root endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"System error: {str(e)}"}
        )

@app.post("/query/")
async def process_query(request: QueryRequest):
    """Main query processing endpoint."""
    SYSTEM_STATUS["total_queries"] += 1
    input_text = request.input_text.strip()
    language = request.language.lower()
    
    if not input_text:
        SYSTEM_STATUS["failed_queries"] += 1
        error_msg = {
            'en': "Please provide a valid query.",
            'mr': "कृपया एक वैध प्रश्न प्रदान करा."
        }
        return JSONResponse(
            status_code=400,
            content={"reply": error_msg.get(language, error_msg['en'])}
        )
    
    if language not in SUPPORTED_LANGUAGES:
        SYSTEM_STATUS["failed_queries"] += 1
        return JSONResponse(
            status_code=400,
            content={"reply": f"Language '{language}' not supported. Use: {', '.join(SUPPORTED_LANGUAGES)}"}
        )
    
    session_id = request.session_id or generate_session_id()

    is_greet, greet_key = detect_greeting(input_text)
    if is_greet:
        SYSTEM_STATUS["successful_queries"] += 1
        reply_text = greeting_reply(language, greet_key)
        add_to_chat_history(session_id, input_text, reply_text, language)
        # Log the greeting interaction
        log_chat(session_id, input_text, reply_text, language, endpoint='/query/')
        return {
            "reply": reply_text,
            "language": language,
            "session_id": session_id,
            "detected_language": language
        }

    try:
        assistant_reply = await process_maha_aastha_query(input_text, session_id, language)
        SYSTEM_STATUS["successful_queries"] += 1
        add_to_chat_history(session_id, input_text, assistant_reply, language)
        # Log the query + assistant reply
        log_chat(session_id, input_text, assistant_reply, language, endpoint='/query/')
        return {
            "reply": assistant_reply,
            "language": language,
            "session_id": session_id,
            "detected_language": language
        }
    except Exception as query_error:
        SYSTEM_STATUS["failed_queries"] += 1
        SYSTEM_STATUS["last_error"] = str(query_error)
        logger.error(f"Query processing error: {query_error}")
        error_msg = {
            'en': "An error occurred while processing your query. Please try again later.",
            'mr': "तुमचा प्रश्न प्रक्रिया करतान त्रुटी आली. कृपया नंतर पुन्हा प्रयत्न करा."
        }
        return JSONResponse(
            status_code=500,
            content={"reply": error_msg.get(language, error_msg['en'])}
        )

@app.post("/ticket/status/")
async def get_ticket_status_endpoint(request: TicketStatusRequest):
    """Get ticket status by ID or mobile number"""
    logger.info(f"Received ticket status request for ID: {request.ticket_id}, Language: {request.language}")
    try:
        if not db_manager.pool:
            logger.info("Initializing database connection...")
            await db_manager.init_pool()

        ticket_data = await db_manager.get_ticket_status(request.ticket_id)
        logger.info(f"Retrieved ticket data: {ticket_data}")

        if ticket_data:
            identifier_type = "mobile_number" if validate_mobile_number_format(request.ticket_id) else "ticket_id"
            
            formatted_status = format_simple_ticket_status(ticket_data, request.language)
            logger.info(f"Formatted status message: {formatted_status}")
            # Log ticket status lookup
            log_chat(None, f"ticket_status_lookup:{request.ticket_id}", formatted_status, request.language, endpoint='/ticket/status/')
            
            return JSONResponse(
                content={
                    "success": True,
                    "found": True,
                    "message": formatted_status,
                    "ticket_id": ticket_data.get("ticket"),
                    "status": ticket_data.get("status"),
                    "created_date": ticket_data.get("created_at").strftime("%d-%b-%Y") if ticket_data.get("created_at") else None,
                    "language": request.language,
                    "search_method": identifier_type,
                    "search_value": request.ticket_id
                }
            )
        else:
            identifier_type = "mobile_number" if validate_mobile_number_format(request.ticket_id) else "ticket_id"
            
            if identifier_type == "mobile_number":
                error_msg = {
                    'en': f"Sorry, no ticket found for mobile number {request.ticket_id}. Please check your registered mobile number and try again.",
                    'mr': f"माफ करा, {request.ticket_id} या मोबाइल नंबरसाठी कोणतीही तिकीट आढळली नाही. कृपया आपला नोंदणीकृत मोबाइल नंबर तपासा आणि पुन्हा प्रयत्न करा."
                }
            else:
                error_msg = {
                    'en': "Sorry, no ticket found with the provided ID. Please check your Ticket ID and try again.",
                    'mr': "माफ करा, दिलेल्या क्रमांकाशी कोणतीही तिकीट आढळली नाही. कृपया आपला तिकीट क्रमांक तपासा आणि पुन्हा प्रयत्न करा."
                }
            
            logger.warning(f"No ticket found with {identifier_type}: {request.ticket_id}")
            log_chat(None, f"ticket_status_lookup:{request.ticket_id}", error_msg.get(request.language, error_msg['en']), request.language, endpoint='/ticket/status/')
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "found": False,
                    "message": error_msg.get(request.language, error_msg['en']),
                    "search_method": identifier_type,
                    "search_value": request.ticket_id
                }
            )
    except Exception as e:
        logger.error(f"Error processing ticket status request: {str(e)}")
        error_msg = {
            'en': "An error occurred while fetching the ticket status. Please try again later.",
            'mr': "तिकीट स्थिती मिळवताना त्रुटी आली. कृपया नंतर पुन्हा प्रयत्न करा."
        }
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": error_msg.get(request.language, error_msg['en']),
                "error": str(e)
            }
        )

@app.post("/user/search/")
async def search_user_tickets_endpoint(request: UserSearchRequest):
    """Search tickets by user identifier (phone number)."""
    try:
        tickets = await get_tickets_by_phone(request.user_identifier)
        if tickets:
            return {
                "found": True,
                "count": len(tickets),
                "tickets": tickets,
                "language": request.language
            }
        else:
            error_msg = {
                'en': "No tickets found for the provided user information.",
                'mr': "दिलेल्या वापरकर्ता माहितीसाठी कोणत्याही तिकीटी आढळल्या नाहीत."
            }
            return JSONResponse(
                status_code=404,
                content={
                    "found": False,
                    "message": error_msg.get(request.language, error_msg['en'])
                }
            )
    except Exception as e:
        logger.error(f"Error searching user tickets: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "found": False,
                "message": "Error searching tickets. Please try again later."
            }
        )

@app.get("/database/stats/")
async def get_database_stats():
    """Get database statistics."""
    try:
        if not SYSTEM_STATUS["database_connected"]:
            return JSONResponse(
                status_code=503,
                content={"error": "Database not connected"}
            )
        stats = await db_manager.get_ticket_stats()
        db_info = await get_db_info()
        return {
            "database_info": db_info,
            "ticket_statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get database statistics: {str(e)}"}
        )

@app.post("/rating/")
async def submit_rating(request: RatingRequest):
    """Submit user rating for service quality."""
    logger.info(f"Received rating request: {request.dict()}")
    try:
        session_id = request.session_id or generate_session_id()
        rating_label = RATING_LABELS[request.language][request.rating]
        success = save_rating_data(
            rating=request.rating,
            session_id=session_id,
            language=request.language,
            ticket_id=request.ticket_id,
            feedback_text=request.feedback_text
        )
        if success:
            thank_you_msg = MAHA_AASTHA_KNOWLEDGE_BASE[request.language]['rating_thank_you']
            response_msg = {
                'en': f"Thank you for your {request.rating}-star rating! ({rating_label})",
                'mr': f"आपल्या {request.rating}-स्टार रेटिंगसाठी धन्यवाद! ({rating_label})"
            }
            logger.info(f"Successfully saved rating: {request.rating} stars for session {session_id}")
            add_to_chat_history(
                session_id,
                f"Rating: {request.rating}/5",
                f"{thank_you_msg}\n\n{response_msg.get(request.language, response_msg['en'])}",
                request.language
            )
            # Log rating submission
            log_chat(session_id, f"rating:{request.rating}", response_msg.get(request.language, response_msg['en']), request.language, endpoint='/rating/')
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": response_msg.get(request.language, response_msg['en']),
                    "thank_you": thank_you_msg,
                    "rating": request.rating,
                    "rating_label": rating_label,
                    "session_id": session_id
                }
            )
        else:
            error_msg = {
                'en': "Failed to save your rating. Please try again.",
                'mr': "आपले रेटिंग जतन करण्यात अयशस्वी. कृपया पुन्हा प्रयत्न करा."
            }
            logger.error(f"Failed to save rating for session {session_id}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": error_msg.get(request.language, error_msg['en'])
                }
            )
    except ValidationError as ve:
        logger.error(f"Validation error in rating submission: {ve}")
        error_msg = {
            'en': "Invalid rating data. Rating must be between 1 and 5.",
            'mr': "अवैध रेटिंग डेटा. रेटिंग 1 आणि 5 दरम्यान असावे."
        }
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": error_msg.get(request.language, error_msg['en']),
                "errors": str(ve)
            }
        )
    except Exception as e:
        logger.error(f"Error in rating submission: {str(e)}")
        error_msg = {
            'en': "An error occurred while processing your rating.",
            'mr': "आपले रेटिंग प्रक्रिया करताना त्रुटी आली."
        }
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": error_msg.get(request.language, error_msg['en']),
                "error": str(e)
            }
        )

@app.get("/ratings/export")
async def export_ratings():
    """Export ratings data as CSV with UTF-8 support."""
    try:
        if not RATINGS_DATA:
            return JSONResponse(
                status_code=404,
                content={"error": "No ratings data available for export"}
            )
        output = io.StringIO()
        fieldnames = ["timestamp", "session_id", "rating", "feedback", "language", "ticket_id"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for rating_data in RATINGS_DATA:
            modified_row = {
                "timestamp": rating_data["timestamp"],
                "session_id": rating_data["session_id"],
                "rating": rating_data["rating"],
                "feedback": rating_data["Feedback"],
                "language": rating_data["language"],
                "ticket_id": rating_data["ticket_id"]
            }
            writer.writerow(modified_row)
        csv_content = output.getvalue()
        output.close()
        utf8_bom = '\ufeff'
        csv_content_with_bom = utf8_bom + csv_content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"maha_aastha_ratings_{timestamp}.csv"
        return StreamingResponse(
            io.BytesIO(csv_content_with_bom.encode('utf-8')),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to export ratings: {str(e)}"}
        )

@app.get("/ratings/stats")
async def get_rating_stats():
    """Get rating statistics."""
    try:
        if not RATINGS_DATA:
            return {
                "total_ratings": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "language_distribution": {}
            }
        total_ratings = len(RATINGS_DATA)
        ratings = [entry["rating"] for entry in RATINGS_DATA]
        average_rating = sum(ratings) / total_ratings if ratings else 0
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[str(i)] = ratings.count(i)
        languages = [entry["language"] for entry in RATINGS_DATA]
        language_distribution = {}
        for lang in set(languages):
            language_distribution[lang] = languages.count(lang)
        return {
            "total_ratings": total_ratings,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
            "language_distribution": language_distribution,
            "latest_ratings": RATINGS_DATA[-10:] if len(RATINGS_DATA) >= 10 else RATINGS_DATA
        }
    except Exception as e:
        logger.error(f"Rating stats error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get rating statistics: {str(e)}"}
        )

@app.get("/health/")
async def health_check():
    """System health check endpoint with database connectivity."""
    try:
        uptime = time.time() - SYSTEM_STATUS["startup_time"]
        db_status = await test_db_connection() if SYSTEM_STATUS["database_connected"] else False
        SYSTEM_STATUS["database_connected"] = db_status
        return {
            "status": "healthy" if db_status else "degraded",
            "timestamp": time.time(),
            "uptime_seconds": round(uptime, 2),
            "system_info": {
                "active_sessions": len(CHAT_HISTORY),
                "total_queries": SYSTEM_STATUS["total_queries"],
                "successful_queries": SYSTEM_STATUS["successful_queries"],
                "failed_queries": SYSTEM_STATUS["failed_queries"],
                "total_ratings": len(RATINGS_DATA),
                "supported_languages": SYSTEM_STATUS["supported_languages"],
                "database_connected": db_status
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": time.time()
            }
        )

@app.get("/suggestions/")
async def get_suggestions(language: str = "en"):
    """Get suggested queries."""
    suggestions_by_language = {
        "en": [
            "I want to register a ticket",
            "Would you like to check the status of the ticket which you have registered on the Maha Aastha Grievance Redressal System?",
            "Check status TKT-12345678",
            "Has a Ticket already been registered on the Maha Aastha Grievance Redressal System?",
            "Would you like to provide feedback regarding the resolution of your ticket addressed through the Maha Aastha Grievance Redressal System?"
        ],
        "mr": [
            "मला तिकीट नोंदवायची आहे",
            "आपण महा आस्था तक्रार निवारण प्रणालीमध्ये नोंदवलेल्या तिकीटची स्थिती तपासू इच्छिता का?",
            "स्थिती तपासा TKT-12345678",
            "महा आस्था तक्रार निवारण प्रणालीमध्ये नोंदविण्यात आलेली तिकीट आहे का?",
            "आपल्या तिकीटच्या निराकरणाबाबत अभिप्राय द्यायला इच्छिता का?"
        ]
    }
    suggestions = suggestions_by_language.get(language, suggestions_by_language["en"])
    return {
        "suggestions": suggestions,
        "language": language,
        "total": len(suggestions)
    }

@app.get("/languages/")
async def get_supported_languages():
    """Get list of supported languages."""
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "language_details": {
            "en": {"name": "English", "native_name": "English"},
            "mr": {"name": "Marathi", "native_name": "मराठी"}
        }
    }

@app.get("/debug/sessions")
async def debug_sessions():
    """Debugs endpoint to check current session states."""
    return {
        "total_sessions": len(USER_SESSION_STATE),
        "sessions": USER_SESSION_STATE,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
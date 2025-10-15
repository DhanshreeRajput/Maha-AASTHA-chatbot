<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maha Aastha</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #fbfcfdff 0%, #f4f3f5ff 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .demo-content {
            text-align: center;
            color: blue;
            padding: 50px 20px;
        }

        .demo-content h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }

        .demo-content p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        /* Chat Widget Styles */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
        }

        .chat-bubble {
            position: relative;
            background: linear-gradient(135deg, #3b5fffff 0%, #7d99f8ff 100%);
            width: 72px;
            height: 74px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(103, 105, 245, 0.4);
            transition: all 0.3s ease;
            animation: pulse 2s infinite;
        }

        .chat-bubble:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(118, 120, 253, 0.6);
        }

        .chat-bubble svg {
            width: 28px;
            height: 28px;
            fill: white;
        }

        .chat-bubble img {
            width: 74px;
            height: 74px;
            object-fit: contain;
            display: block;
        }

        .notification-badge {
            position: absolute;
            top: -2px;
            right: -2px;
            background: #e74c3c;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid white;
        }

        @keyframes pulse {
            0% { box-shadow: 0 4px 20px rgba(117, 160, 253, 0.4); }
            50% { box-shadow: 0 4px 20px rgba(132, 134, 255, 0.8); }
            100% { box-shadow: 0 4px 20px rgba(124, 153, 247, 0.4); }
        }

        /* Chat Window */
        .chat-window {
            position: fixed;
            bottom: 103px;
            right: 20px;
            width: 380px;
            height: 500px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 9999;
            animation: slideUp 0.3s ease;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .chat-header {
            background: linear-gradient(135deg, #e6e9f0ff 0%, #092becff 100%);
            padding: 15px 20px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
        }

        .chat-header-info {
            display: flex;
            align-items: center;
            flex: 1;
        }

        .chat-avatar {
            width: auto;
            height: auto;
            border-radius: 0;
            background: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
        }

        .chat-avatar img {
            width: 72px;
            height: 72px;
            object-fit: contain;
            display: block;
        }

        .chat-header-text h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 2px;
        }

        .chat-header-text p {
            font-size: 12px;
            opacity: 0.9;
        }

        /* Language Dropdown */
        .language-selector {
            display: flex;
            align-items: center;
            margin-right: 0px;
        }

        .language-dropdown {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 12px;
            cursor: pointer;
            outline: none;
            transition: all 0.2s;
        }

        .language-dropdown:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .language-dropdown option {
            background: #606bfdff;
            color: white;
            padding: 5px;
        }

        .close-chat {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .close-chat:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
            max-height: 300px;
            display: flex;
            flex-direction: column;
        }

        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-content {
            max-width: 280px;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
        }

        .message.bot .message-content {
            background: white;
            border: 1px solid #e1e8ed;
            color: #333;
            border-bottom-left-radius: 8px;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 8px;
        }

        .message-time {
            font-size: 11px;
            color: #999;
            margin-top: 5px;
            text-align: right;
        }

        .message.bot .message-time {
            text-align: left;
        }

        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border: 1px solid #e1e8ed;
            border-radius: 18px;
            border-bottom-left-radius: 8px;
            max-width: 60px;
            margin-bottom: 15px;
        }

        .typing-dots {
            display: flex;
            gap: 4px;
        }

        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            animation: typing 1.4s infinite;
        }

        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.5;
            }
            30% {
                transform: translateY(-10px);
                opacity: 1;
            }
        }

        .chat-input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e1e8ed;
        }

        .suggested-questions {
            margin-bottom: 15px;
        }

        .suggested-questions p {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .suggestion-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 10px;
        }

        .suggestion-btn {
            background: #f1f3f4;
            border: none;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            color: #5f6368;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .suggestion-btn:hover {
            background: #e8eaed;
            transform: translateY(-1px);
        }

        .suggestion-btn:active {
            transform: translateY(0);
        }

        .chat-input-form {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e1e8ed;
            border-radius: 24px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .chat-input:focus {
            border-color: #574bf7ff;
        }

        .send-btn {
            background: linear-gradient(135deg, #5161f1ff 0%, #858febff 100%);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .send-btn:hover:not(:disabled) {
            transform: scale(1.05);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .send-btn svg {
            width: 16px;
            height: 16px;
            fill: white;
        }

        .status-indicator {
            padding: 8px 16px;
            margin: 10px 0;
            border-radius: 8px;
            font-size: 12px;
            text-align: center;
        }

        .status-indicator.error {
            background: #ffe6e6;
            color: #c53030;
            border: 1px solid #feb2b2;
        }

        .status-indicator.success {
            background: #e6fffa;
            color: #2d7d72;
            border: 1px solid #81e6d9;
        }

        .status-indicator.info {
            background: #e6f3ff;
            color: #2563eb;
            border: 1px solid #93c5fd;
        }

        .quick-actions {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        .quick-action-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 8px 12px;
            border-radius: 16px;
            font-size: 11px;
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .quick-action-btn:hover {
            transform: translateY(-1px);
            opacity: 0.9;
        }

        .quick-action-btn:active {
            transform: translateY(0);
        }

        /* Enhanced Button Animations - Applied to all interactive buttons */
        .pgrs-options {
            display: flex;
            flex-direction: row;
            gap: 4px;
            margin-top: 10px;
        }

        .option-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 7px 35px;
            border-radius: 16px;
            font-size: 12px;
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 0px solid transparent;
        }

        .option-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }

        .option-button:active {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }

        .link-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 10px 16px;
            border-radius: 16px;
            font-size: 12px;
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
            margin: 4px;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .link-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }

        .link-button:active {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }

        /* 5-Star Rating System Styles */
        .rating-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e9ecef;
        }

        .rating-title {
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            text-align: center;
            margin-bottom: 10px;
        }

        .stars-container {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin: 10px 0;
        }

        .star {
            width: 32px;
            height: 32px;
            cursor: pointer;
            transition: all 0.3s ease;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }

        .star svg {
            width: 100%;
            height: 100%;
        }

        .star.empty svg {
            fill: #d1d5db;
            stroke: #9ca3af;
            stroke-width: 1;
        }

        .star.filled svg {
            fill: #fbbf24;
            stroke: #f59e0b;
            stroke-width: 1;
        }

        .star.hover svg {
            fill: #fcd34d;
            stroke: #f59e0b;
            stroke-width: 1;
            transform: scale(1.1);
        }

        .star:hover {
            transform: scale(1.15);
        }

        .rating-labels {
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: #6b7280;
            margin-top: 5px;
            padding: 0 5px;
        }

        .rating-feedback {
            text-align: center;
            margin: 10px 0;
            font-size: 13px;
            font-weight: 500;
        }

        .rating-feedback.rating-1 { color: #dc2626; }
        .rating-feedback.rating-2 { color: #ea580c; }
        .rating-feedback.rating-3 { color: #ca8a04; }
        .rating-feedback.rating-4 { color: #16a34a; }
        .rating-feedback.rating-5 { color: #059669; }

        .message.bot.rating-confirmation {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            text-align: center;
            padding: 12px 16px;
            border-radius: 12px;
            margin: 8px 0;
            box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
        }

        .message.bot.thank-you {
            background: #f8fafc;
            color: #1e293b;
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
            border: 1px solid #e2e8f0;
        }

        .submit-rating-btn {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: -15px;
            align-self: center;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        }

        .submit-rating-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
        }

        .submit-rating-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
            background: #9ca3af;
            box-shadow: none;
        }

        .submit-rating-btn:active:not(:disabled) {
            transform: translateY(-1px);
        }

        .rating-success {
            background: #dcfce7;
            border: 1px solid #bbf7d0;
            color: #166534;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-size: 12px;
            margin-top: 10px;
        }

        .input-field {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #e1e8ed;
            border-radius: 12px;
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
            margin-bottom: 10px;
        }

        .input-field:focus {
            border-color: #574bf7ff;
            box-shadow: 0 0 0 3px rgba(87, 75, 247, 0.1);
        }

        .connection-status {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #e74c3c;
            transition: background-color 0.3s;
        }

        .connection-status.connected {
            background: #27ae60;
        }

        .suggestion-title {
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 12px;
        }

        .suggestion-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .suggestion-item {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 5px 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 13px;
            color: #495057;
            text-align: left;
        }

        .suggestion-item:hover {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
            transform: translateY(-1px);
        }

        .status-header {
            font-size: 16px;
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 15px;
            text-align: center;
            border-bottom: 2px solid #e3f2fd;
            padding-bottom: 8px;
        }

        .status-details {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0;
            border-bottom: 1px solid #e8f4fd;
        }

        .status-item:last-child {
            border-bottom: none;
        }

        .status-label {
            font-weight: 600;
            color: #34495e;
            font-size: 13px;
            min-width: 100px;
        }

        .status-value {
            color: #2c3e50;
            font-size: 13px;
            text-align: right;
            font-weight: 500;
        }

        .status-value.highlight {
            background: #e8f5e8;
            padding: 3px 8px;
            border-radius: 6px;
            color: #27ae60;
            font-weight: bold;
        }

        /* Export Button */
        .export-ratings-btn {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border: none;
            padding: 8px 12px;
            border-radius: 16px;
            font-size: 11px;
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-left: 8px;
        }

        .export-ratings-btn:hover {
            transform: translateY(-1px);
            opacity: 0.9;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }

        .export-ratings-btn:active {
            transform: translateY(0);
        }

        /* Responsive Design */
        @media (max-width: 480px) {
            .chat-window {
                right: 10px;
                left: 10px;
                width: auto;
                bottom: 80px;
            }
        }
        .suggestion-dropdown {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #e1e8ed;
            border-radius: 12px;
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
            margin-bottom: 10px;
            background: white;
        }

        .suggestion-dropdown:focus {
            border-color: #574bf7ff;
            box-shadow: 0 0 0 3px rgba(87, 75, 247, 0.1);
        }

        .chat-input-container {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-top: 10px;
        }

        .chat-text-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e1e8ed;
            border-radius: 24px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .chat-text-input:focus {
            border-color: #574bf7ff;
        }

        .send-message-btn {
            background: linear-gradient(135deg, #5161f1ff 0%, #858febff 100%);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .send-message-btn:hover:not(:disabled) {
            transform: scale(1.05);
        }

        .send-message-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .send-message-btn svg {
            width: 16px;
            height: 16px;
            fill: white;
        }
    </style>
</head>
<body>
    <!-- Demo Content -->
    <div>
<img src="logo/home.png" width="100%" height="auto" style="max-height: 100vh;" alt="Home Logo">
    </div>   

    <!-- Chat Widget -->
    <div class="chat-widget">
        <div class="chat-bubble" id="chatBubble">
            <img src="logo/main_logo.png" alt="Chat" onerror="this.style.display='none'; this.parentNode.innerHTML='<svg viewBox=\'0 0 24 24\'><path d=\'M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4A2,2 0 0,0 20,2M6,9H18V11H6V9M14,14H6V12H14V14M18,8H6V6H18V8Z\'/></svg>'"/>
            <div class="notification-badge" id="notificationBadge" style="display: none;">0</div>
        </div>

        <div class="chat-window" id="chatWindow">
            <div class="chat-header">
                <div class="chat-header-info">
                    <div class="chat-avatar">
                        <img src="logo/maha_aastha_logo.png" alt="Maha Aastha Logo" onerror="this.style.display='none'">
                    </div>
                    <div class="chat-header-text"
                        <h3 id="chatTitle">Maha Aastha Grievance Redressal System</h3>
                        <p id="connectionStatus">Ready to help</p>
                    </div>
                </div>
                
                <div class="language-selector">
                   <select class="language-dropdown" id="languageSelect">
                        <option value="mr">मराठी</option>
                        <option value="en">English</option>
                    </select>
                </div>
                
                <button class="close-chat" id="closeChat">&times;</button>
            </div>

            <div class="chat-messages" id="chatMessages">
                <div class="typing-indicator" id="typingIndicator">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>

            <div class="chat-input-area">
                <!-- Permanent text input at bottom -->
                <div class="chat-input-form">
                    <input type="text" 
                        class="chat-input" 
                        id="chatInput" 
                        placeholder="Ask your query here">
                    <button class="send-btn" id="sendBtn" disabled>
                        <svg viewBox="0 0 24 24">
                            <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                        </svg>
                    </button>
                </div>
                
                <div class="quick-actions">
                    <button class="quick-action-btn" id="restartBtn">Restart</button>
                    <button class="quick-action-btn" id="clearChatBtn">Clear Chat</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // API Configuration
        const API_BASE_URL = 'http://localhost:8000';
        
        // MAHA AASTHA SCRIPTS - Updated for Maha Aastha
        const MAHA_AASTHA_SCRIPTS = {
            en: {
                // Page elements
                pageTitle: "Welcome to Maha Aastha Chatbot.",
                chatTitle: "Maha Aastha Grievance Redressal System",
                connectionStatus: "Ready to help",
                restartBtn: "Restart",
                clearChatBtn: "Clear Chat",
                input_placeholder: "Ask your query here",
                suggestions_title: "Questions you can ask me:",
                
                // Greeting and unknown responses
                greeting_response: "Hello! Welcome to the Maha Aastha Grievance Redressal System. How may I help you today?",
                how_may_help: "How may I help you today?",
                unknown_question: "I can help you with ticket registration, status checking, or providing feedback. Please choose from the suggestions above or be more specific.",
                
                // Conversation content
                welcome: "Welcome to Maha Aastha Grievance Redressal System AI-ChatBot.",
                question1: "Would you like to register a Ticket on the Maha Aastha Grievance Redressal System?",
                question2: "Would you like to check the status of the ticket which you have registered on the Maha Aastha Grievance Redressal System?",
                question3: "Would you like to provide feedback regarding the resolution of your ticket addressed through the Maha Aastha Grievance Redressal System?",
                register_intro: "You can register your Ticket on the Maha Aastha Grievance Redressal System through below link:",
                register_link: "http://172.17.46.11:8001/#grievance",
                ticket_id_prompt: "Please enter your Ticket ID or Mobile Number to check the status:",
                ticket_id_input_label: "Enter Ticket ID (Example: TKT-12345678) or Mobile Number (Example: 9876543210)",
                ticket_id_placeholder: "Type your Ticket ID or Mobile Number here...",
                invalid_ticket_id: "Please provide a valid Ticket ID (e.g., TKT-12345678) or 10-digit mobile number (e.g., 9876543210).",
                check_status_btn: "Check Ticket Status",
                processing: "Processing...",
                status_prefix: "The current status of your Ticket is as follows:",
                rating_request: "Please provide your rating between 1 and 5:",
                rating_title: "Rate our service quality",
                submit_rating: "Submit Rating",
                submitting: "Submitting...",
                invalid_input: "The information you have entered is invalid. Please try again.",
                thank_you: "Thank you for using the Maha Aastha Grievance Redressal System.",
                yes: "YES",
                no: "NO",
                register_button: "Register Ticket",
                suggestions_title: "Quick Suggestions:",
                language_switch_msg: "Language switched to English. Restarting conversation...",
                status_details_header: "Ticket Status Details",
                track_ticket_help: "You can also track your ticket status at: http://172.17.46.11:8001/#view-ticket",
                rating_labels: {
                    1: "Poor",
                    2: "Fair", 
                    3: "Good",
                    4: "Very Good",
                    5: "Excellent"
                },
                suggestions: [
                    "I want to check ticket status",
                    "I want to Register a Ticket",
                    "I want to provide feedback"
                ]
            },
            mr: {
                // Page elements - MARATHI TRANSLATIONS
                pageTitle: "महा आस्था चॅटबॉटमध्ये आपले स्वागत आहे.",
                chatTitle: "महा आस्था तक्रार निवारण प्रणाली",
                connectionStatus: "मदत करण्यासाठी तयार",
                restartBtn: "पुन्हा सुरू करा",
                clearChatBtn: "चॅट साफ करा",
                input_placeholder: "तुमची क्वेरी येथे विचारा",
                suggestions_title: "तुम्ही मला विचारू शकता:",
                
                // Greeting and unknown responses
                greeting_response: "नमस्कार! महा आस्था तक्रार निवारण प्रणालीमध्ये आपले स्वागत आहे. आज मी आपल्याला कशी मदत करू शकतो?",
                how_may_help: "आज मी आपल्याला कशी मदत करू शकतो?",
                unknown_question: "मी आपल्याला तिकीट नोंदणी, स्थिती तपासणे किंवा अभिप्राय देण्यासाठी मदत करू शकतो. कृपया वरील सूचनांमधून निवडा किंवा अधिक स्पष्ट करा.",
                
                // Conversation content
                welcome: "नमस्कार, महा आस्था तक्रार निवारण प्रणाली एआय-चॅटबॉटमध्ये आपले स्वागत आहे.",
                question1: "महा आस्था तक्रार निवारण प्रणालीमध्ये आपण तिकीट नोंदवू इच्छिता का?",
                question2: "आपण महा आस्था तक्रार निवारण प्रणालीमध्ये नोंदवलेल्या तिकीटची स्थिती तपासू इच्छिता का?",
                question3: "महा आस्था तक्रार निवारण प्रणालीद्वारे सोडविण्यात आलेल्या आपल्या तिकीटच्या निराकरणाबाबत अभिप्राय द्यायला इच्छिता का?",
                register_intro: "आपण महा आस्था तक्रार निवारण प्रणालीमध्ये आपली तिकीट खालील लिंकद्वारे नोंदवू शकता:",
                register_link: "http://172.17.46.11:8001/#grievance",
                ticket_id_prompt: "कृपया स्थिती तपासण्यासाठी आपला तिकीट क्रमांक किंवा मोबाइल नंबर प्रविष्ट करा:",
                ticket_id_input_label: "तिकीट क्रमांक (उदाहरण: TKT-12345678) किंवा मोबाइल नंबर (उदाहरण: 9876543210) प्रविष्ट करा",
                ticket_id_placeholder: "आपला तिकीट क्रमांक किंवा मोबाइल नंबर येथे टाइप करा...",
                invalid_ticket_id: "कृपया वैध तिकीट क्रमांक (उदा. TKT-12345678) किंवा 10-अंकी मोबाइल नंबर (उदा. 9876543210) प्रदान करा.",
                check_status_btn: "तिकीट स्थिती तपासा",
                processing: "प्रक्रिया करत आहे...",
                status_prefix: "आपल्या तिकीटची सद्यस्थिती खालीलप्रमाणे आहे:",
                rating_request: "कृपया आपल्याद्वारे देण्यात आलेले गुण १ ते ५ मध्ये द्या:",
                rating_title: "आमच्या सेवेची गुणवत्ता रेट करा",
                submit_rating: "रेटिंग सबमिट करा",
                submitting: "सबमिट करत आहे...",
                invalid_input: "आपण दिलेली माहिती अवैध आहे. कृपया पुन्हा प्रयत्न करा.",
                thank_you: "महा आस्था तक्रार निवारण प्रणालीचा वापर केल्याबद्दल आपले धन्यवाद.",
                yes: "होय",
                no: "नाही",
                register_button: "तिकीट नोंदवा",
                suggestions_title: "त्वरित सूचना:",
                language_switch_msg: "भाषा मराठी मध्ये बदलली. संवाद पुन्हा सुरू करत आहे...",
                status_details_header: "तिकीट स्थिती तपशील",
                track_ticket_help: "आपण आपल्या तिकीटची स्थिती येथे देखील तपासू शकता: http://172.17.46.11:8001/#view-ticket",
                rating_labels: {
                    1: "खराब",
                    2: "सामान्य",
                    3: "चांगले", 
                    4: "खूप चांगले",
                    5: "उत्कृष्ट"
                },
                suggestions: [
                    "मला तिकीट स्थिती तपासायची आहे",
                    "मला तिकीट नोंदवायची आहे",
                    "मला अभिप्राय द्यायचा आहे"
                ]
            }
        };

        // State Management
        let currentLanguage = 'mr'; // Default language set to Marathi
        let chatState = 'start';
        let pendingTicketId = '';
        let selectedRating = null;
        let isWindowOpen = false;
        let currentSessionId = null;

        // DOM Elements
        const elements = {
            chatBubble: document.getElementById('chatBubble'),
            chatWindow: document.getElementById('chatWindow'),
            closeChat: document.getElementById('closeChat'),
            chatMessages: document.getElementById('chatMessages'),
            typingIndicator: document.getElementById('typingIndicator'),
            languageSelect: document.getElementById('languageSelect'),
            restartBtn: document.getElementById('restartBtn'),
            clearChatBtn: document.getElementById('clearChatBtn'),
            chatInput: document.getElementById('chatInput'),
            sendBtn: document.getElementById('sendBtn'),
            chatTitle: document.getElementById('chatTitle'),
            connectionStatus: document.getElementById('connectionStatus')
        };

        // Update all UI elements based on language
        function updateUILanguage() {
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            
            document.title = script.pageTitle || 'Maha Aastha';
            
            if (elements.chatTitle) {
                elements.chatTitle.textContent = script.chatTitle;
            }
            if (elements.connectionStatus) {
                elements.connectionStatus.textContent = script.connectionStatus;
            }
            
            if (elements.restartBtn) {
                elements.restartBtn.textContent = script.restartBtn;
            }
            if (elements.clearChatBtn) {
                elements.clearChatBtn.textContent = script.clearChatBtn;
            }
            
            if (elements.chatInput) {
                elements.chatInput.placeholder = script.input_placeholder;
            }
            
            if (elements.languageSelect) {
                elements.languageSelect.value = currentLanguage;
            }
        }

        // Utility Functions
        function generateSessionId() {
            return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        }

        function isGreetingMessage(message) {
            const lowerMessage = message.toLowerCase();
            
            const englishGreetings = [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
                'good evening', 'greetings', 'howdy', 'hiya', 'sup'
            ];
            
            const marathiGreetings = [
                'नमस्कार', 'हॅलो', 'हाय', 'सकाळची नमस्कार', 
                'दुपारची नमस्कार', 'संध्याकाळची नमस्कार', 'अभिवादन'
            ];
            
            const allGreetings = [...englishGreetings, ...marathiGreetings];
            return allGreetings.some(greeting => lowerMessage.includes(greeting));
        }

        function getCurrentTime() {
            return new Date().toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: true 
            });
        }

        function scrollToBottom() {
            setTimeout(() => {
                elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
            }, 100);
        }

        function sendUserMessage() {
            const message = elements.chatInput.value.trim();
            if (message) {
                addMessage(message, true);
                elements.chatInput.value = '';
                elements.sendBtn.disabled = true;
                
                setTimeout(() => {
                    processUserMessage(message);
                }, 500);
            }
        }

        function processUserMessage(message) {
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            const lowerMessage = message.toLowerCase();
            
            if (chatState === 'awaiting_ticket_id') {
                elements.chatInput.placeholder = script.input_placeholder;
                processTicketId(message);
                return;
            }
            
            // Auto-detect ticket ID or mobile number
            const ticketIdPattern = /TKT-[A-Za-z0-9]{8,}/i;
            const mobilePattern = /\b[6-9]\d{9}\b/;
            
            if (ticketIdPattern.test(message) || mobilePattern.test(message)) {
                const identifier = ticketIdPattern.test(message) 
                    ? message.match(ticketIdPattern)[0]
                    : message.match(mobilePattern)[0];
                
                setTimeout(() => {
                    chatState = 'awaiting_ticket_id';
                    processTicketId(identifier);
                }, 500);
                return;
            }
            
            // Check for greetings first
            if (isGreetingMessage(message)) {
                setTimeout(() => {
                    addMessage(script.greeting_response, false);
                    setTimeout(() => {
                        showSuggestionsInChat();
                    }, 1000);
                }, 500);
                return;
            }
            
            // Check for specific queries
            if (lowerMessage.includes('status') || lowerMessage.includes('check') || 
                lowerMessage.includes('स्थिती') || lowerMessage.includes('तपास')) {
                setTimeout(() => {
                    showTicketInput();
                }, 500);
            } else if (lowerMessage.includes('feedback') || lowerMessage.includes('rating') || 
                    lowerMessage.includes('अभिप्राय') || lowerMessage.includes('द्या')) {
                chatState = 'question3';
                setTimeout(() => {
                    addOptionsMessage(script.question3, [script.yes, script.no]);
                }, 500);
            } else if (lowerMessage.includes('register') || lowerMessage.includes('ticket') || 
                    lowerMessage.includes('तिकीट') || lowerMessage.includes('नोंद')) {
                chatState = 'start';
                setTimeout(() => {
                    addOptionsMessage(script.question1, [script.yes, script.no]);
                }, 500);
            } else {
                setTimeout(() => {
                    addMessage(script.unknown_question, false);
                    setTimeout(() => {
                        showSuggestionsInChat();
                    }, 1000);
                }, 500);
            }
        }

        function showTypingIndicator() {
            elements.typingIndicator.style.display = 'block';
            scrollToBottom();
        }

        function hideTypingIndicator() {
            elements.typingIndicator.style.display = 'none';
        }

        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${content}
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            `;
            
            elements.chatMessages.insertBefore(messageDiv, elements.typingIndicator);
            scrollToBottom();
        }

        function formatTicketStatus(statusText) {
            const englishPattern = /(?=Ticket ID:|Status:|Created:|Employee Name:|Category:|District:|Office:|Subject:|Last Updated:)/;
            const marathiPattern = /(?=तिकीट क्रमांक:|स्थिती:|दाखल दिनांक:|कर्मचारी नाव:|श्रेणी:|जिल्हा:|कार्यालय:|विषय:|शेवटचा अद्यतन:)/;
            
            const isMarathi = /[\u0900-\u097F]/.test(statusText);
            
            let processedText = statusText;
            
            let parts;
            if (isMarathi) {
                parts = processedText.split(marathiPattern);
                if (parts.length <= 1) {
                    parts = processedText.split(/\n+|(?=[\u0900-\u097F]+\s*:)/);
                }
            } else {
                parts = processedText.split(englishPattern);
                if (parts.length <= 1) {
                    parts = processedText.split(/\n+|(?=\w+\s*:)/);
                }
            }
            
            if (parts.length <= 1) {
                parts = processedText.split(/\n+/);
                if (parts.length <= 1) {
                    parts = processedText.split(/(?=\w+:|[\u0900-\u097F]+:)/);
                }
            }
            
            let formattedStatus = '<div class="grievance-status-container">';
            
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            formattedStatus += `<div class="status-header">${script.status_details_header}</div>`;
            formattedStatus += '<div class="status-details">';
            
            parts.forEach(part => {
                const trimmedPart = part.trim();
                if (trimmedPart && trimmedPart.length > 0) {
                    const colonIndex = trimmedPart.indexOf(':');
                    if (colonIndex !== -1) {
                        const label = trimmedPart.substring(0, colonIndex + 1);
                        const value = trimmedPart.substring(colonIndex + 1).trim();
                        
                        if (label.trim() && value.trim()) {
                            const isStatusField = label.includes('Status:') || 
                                                 label.includes('स्थिती:') || 
                                                 label.toLowerCase().includes('status');
                            const valueClass = isStatusField ? 'status-value highlight' : 'status-value';
                            
                            formattedStatus += `
                                <div class="status-item">
                                    <span class="status-label">${label}</span>
                                    <span class="${valueClass}">${value}</span>
                                </div>
                            `;
                        }
                    } else if (trimmedPart.length > 10 && !trimmedPart.includes(':')) {
                        formattedStatus += `
                            <div class="status-item">
                                <span class="status-value" style="width: 100%; text-align: left;">${trimmedPart}</span>
                            </div>
                        `;
                    }
                }
            });
            
            formattedStatus += '</div></div>';
            return formattedStatus;
        }
        
        function addOptionsMessage(content, options) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            let optionsHtml = '';
            options.forEach((option, index) => {
                optionsHtml += `<button class="option-button" data-option="${index}">${option}</button>`;
            });
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${content}
                    <div class="pgrs-options">
                        ${optionsHtml}
                    </div>
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            `;
            
            elements.chatMessages.insertBefore(messageDiv, elements.typingIndicator);
            scrollToBottom();
            
            messageDiv.querySelectorAll('.option-button').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const optionIndex = parseInt(e.target.dataset.option);
                    const optionText = options[optionIndex];
                    addMessage(optionText, true);
                    handleUserChoice(optionIndex);
                });
            });
        }

        function addLinkMessage(content, link) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${content}<br><br>
                    <button class="link-button" onclick="window.open('${link}', '_blank')">
                        ${MAHA_AASTHA_SCRIPTS[currentLanguage].register_button}
                    </button>
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            `;
            
            elements.chatMessages.insertBefore(messageDiv, elements.typingIndicator);
            scrollToBottom();
        }

        function addRatingMessage(content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            const labels = script.rating_labels;
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    ${content}
                    <div class="rating-container">
                        <div class="rating-title">${script.rating_title}</div>
                        <div class="stars-container" id="starsContainer">
                            ${[1,2,3,4,5].map(num => `
                                <div class="star empty" data-rating="${num}">
                                    <svg viewBox="0 0 24 24">
                                        <path d="M12,17.27L18.18,21L16.54,13.97L22,9.24L14.81,8.62L12,2L9.19,8.62L2,9.24L7.46,13.97L5.82,21L12,17.27Z"/>
                                    </svg>
                                </div>
                            `).join('')}
                        </div>
                        <div class="rating-labels">
                            <span>${labels[1]}</span>
                            <span>${labels[2]}</span>
                            <span>${labels[3]}</span>
                            <span>${labels[4]}</span>
                            <span>${labels[5]}</span>
                        </div>
                        <div class="rating-feedback" id="ratingFeedback"></div>
                        <button class="submit-rating-btn" id="submitRatingBtn" disabled>${script.submit_rating}</button>
                    </div>
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            `;
            
            elements.chatMessages.insertBefore(messageDiv, elements.typingIndicator);
            scrollToBottom();
            
            setupRatingSystem(messageDiv);
        }

        function setupRatingSystem(container) {
            const stars = container.querySelectorAll('.star');
            const submitBtn = container.querySelector('#submitRatingBtn');
            const feedback = container.querySelector('#ratingFeedback');
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            
            let currentRating = 0;
            let hoverRating = 0;

            stars.forEach((star, index) => {
                const rating = index + 1;
                
                star.addEventListener('mouseenter', () => {
                    hoverRating = rating;
                    updateStarDisplay(stars, hoverRating, currentRating, true);
                    showFeedback(feedback, rating, script.rating_labels);
                });
                
                star.addEventListener('mouseleave', () => {
                    hoverRating = 0;
                    updateStarDisplay(stars, currentRating, currentRating, false);
                    if (currentRating > 0) {
                        showFeedback(feedback, currentRating, script.rating_labels);
                    } else {
                        feedback.textContent = '';
                        feedback.className = 'rating-feedback';
                    }
                });
                
                star.addEventListener('click', () => {
                    currentRating = rating;
                    selectedRating = rating;
                    updateStarDisplay(stars, currentRating, currentRating, false);
                    showFeedback(feedback, currentRating, script.rating_labels);
                    submitBtn.disabled = false;
                });
            });

            submitBtn.addEventListener('click', async () => {
                if (selectedRating) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = script.submitting;
                    
                    try {
                        await submitRating(selectedRating);
                    } catch (error) {
                        console.error('Failed to submit rating:', error);
                        submitBtn.disabled = false;
                        submitBtn.textContent = script.submit_rating;
                    }
                }
            });
        }

        function updateStarDisplay(stars, rating, currentRating, isHovering) {
            stars.forEach((star, index) => {
                const starRating = index + 1;
                star.className = 'star';
                
                if (starRating <= rating) {
                    if (isHovering) {
                        star.className += ' hover';
                    } else {
                        star.className += ' filled';
                    }
                } else {
                    star.className += ' empty';
                }
            });
        }

        function showFeedback(feedbackElement, rating, labels) {
            feedbackElement.textContent = labels[rating];
            feedbackElement.className = `rating-feedback rating-${rating}`;
        }

        async function submitRating(rating) {
            try {
                const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
                
                const response = await fetch(`${API_BASE_URL}/rating/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        rating: rating,
                        session_id: currentSessionId,
                        language: currentLanguage,
                        ticket_id: pendingTicketId || 'NA',
                        feedback_text: document.getElementById('feedbackText')?.value || ''
                    })
                });

                if (response.ok) {
                    setTimeout(() => {
                        addMessage(script.thank_you, false);
                        chatState = 'end';
                        pendingTicketId = '';
                    }, 500);
                } else {
                    throw new Error('Failed to submit rating');
                }
            } catch (error) {
                console.error('Rating submission error:', error);
                addMessage('Sorry, there was an error submitting your rating. Please try again.', false);
                chatState = 'rating';
            }
        }

        function showSuggestionsInChat() {
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            
            const suggestionDiv = document.createElement('div');
            suggestionDiv.className = 'message bot';
            
            let suggestionsHtml = `
                <div class="suggestion-message">
                    <div class="suggestion-title">${script.suggestions_title}</div>
                    <div class="suggestion-list">
            `;
            
            script.suggestions.forEach((suggestion, index) => {
                suggestionsHtml += `<div class="suggestion-item" data-suggestion="${index}">${suggestion}</div>`;
            });
            
            suggestionsHtml += `
                    </div>
                </div>
            `;
            
            suggestionDiv.innerHTML = `
                <div class="message-content">
                    ${suggestionsHtml}
                    <div class="message-time">${getCurrentTime()}</div>
                </div>
            `;
            
            elements.chatMessages.insertBefore(suggestionDiv, elements.typingIndicator);
            scrollToBottom();
            
            suggestionDiv.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    const suggestionIndex = parseInt(e.target.dataset.suggestion);
                    const suggestion = script.suggestions[suggestionIndex];
                    handleQuickSuggestion(suggestion);
                });
            });
        }

        function showTicketInput() {
            chatState = 'awaiting_ticket_id';
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            
            const promptMsg = currentLanguage === 'en' 
                ? "Please enter your Ticket ID (e.g., TKT-12345678) or Mobile Number (e.g., 9876543210) to check status:"
                : "कृपया स्थिती तपासण्यासाठी आपला तिकीट क्रमांक (उदा. TKT-12345678) किंवा मोबाइल नंबर (उदा. 9876543210) प्रविष्ट करा:";
            
            addMessage(promptMsg, false);
            
            const placeholderMsg = currentLanguage === 'en'
                ? "Enter Ticket ID or Mobile Number..."
                : "तिकीट क्रमांक किंवा मोबाइल नंबर प्रविष्ट करा...";
            
            elements.chatInput.placeholder = placeholderMsg;
            elements.chatInput.focus();
        }

        async function fetchTicketStatus(ticketId, language) {
            try {
                const response = await fetch(`${API_BASE_URL}/ticket/status/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticket_id: ticketId, language: language })
                });
                const data = await response.json();
                if (response.ok && data.found) {
                    return { success: true, message: data.message };
                } else if (response.status === 404) {
                    return { success: false, message: data.message || "Ticket not found." };
                } else {
                    return { success: false, message: "Sorry, no ticket found with the provided ID. Please check your Ticket ID and try again." };
                }
            } catch (error) {
                console.error("Network error", error);
                return { success: false, message: "Error connecting to server." };
            }
        }

        async function processTicketId(input) {
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            
            const ticketPattern = /^TKT-[A-Za-z0-9]{6,}$/i;
            const mobilePattern = /^[6-9]\d{9}$/;
            
            const isValidTicketId = ticketPattern.test(input.trim());
            const isValidMobileNumber = mobilePattern.test(input.replace(/\D/g, ''));
            
            if (!isValidTicketId && !isValidMobileNumber) {
                setTimeout(() => {
                    const errorMsg = currentLanguage === 'en' 
                        ? "Please provide a valid Ticket ID (e.g., TKT-12345678) or 10-digit mobile number (e.g., 9876543210)."
                        : "कृपया वैध तिकीट क्रमांक (उदा. TKT-12345678) किंवा 10-अंकी मोबाइल नंबर (उदा. 9876543210) प्रदान करा.";
                    addMessage(errorMsg, false);
                    setTimeout(() => {
                        showTicketInput();
                    }, 1500);
                }, 1000);
                return;
            }

            showTypingIndicator();

            try {
                const cleanInput = isValidMobileNumber ? input.replace(/\D/g, '') : input.trim();
                const result = await fetchTicketStatus(cleanInput, currentLanguage);

                if (result.success) {
                    hideTypingIndicator();
                    
                    const formattedStatus = formatTicketStatus(result.message);
                    
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message bot';
                    messageDiv.innerHTML = `
                        <div class="message-content">
                            ${formattedStatus}
                            <div class="message-time">${getCurrentTime()}</div>
                        </div>
                    `;
                    elements.chatMessages.insertBefore(messageDiv, elements.typingIndicator);
                    scrollToBottom();
                    
                    pendingTicketId = cleanInput;
                    setTimeout(() => {
                        chatState = 'question3';
                        addOptionsMessage(script.question3, [script.yes, script.no]);
                    }, 2000);
                } else {
                    hideTypingIndicator();
                    addMessage(result.message, false);
                    setTimeout(() => {
                        showTicketInput();
                    }, 1500);
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage("Error connecting to the server. Please try again.", false);
                setTimeout(() => {
                    showTicketInput();
                }, 1500);
            }
        }

        function handleQuickSuggestion(suggestion) {
            addMessage(suggestion, true);
            
            setTimeout(() => {
                processQuickSuggestion(suggestion);
            }, 500);
        }

        function processQuickSuggestion(suggestion) {
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            const lowerSuggestion = suggestion.toLowerCase();
            
            if (lowerSuggestion.includes('feedback') || lowerSuggestion.includes('अभिप्राय') || 
                lowerSuggestion.includes('द्यायचा')) {
                chatState = 'question3';
                setTimeout(() => {
                    addOptionsMessage(script.question3, [script.yes, script.no]);
                }, 500);
                return;
            }
            
            if (lowerSuggestion.includes('status') || lowerSuggestion.includes('check') || 
                lowerSuggestion.includes('स्थिती') || lowerSuggestion.includes('तपासायची')) {
                setTimeout(() => {
                    showTicketInput();
                }, 500);
                return;
            }
            
            if (lowerSuggestion.includes('register') || lowerSuggestion.includes('ticket') || 
                lowerSuggestion.includes('तिकीट') || lowerSuggestion.includes('नोंदवायची')) {
                
                chatState = 'start';
                setTimeout(() => {
                    addOptionsMessage(script.question1, [script.yes, script.no]);
                }, 500);
                return;
            }
            
            setTimeout(() => {
                addOptionsMessage(script.question1, [script.yes, script.no]);
                chatState = 'start';
            }, 500);
        }

        function handleUserChoice(optionIndex) {
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            
            switch (chatState) {
                case 'start':
                    if (optionIndex === 0) {
                        setTimeout(() => {
                            addLinkMessage(script.register_intro, script.register_link);
                            setTimeout(() => {
                                addMessage(script.thank_you);
                                chatState = 'end';
                            }, 1000);
                        }, 500);
                    } else {
                        setTimeout(() => {
                            addMessage(script.thank_you);
                            chatState = 'end';
                        }, 500);
                    }
                    break;
                
                case 'question2':
                    if (optionIndex === 0) {
                        setTimeout(() => {
                            showTicketInput();
                        }, 500);
                    } else {
                        chatState = 'question3';
                        setTimeout(() => {
                            addOptionsMessage(script.question3, [script.yes, script.no]);
                        }, 500);
                    }
                    break;
                
                case 'question3':
                    if (optionIndex === 0) {
                        setTimeout(() => {
                            addRatingMessage(script.rating_request);
                            chatState = 'awaiting_rating';
                        }, 500);
                    } else {
                        setTimeout(() => {
                            addMessage(script.thank_you);
                            chatState = 'end';
                        }, 500);
                    }
                    break;
            }
        }

        function toggleChatWindow() {
            isWindowOpen = !isWindowOpen;
            elements.chatWindow.style.display = isWindowOpen ? 'flex' : 'none';
            
            if (isWindowOpen) {
                if (!currentSessionId) {
                    currentSessionId = generateSessionId();
                }
                if (chatState === 'start' && elements.chatMessages.querySelectorAll('.message').length === 0) {
                    startConversation();
                }
            }
        }

        function startConversation() {
            const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
            
            const existingMessages = elements.chatMessages.querySelectorAll('.message');
            existingMessages.forEach(msg => msg.remove());
            
            pendingTicketId = '';
            chatState = 'start';
            
            setTimeout(() => {
                addMessage(script.welcome, false);
                setTimeout(() => {
                    showSuggestionsInChat();
                    setTimeout(() => {
                        addOptionsMessage(script.question1, [script.yes, script.no]);
                    }, 1000);
                }, 1000);
            }, 500);
        }

        function clearChat() {
            const messages = elements.chatMessages.querySelectorAll('.message, .status-indicator');
            messages.forEach(msg => msg.remove());
            chatState = 'start';
            selectedRating = null;
            pendingTicketId = '';
            currentSessionId = generateSessionId();
        }

        function updateLanguage(langCode) {
            const previousLanguage = currentLanguage;
            currentLanguage = langCode;
            
            updateUILanguage();
            
            if (isWindowOpen && elements.chatMessages.querySelectorAll('.message').length > 0) {
                const script = MAHA_AASTHA_SCRIPTS[currentLanguage];
                addMessage(script.language_switch_msg);
                setTimeout(() => {
                    startConversation();
                }, 1000);
            }
        }

        // Event Listeners
        elements.chatBubble.addEventListener('click', toggleChatWindow);
        elements.closeChat.addEventListener('click', toggleChatWindow);
        
        elements.chatInput.addEventListener('input', function() {
            const hasValue = this.value.trim().length > 0;
            elements.sendBtn.disabled = !hasValue;
        });

        elements.chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !elements.sendBtn.disabled) {
                sendUserMessage();
            }
        });

        elements.sendBtn.addEventListener('click', function() {
            if (!this.disabled) {
                sendUserMessage();
            }
        });

        elements.languageSelect.addEventListener('change', (e) => {
            updateLanguage(e.target.value);
        });
        
        elements.restartBtn.addEventListener('click', () => {
            startConversation();
        });
        
        elements.clearChatBtn.addEventListener('click', () => {
            clearChat();
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            console.log('Maha Aastha ChatBot initialized');
            currentSessionId = generateSessionId();
            
            elements.languageSelect.value = currentLanguage;
            
            updateUILanguage();
            
            console.log('Default language set to:', currentLanguage);
        });

        console.log('Maha Aastha ChatBot script loaded successfully');

    </script>
</body>
</html>
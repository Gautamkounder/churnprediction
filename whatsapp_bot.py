import os
import json
import logging
from flask import Flask, request, jsonify
import requests
import pandas as pd
import joblib
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load environment variables
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'your_verify_token_here')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

# Load ML models (if they exist)
try:
    model = joblib.load("xgboost_model.pkl")
    scaler = joblib.load("scaler.pkl")
    ml_models_loaded = True
    logger.info("ML models loaded successfully")
except Exception as e:
    logger.warning(f"Could not load ML models: {e}")
    ml_models_loaded = False

class WhatsAppBot:
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}"
        self.headers = {
            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, to_phone, message_text):
        """Send a text message via WhatsApp Business API"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"body": message_text}
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Message sent successfully to {to_phone}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def send_interactive_message(self, to_phone, header_text, body_text, buttons):
        """Send an interactive message with buttons"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {"type": "text", "text": header_text},
                "body": {"text": body_text},
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Interactive message sent successfully to {to_phone}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send interactive message: {e}")
            return False

class MessageProcessor:
    def __init__(self, whatsapp_bot):
        self.bot = whatsapp_bot
        self.user_sessions = {}  # Store user conversation state
    
    def process_message(self, phone_number, message_text, message_id):
        """Process incoming message and generate appropriate response"""
        logger.info(f"Processing message from {phone_number}: {message_text}")
        
        # Initialize user session if not exists
        if phone_number not in self.user_sessions:
            self.user_sessions[phone_number] = {
                'state': 'initial',
                'data': {},
                'last_interaction': datetime.now()
            }
        
        session = self.user_sessions[phone_number]
        session['last_interaction'] = datetime.now()
        
        message_lower = message_text.lower().strip()
        
        # Handle different conversation states
        if session['state'] == 'initial' or message_lower in ['hi', 'hello', 'start', 'menu']:
            self.send_welcome_message(phone_number)
        
        elif message_lower in ['predict', 'churn', 'prediction']:
            if ml_models_loaded:
                self.start_churn_prediction(phone_number)
            else:
                self.bot.send_message(phone_number, 
                    "Sorry, the prediction service is currently unavailable. Please try again later.")
        
        elif session['state'] == 'collecting_data':
            self.handle_data_collection(phone_number, message_text)
        
        elif message_lower in ['help', 'support']:
            self.send_help_message(phone_number)
        
        else:
            self.send_default_response(phone_number)
    
    def send_welcome_message(self, phone_number):
        """Send welcome message with options"""
        session = self.user_sessions[phone_number]
        session['state'] = 'menu'
        
        if ml_models_loaded:
            buttons = [
                {"type": "reply", "reply": {"id": "predict", "title": "📊 Churn Prediction"}},
                {"type": "reply", "reply": {"id": "help", "title": "❓ Help"}},
                {"type": "reply", "reply": {"id": "about", "title": "ℹ️ About"}}
            ]
            
            self.bot.send_interactive_message(
                phone_number,
                "🤖 Welcome to Customer Service Bot",
                "Hi! I'm your AI assistant. I can help you with customer churn predictions and answer your questions. What would you like to do?",
                buttons
            )
        else:
            self.bot.send_message(phone_number, 
                "🤖 Welcome to Customer Service Bot!\n\n"
                "I'm currently in maintenance mode. Please try again later or contact support for assistance.\n\n"
                "Type 'help' for more information.")
    
    def start_churn_prediction(self, phone_number):
        """Start the churn prediction process"""
        session = self.user_sessions[phone_number]
        session['state'] = 'collecting_data'
        session['data'] = {}
        session['current_field'] = 'CreditScore'
        
        self.bot.send_message(phone_number,
            "📊 Let's predict customer churn probability!\n\n"
            "I'll need some information from you. Let's start:\n\n"
            "Please enter the **Credit Score** (300-900):")
    
    def handle_data_collection(self, phone_number, message_text):
        """Handle data collection for churn prediction"""
        session = self.user_sessions[phone_number]
        current_field = session.get('current_field')
        
        try:
            if current_field == 'CreditScore':
                value = int(message_text)
                if 300 <= value <= 900:
                    session['data']['CreditScore'] = value
                    session['current_field'] = 'Geography'
                    self.bot.send_message(phone_number,
                        "✅ Credit Score saved!\n\n"
                        "Please select your **Geography**:\n"
                        "1. France\n"
                        "2. Spain\n"
                        "3. Germany\n\n"
                        "Reply with 1, 2, or 3:")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please enter a valid credit score between 300-900:")
            
            elif current_field == 'Geography':
                geo_map = {'1': 'France', '2': 'Spain', '3': 'Germany'}
                if message_text in geo_map:
                    session['data']['Geography'] = geo_map[message_text]
                    session['current_field'] = 'Gender'
                    self.bot.send_message(phone_number,
                        "✅ Geography saved!\n\n"
                        "Please select **Gender**:\n"
                        "1. Male\n"
                        "2. Female\n\n"
                        "Reply with 1 or 2:")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please reply with 1, 2, or 3 for geography:")
            
            elif current_field == 'Gender':
                gender_map = {'1': 'Male', '2': 'Female'}
                if message_text in gender_map:
                    session['data']['Gender'] = gender_map[message_text]
                    session['current_field'] = 'Age'
                    self.bot.send_message(phone_number,
                        "✅ Gender saved!\n\n"
                        "Please enter **Age** (18-100):")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please reply with 1 for Male or 2 for Female:")
            
            elif current_field == 'Age':
                value = int(message_text)
                if 18 <= value <= 100:
                    session['data']['Age'] = value
                    session['current_field'] = 'Tenure'
                    self.bot.send_message(phone_number,
                        "✅ Age saved!\n\n"
                        "Please enter **Tenure** (years with bank, 0-10):")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please enter a valid age between 18-100:")
            
            elif current_field == 'Tenure':
                value = int(message_text)
                if 0 <= value <= 10:
                    session['data']['Tenure'] = value
                    session['current_field'] = 'Balance'
                    self.bot.send_message(phone_number,
                        "✅ Tenure saved!\n\n"
                        "Please enter **Account Balance** (e.g., 50000.50):")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please enter a valid tenure between 0-10 years:")
            
            elif current_field == 'Balance':
                value = float(message_text)
                session['data']['Balance'] = value
                session['current_field'] = 'NumOfProducts'
                self.bot.send_message(phone_number,
                    "✅ Balance saved!\n\n"
                    "Please enter **Number of Products** (1-4):")
            
            elif current_field == 'NumOfProducts':
                value = int(message_text)
                if 1 <= value <= 4:
                    session['data']['NumOfProducts'] = value
                    session['current_field'] = 'HasCrCard'
                    self.bot.send_message(phone_number,
                        "✅ Number of Products saved!\n\n"
                        "Does customer **have a Credit Card**?\n"
                        "1. Yes\n"
                        "2. No\n\n"
                        "Reply with 1 or 2:")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please enter a number between 1-4:")
            
            elif current_field == 'HasCrCard':
                if message_text in ['1', '2']:
                    session['data']['HasCrCard'] = 1 if message_text == '1' else 0
                    session['current_field'] = 'IsActiveMember'
                    self.bot.send_message(phone_number,
                        "✅ Credit Card status saved!\n\n"
                        "Is customer an **Active Member**?\n"
                        "1. Yes\n"
                        "2. No\n\n"
                        "Reply with 1 or 2:")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please reply with 1 for Yes or 2 for No:")
            
            elif current_field == 'IsActiveMember':
                if message_text in ['1', '2']:
                    session['data']['IsActiveMember'] = 1 if message_text == '1' else 0
                    session['current_field'] = 'EstimatedSalary'
                    self.bot.send_message(phone_number,
                        "✅ Active Member status saved!\n\n"
                        "Finally, please enter **Estimated Salary** (e.g., 75000.00):")
                else:
                    self.bot.send_message(phone_number,
                        "❌ Please reply with 1 for Yes or 2 for No:")
            
            elif current_field == 'EstimatedSalary':
                value = float(message_text)
                session['data']['EstimatedSalary'] = value
                
                # All data collected, make prediction
                self.make_churn_prediction(phone_number, session['data'])
                
        except ValueError:
            self.bot.send_message(phone_number,
                "❌ Please enter a valid number.")
        except Exception as e:
            logger.error(f"Error in data collection: {e}")
            self.bot.send_message(phone_number,
                "❌ An error occurred. Let's start over. Type 'predict' to begin again.")
            session['state'] = 'menu'
    
    def make_churn_prediction(self, phone_number, data):
        """Make churn prediction using the ML model"""
        try:
            # Encode categorical values
            gender_encoded = 1 if data['Gender'] == 'Male' else 0
            geography_map = {"France": 0, "Spain": 1, "Germany": 2}
            geo_encoded = geography_map[data['Geography']]
            
            # Create input DataFrame
            input_data = pd.DataFrame([[
                data['CreditScore'], geo_encoded, gender_encoded, data['Age'], 
                data['Tenure'], data['Balance'], data['NumOfProducts'], 
                data['HasCrCard'], data['IsActiveMember'], data['EstimatedSalary']
            ]], columns=[
                'CreditScore', 'Geography', 'Gender', 'Age', 'Tenure', 'Balance',
                'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary'
            ])
            
            # Scale features and predict
            input_scaled = scaler.transform(input_data)
            prediction = model.predict(input_scaled)[0]
            probability = model.predict_proba(input_scaled)[0][1]
            
            # Format result message
            if prediction == 1:
                risk_level = "HIGH" if probability > 0.7 else "MEDIUM"
                message = (f"📊 **CHURN PREDICTION RESULT**\n\n"
                          f"🔴 **Risk Level: {risk_level}**\n"
                          f"❌ Customer likely to churn\n"
                          f"📈 Probability: {probability:.1%}\n\n"
                          f"💡 **Recommendations:**\n"
                          f"• Contact customer proactively\n"
                          f"• Offer retention incentives\n"
                          f"• Improve customer experience")
            else:
                message = (f"📊 **CHURN PREDICTION RESULT**\n\n"
                          f"🟢 **Risk Level: LOW**\n"
                          f"✅ Customer likely to stay\n"
                          f"📈 Retention probability: {(1-probability):.1%}\n\n"
                          f"💡 **Recommendations:**\n"
                          f"• Maintain current service level\n"
                          f"• Consider upselling opportunities\n"
                          f"• Keep customer engaged")
            
            self.bot.send_message(phone_number, message)
            
            # Reset session
            session = self.user_sessions[phone_number]
            session['state'] = 'menu'
            session['data'] = {}
            
            # Offer to predict again
            self.bot.send_message(phone_number,
                "\nWould you like to make another prediction? Type 'predict' or 'menu' for options.")
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            self.bot.send_message(phone_number,
                "❌ Sorry, there was an error processing your prediction. Please try again later.")
            session = self.user_sessions[phone_number]
            session['state'] = 'menu'
    
    def send_help_message(self, phone_number):
        """Send help information"""
        help_text = (
            "🆘 **HELP & SUPPORT**\n\n"
            "**Available Commands:**\n"
            "• 'predict' - Start churn prediction\n"
            "• 'menu' - Show main menu\n"
            "• 'help' - Show this help\n\n"
            "**About Churn Prediction:**\n"
            "Our AI model analyzes customer data to predict the likelihood of customer churn, helping businesses take proactive retention measures.\n\n"
            "**Need Human Support?**\n"
            "Contact our support team at support@yourcompany.com"
        )
        self.bot.send_message(phone_number, help_text)
    
    def send_default_response(self, phone_number):
        """Send default response for unrecognized messages"""
        self.bot.send_message(phone_number,
            "🤔 I didn't understand that. Type 'menu' to see available options or 'help' for assistance.")

# Initialize bot components
whatsapp_bot = WhatsAppBot()
message_processor = MessageProcessor(whatsapp_bot)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return challenge
    else:
        logger.warning("Webhook verification failed")
        return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        if 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if 'value' in change and 'messages' in change['value']:
                            for message in change['value']['messages']:
                                phone_number = message['from']
                                message_id = message['id']
                                
                                if message['type'] == 'text':
                                    message_text = message['text']['body']
                                    message_processor.process_message(
                                        phone_number, message_text, message_id
                                    )
                                elif message['type'] == 'interactive':
                                    # Handle button responses
                                    if 'button_reply' in message['interactive']:
                                        button_id = message['interactive']['button_reply']['id']
                                        message_processor.process_message(
                                            phone_number, button_id, message_id
                                        )
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_models_loaded': ml_models_loaded
    })

@app.route('/send-message', methods=['POST'])
def send_message_api():
    """API endpoint to send messages programmatically"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'error': 'phone_number and message are required'}), 400
        
        success = whatsapp_bot.send_message(phone_number, message)
        
        if success:
            return jsonify({'status': 'message sent successfully'})
        else:
            return jsonify({'error': 'failed to send message'}), 500
    
    except Exception as e:
        logger.error(f"Error in send_message_api: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if required environment variables are set
    if not WHATSAPP_TOKEN:
        logger.warning("WHATSAPP_TOKEN not set in environment variables")
    if not PHONE_NUMBER_ID:
        logger.warning("PHONE_NUMBER_ID not set in environment variables")
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting WhatsApp Bot server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
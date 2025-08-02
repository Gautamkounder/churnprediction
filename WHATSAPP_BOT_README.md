# 🤖 WhatsApp Chatbot Backend

A comprehensive WhatsApp chatbot backend built with Flask that integrates with the WhatsApp Business API and includes AI-powered customer churn prediction capabilities.

## 🚀 Features

- **WhatsApp Business API Integration**: Full webhook support for receiving and sending messages
- **Interactive Conversations**: Button-based menus and step-by-step data collection
- **AI-Powered Predictions**: Integrated customer churn prediction using XGBoost
- **Session Management**: Stateful conversations with user session tracking
- **Rate Limiting**: Built-in protection against spam and abuse
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Health Monitoring**: Health check endpoints for deployment monitoring
- **Flexible Configuration**: Environment-based configuration management

## 📁 Project Structure

```
.
├── whatsapp_bot.py          # Main Flask application
├── start_bot.py             # Production startup script
├── config.py                # Configuration management
├── test_bot.py              # Testing utilities
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── WHATSAPP_BOT_README.md   # This documentation
└── ML Models/
    ├── xgboost_model.pkl    # Trained churn prediction model
    └── scaler.pkl           # Feature scaler for ML model
```

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8+
- WhatsApp Business Account
- Facebook Developer Account
- ngrok (for local development)

### 2. WhatsApp Business API Setup

1. **Create Facebook App**:
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create a new app and add WhatsApp Business API
   - Note down your App ID and App Secret

2. **Get WhatsApp Credentials**:
   - Get your `WHATSAPP_TOKEN` (permanent access token)
   - Get your `PHONE_NUMBER_ID` from the WhatsApp Business API dashboard
   - Set up a webhook URL (use ngrok for local development)

3. **Configure Webhook**:
   - Webhook URL: `https://your-domain.com/webhook`
   - Verify Token: Choose a secure random string
   - Subscribe to `messages` webhook field

### 3. Installation

1. **Clone and Setup Environment**:
```bash
# Clone the repository (or copy the files)
cd your-project-directory

# Create virtual environment
python -m venv whatsapp_bot_env
source whatsapp_bot_env/bin/activate  # On Windows: whatsapp_bot_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Environment Configuration**:
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

3. **Configure Environment Variables**:
```env
# WhatsApp Business API Configuration
WHATSAPP_TOKEN=your_permanent_access_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_webhook_verify_token

# Flask Configuration
FLASK_ENV=development
PORT=5000

# Optional Configuration
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=10
SESSION_TIMEOUT_MINUTES=30
```

### 4. Local Development

1. **Start the Application**:
```bash
# Option 1: Direct start
python whatsapp_bot.py

# Option 2: Using startup script (recommended)
python start_bot.py

# Option 3: Development mode
FLASK_ENV=development python start_bot.py
```

2. **Set up ngrok for Local Testing**:
```bash
# Install ngrok (if not already installed)
# Download from https://ngrok.com/

# Expose your local server
ngrok http 5000

# Use the HTTPS URL for webhook configuration
# Example: https://abc123.ngrok.io/webhook
```

3. **Test the Bot**:
```bash
# Run automated tests
python test_bot.py

# Test specific functionality
python test_bot.py --test health
python test_bot.py --test conversation
```

## 🔧 API Endpoints

### Webhook Endpoints

#### `GET /webhook`
**Purpose**: Webhook verification for WhatsApp Business API
**Parameters**:
- `hub.mode`: Should be 'subscribe'
- `hub.verify_token`: Your verification token
- `hub.challenge`: Challenge string from WhatsApp

#### `POST /webhook`
**Purpose**: Receive incoming WhatsApp messages
**Body**: WhatsApp webhook payload
**Response**: `200 OK` with status message

### Utility Endpoints

#### `GET /health`
**Purpose**: Health check for monitoring
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "ml_models_loaded": true
}
```

#### `POST /send-message`
**Purpose**: Send messages programmatically
**Body**:
```json
{
  "phone_number": "+1234567890",
  "message": "Hello from the bot!"
}
```

## 🤖 Bot Features

### Conversation Flow

1. **Welcome Message**: Interactive buttons for main options
2. **Churn Prediction**: Step-by-step data collection
3. **Help System**: Comprehensive help and support information
4. **Error Handling**: Graceful error handling with user-friendly messages

### Supported Commands

- `hi`, `hello`, `start`, `menu` - Show welcome message
- `predict`, `churn`, `prediction` - Start churn prediction
- `help`, `support` - Show help information

### Churn Prediction Process

The bot collects the following information for churn prediction:

1. **Credit Score** (300-900)
2. **Geography** (France/Spain/Germany)
3. **Gender** (Male/Female)
4. **Age** (18-100)
5. **Tenure** (0-10 years)
6. **Account Balance**
7. **Number of Products** (1-4)
8. **Has Credit Card** (Yes/No)
9. **Is Active Member** (Yes/No)
10. **Estimated Salary**

After collecting all data, the bot provides:
- Churn probability percentage
- Risk level assessment
- Actionable recommendations

## 🚀 Deployment

### Docker Deployment

1. **Create Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "start_bot.py"]
```

2. **Build and Run**:
```bash
docker build -t whatsapp-bot .
docker run -p 5000:5000 --env-file .env whatsapp-bot
```

### Heroku Deployment

1. **Create Procfile**:
```
web: python start_bot.py
```

2. **Deploy**:
```bash
heroku create your-whatsapp-bot
heroku config:set WHATSAPP_TOKEN=your_token
heroku config:set PHONE_NUMBER_ID=your_phone_id
heroku config:set VERIFY_TOKEN=your_verify_token
git push heroku main
```

### Production Considerations

1. **Environment Variables**: Set all required environment variables
2. **HTTPS**: Ensure your webhook URL uses HTTPS
3. **Monitoring**: Set up monitoring for the `/health` endpoint
4. **Rate Limiting**: Configure appropriate rate limits
5. **Logging**: Set up log aggregation and monitoring
6. **Security**: Implement additional security measures as needed

## 🧪 Testing

### Automated Testing

```bash
# Run all tests
python test_bot.py

# Test specific components
python test_bot.py --test health
python test_bot.py --test webhook
python test_bot.py --test conversation

# Test against different URL
python test_bot.py --url https://your-production-url.com
```

### Manual Testing

1. **Send a message** to your WhatsApp Business number
2. **Test commands**: Try `hi`, `predict`, `help`
3. **Complete flow**: Go through the entire churn prediction process
4. **Error handling**: Test with invalid inputs

### Load Testing

For production environments, consider load testing:

```bash
# Example using Apache Bench
ab -n 100 -c 10 -H "Content-Type: application/json" \
   -p test_payload.json \
   https://your-bot-url.com/webhook
```

## 🔍 Monitoring and Logging

### Log Files

- **Application logs**: `whatsapp_bot.log`
- **Console output**: Real-time logging to stdout

### Key Metrics to Monitor

- Response time for webhook endpoints
- Message processing success rate
- ML model prediction accuracy
- User session completion rates
- Error rates and types

### Health Checks

Set up monitoring to regularly check:
- `GET /health` endpoint
- ML model loading status
- WhatsApp API connectivity

## 🔧 Customization

### Adding New Features

1. **New Commands**: Add to `MessageProcessor.process_message()`
2. **New Data Collection**: Extend `handle_data_collection()`
3. **New ML Models**: Update model loading in main application
4. **New APIs**: Add new Flask routes

### Configuration Options

All configuration is managed through environment variables:

- **Rate Limiting**: `RATE_LIMIT_PER_MINUTE`
- **Session Timeout**: `SESSION_TIMEOUT_MINUTES`
- **Model Paths**: `MODEL_PATH`, `SCALER_PATH`
- **Logging**: `LOG_LEVEL`

## 🐛 Troubleshooting

### Common Issues

1. **Webhook Verification Failed**:
   - Check VERIFY_TOKEN matches between WhatsApp and your app
   - Ensure webhook URL is accessible and uses HTTPS

2. **Messages Not Received**:
   - Verify webhook subscription in WhatsApp Business API
   - Check webhook URL and verify token

3. **ML Model Errors**:
   - Ensure model files exist and are accessible
   - Check model file compatibility with current Python/library versions

4. **Rate Limiting Issues**:
   - Adjust `RATE_LIMIT_PER_MINUTE` setting
   - Implement user-specific rate limiting if needed

### Debug Mode

Run in debug mode for development:

```bash
FLASK_ENV=development python start_bot.py
```

This enables:
- Detailed error messages
- Auto-reload on code changes
- Debug logging

## 📞 Support

For support and questions:

1. **Check logs**: Review application logs for error details
2. **Run tests**: Use `test_bot.py` to verify functionality
3. **WhatsApp Documentation**: [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp)
4. **Flask Documentation**: [Flask Documentation](https://flask.palletsprojects.com/)

## 📄 License

This project is provided as-is for educational and commercial use. Please ensure compliance with WhatsApp Business API terms of service and local regulations regarding automated messaging.

---

**Built with ❤️ using Flask, WhatsApp Business API, and XGBoost**
#!/usr/bin/env python3
"""
WhatsApp Bot Testing Utility
Test the bot functionality without WhatsApp API
"""

import json
import requests
import time
from datetime import datetime

class WhatsAppBotTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_phone = "+1234567890"
        
    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Status: {data['status']}")
                print(f"   ML Models Loaded: {data['ml_models_loaded']}")
                print(f"   Timestamp: {data['timestamp']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_webhook_verification(self):
        """Test webhook verification"""
        try:
            params = {
                'hub.mode': 'subscribe',
                'hub.verify_token': 'your_verify_token_here',
                'hub.challenge': 'test_challenge_123'
            }
            response = requests.get(f"{self.base_url}/webhook", params=params)
            
            if response.status_code == 200 and response.text == 'test_challenge_123':
                print("✅ Webhook verification passed")
                return True
            else:
                print(f"❌ Webhook verification failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Webhook verification error: {e}")
            return False
    
    def simulate_message(self, message_text):
        """Simulate receiving a WhatsApp message"""
        webhook_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": self.test_phone,
                            "id": f"msg_{int(time.time())}",
                            "type": "text",
                            "text": {"body": message_text}
                        }]
                    }
                }]
            }]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/webhook",
                json=webhook_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ Message processed: '{message_text}'")
                return True
            else:
                print(f"❌ Message processing failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Message processing error: {e}")
            return False
    
    def test_send_message_api(self, message):
        """Test the send message API endpoint"""
        data = {
            "phone_number": self.test_phone,
            "message": message
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/send-message",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"✅ Send message API test passed: '{message}'")
                return True
            else:
                print(f"❌ Send message API failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Send message API error: {e}")
            return False
    
    def run_conversation_test(self):
        """Run a full conversation test"""
        print("\n🤖 Starting conversation test...")
        
        conversation_flow = [
            "hi",
            "predict",
            "650",  # Credit Score
            "1",    # France
            "1",    # Male
            "35",   # Age
            "3",    # Tenure
            "50000", # Balance
            "2",    # Number of Products
            "1",    # Has Credit Card
            "1",    # Is Active Member
            "75000" # Estimated Salary
        ]
        
        for i, message in enumerate(conversation_flow):
            print(f"\nStep {i+1}: Sending '{message}'")
            success = self.simulate_message(message)
            if not success:
                print(f"❌ Conversation test failed at step {i+1}")
                return False
            time.sleep(1)  # Wait between messages
        
        print("✅ Conversation test completed!")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting WhatsApp Bot Tests")
        print("=" * 40)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Webhook Verification", self.test_webhook_verification),
            ("Simple Message", lambda: self.simulate_message("hello")),
            ("Help Command", lambda: self.simulate_message("help")),
            ("Menu Command", lambda: self.simulate_message("menu")),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)
        
        # Run conversation test
        print(f"\n🔍 Running Conversation Test...")
        conv_result = self.run_conversation_test()
        results.append(("Full Conversation", conv_result))
        
        # Print summary
        print("\n" + "=" * 40)
        print("📊 TEST SUMMARY")
        print("=" * 40)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nPassed: {passed}/{len(results)}")
        
        if passed == len(results):
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the logs above.")

def main():
    """Main testing function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test WhatsApp Bot')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL of the bot server')
    parser.add_argument('--test', choices=['health', 'webhook', 'message', 'conversation', 'all'],
                       default='all', help='Specific test to run')
    
    args = parser.parse_args()
    
    tester = WhatsAppBotTester(args.url)
    
    if args.test == 'health':
        tester.test_health_check()
    elif args.test == 'webhook':
        tester.test_webhook_verification()
    elif args.test == 'message':
        tester.simulate_message("hello")
    elif args.test == 'conversation':
        tester.run_conversation_test()
    else:
        tester.run_all_tests()

if __name__ == '__main__':
    main()
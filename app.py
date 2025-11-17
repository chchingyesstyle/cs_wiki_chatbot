from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import WikiChatbot
from config import Config
import traceback

app = Flask(__name__)
CORS(app)

# Initialize chatbot
print("Initializing chatbot...")
chatbot = None

try:
    chatbot = WikiChatbot()
    print("Chatbot initialized successfully")
except Exception as e:
    print(f"Error initializing chatbot: {e}")
    traceback.print_exc()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'chatbot_ready': chatbot is not None
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    if not chatbot:
        return jsonify({
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({
                'error': 'No question provided'
            }), 400
        
        # Get response from chatbot
        response = chatbot.chat(question)
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Chat error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    config = Config()
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

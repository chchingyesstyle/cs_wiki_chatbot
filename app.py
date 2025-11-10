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

@app.route('/api/search', methods=['GET'])
def search():
    """Search wiki pages endpoint"""
    if not chatbot:
        return jsonify({
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({
                'error': 'No query provided'
            }), 400
        
        # Search pages
        results = chatbot.db.search_pages(query, limit=limit)
        
        # Format results
        formatted_results = []
        for result in results:
            # Handle bytes from database
            page_title = result['page_title']
            if isinstance(page_title, bytes):
                page_title = page_title.decode('utf-8', errors='ignore')
            page_title = page_title.replace('_', ' ')
            
            content = result.get('content', '')
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            formatted_results.append({
                'page_id': result['page_id'],
                'title': page_title,
                'snippet': chatbot.clean_wiki_text(content)[:200] + '...'
            })
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results)
        })
    
    except Exception as e:
        print(f"Search error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/pages', methods=['GET'])
def list_pages():
    """List all wiki pages"""
    if not chatbot:
        return jsonify({
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        limit = int(request.args.get('limit', 50))
        pages = chatbot.db.get_all_pages(limit=limit)
        
        formatted_pages = []
        for page in pages:
            # Handle bytes from database
            page_title = page['page_title']
            if isinstance(page_title, bytes):
                page_title = page_title.decode('utf-8', errors='ignore')
            page_title = page_title.replace('_', ' ')
            
            formatted_pages.append({
                'page_id': page['page_id'],
                'title': page_title
            })
        
        return jsonify({
            'pages': formatted_pages,
            'count': len(formatted_pages)
        })
    
    except Exception as e:
        print(f"List pages error: {e}")
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

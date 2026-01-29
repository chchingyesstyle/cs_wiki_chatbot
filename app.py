from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import WikiChatbot
from feedback_store import FeedbackStore
from index_wiki import reindex_wiki
from config import Config
import traceback
import uuid
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Initialize chatbot
print("Initializing chatbot...")
chatbot = None
feedback_store = None

# Conversation history storage (session_id -> list of {question, answer})
# In production, use Redis or database for persistence
conversation_history = defaultdict(list)
MAX_HISTORY_LENGTH = 5  # Keep last 5 exchanges per session
SESSION_TIMEOUT_HOURS = 24

try:
    chatbot = WikiChatbot()
    print("Chatbot initialized successfully")
except Exception as e:
    print(f"Error initializing chatbot: {e}")
    traceback.print_exc()

# Initialize feedback store
try:
    feedback_store = FeedbackStore()
    feedback_store.initialize()
    print("Feedback store initialized successfully")
except Exception as e:
    print(f"Error initializing feedback store: {e}")
    traceback.print_exc()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    vector_store_status = {
        'enabled': False,
        'documents': 0
    }

    if chatbot and chatbot.vector_store:
        try:
            vector_store_status = {
                'enabled': True,
                'documents': chatbot.vector_store.collection.count()
            }
        except:
            vector_store_status['enabled'] = False

    return jsonify({
        'status': 'ok',
        'chatbot_ready': chatbot is not None,
        'vector_store': vector_store_status
    })


@app.route('/api/reindex', methods=['POST'])
def reindex_vectordb():
    """
    Reindex wiki pages into vector database.
    
    Request body (optional):
    {
        "confirm": true,           # Required to start reindex
        "clear_existing": true     # Clear existing vectors before indexing (default: true)
    }
    
    This will:
    1. Connect to MediaWiki database
    2. Fetch all wiki pages
    3. Clean and filter content (skip redirects, outdated pages)
    4. Re-create vector embeddings
    5. Store in ChromaDB
    
    Note: This does NOT affect feedback data (separate collection).
    """
    try:
        data = request.get_json() or {}
        
        # Require confirmation to prevent accidental long-running operation
        if not data.get('confirm'):
            # Get current stats
            current_docs = 0
            if chatbot and chatbot.vector_store:
                try:
                    current_docs = chatbot.vector_store.collection.count()
                except:
                    pass
            
            return jsonify({
                'error': 'Confirmation required. Send {"confirm": true} to start reindexing.',
                'warning': 'This will refresh all wiki vectors. May take 2-5 minutes.',
                'current_documents': current_docs
            }), 400
        
        clear_existing = data.get('clear_existing', True)
        
        # Run reindexing
        result = reindex_wiki(clear_existing=clear_existing)
        
        if result['success']:
            # Reinitialize chatbot's vector store to pick up new data
            if chatbot and chatbot.vector_store:
                try:
                    chatbot.vector_store.initialize()
                except:
                    pass
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'pages_found': result['pages_found'],
                'pages_indexed': result['pages_indexed'],
                'pages_skipped': result['pages_skipped']
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message'],
                'errors': result['errors']
            }), 500
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with conversation history support"""
    if not chatbot:
        return jsonify({
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '')
        session_id = data.get('session_id', '')
        
        if not question:
            return jsonify({
                'error': 'No question provided'
            }), 400
        
        # Generate session_id if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get conversation history for this session
        history = conversation_history.get(session_id, [])
        
        # Get response from chatbot with history
        response = chatbot.chat(question, history=history)
        
        # Store this exchange in history
        conversation_history[session_id].append({
            'question': question,
            'answer': response['answer'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Trim history to max length
        if len(conversation_history[session_id]) > MAX_HISTORY_LENGTH:
            conversation_history[session_id] = conversation_history[session_id][-MAX_HISTORY_LENGTH:]
        
        # Add session_id to response
        response['session_id'] = session_id
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Chat error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500


# ============== FEEDBACK ENDPOINTS ==============

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit user feedback on a chatbot response
    
    Request body:
    {
        "question": "user question",
        "answer": "chatbot answer",
        "rating": "up" or "down",
        "sources": [...],           # optional
        "correction": "correct answer",  # optional, for bad answers
        "comment": "user comment"   # optional
    }
    """
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        data = request.get_json()
        
        question = data.get('question', '')
        answer = data.get('answer', '')
        rating = data.get('rating', '')
        
        if not question or not answer or not rating:
            return jsonify({
                'error': 'Missing required fields: question, answer, rating'
            }), 400
        
        if rating not in ['up', 'down']:
            return jsonify({
                'error': 'Rating must be "up" or "down"'
            }), 400
        
        feedback_id = feedback_store.save_feedback(
            question=question,
            answer=answer,
            rating=rating,
            sources=data.get('sources'),
            correction=data.get('correction'),
            user_comment=data.get('comment'),
            session_id=data.get('session_id'),
            retrieval_method=data.get('retrieval_method')
        )
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Thank you for your feedback!'
        })
    
    except Exception as e:
        print(f"Feedback error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/stats', methods=['GET'])
def feedback_stats():
    """Get feedback statistics"""
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        stats = feedback_store.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/list', methods=['GET'])
def list_feedback():
    """
    List feedback entries with optional filters
    
    Query params:
    - rating: 'up' or 'down' (optional)
    - reviewed: 'true' or 'false' (optional)
    - limit: max results (default 100)
    """
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        rating = request.args.get('rating')
        reviewed_param = request.args.get('reviewed')
        limit = int(request.args.get('limit', 100))
        
        reviewed = None
        if reviewed_param == 'true':
            reviewed = True
        elif reviewed_param == 'false':
            reviewed = False
        
        feedback_list = feedback_store.get_feedback(
            rating=rating,
            reviewed=reviewed,
            limit=limit
        )
        
        return jsonify({
            'count': len(feedback_list),
            'feedback': feedback_list
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/search', methods=['GET'])
def search_feedback():
    """
    Search for similar feedback using semantic search
    
    Query params:
    - q: search query
    - limit: max results (default 5)
    """
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({'error': 'Missing query parameter: q'}), 400
        
        similar = feedback_store.search_similar_feedback(query, top_k=limit)
        
        return jsonify({
            'query': query,
            'count': len(similar),
            'results': similar
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/<feedback_id>/review', methods=['POST'])
def review_feedback(feedback_id):
    """
    Mark feedback as reviewed
    
    Request body (optional):
    {
        "notes": "reviewer notes"
    }
    """
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        data = request.get_json() or {}
        notes = data.get('notes')
        
        success = feedback_store.mark_reviewed(feedback_id, notes)
        
        if success:
            return jsonify({'success': True, 'message': 'Feedback marked as reviewed'})
        else:
            return jsonify({'error': 'Feedback not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/training-data', methods=['GET'])
def export_training_data():
    """
    Export positive feedback for fine-tuning or few-shot prompts
    
    Query params:
    - include_corrections: 'true' to include corrected negative feedback
    """
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        include_corrections = request.args.get('include_corrections', 'false') == 'true'
        
        training_data = feedback_store.get_training_data(only_positive=not include_corrections)
        
        return jsonify({
            'count': len(training_data),
            'data': training_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/clear', methods=['POST'])
def clear_feedback():
    """
    Clear all feedback entries (reset completely).
    
    Request body (optional):
    {
        "confirm": true  # Required to prevent accidental deletion
    }
    
    This is useful for:
    - Starting fresh with feedback collection
    - Removing outdated feedback after major wiki updates
    """
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        data = request.get_json() or {}
        
        # Require confirmation to prevent accidental deletion
        if not data.get('confirm'):
            return jsonify({
                'error': 'Confirmation required. Send {"confirm": true} to clear all feedback.',
                'warning': 'This will permanently delete all feedback entries!'
            }), 400
        
        # Get count before clearing
        stats = feedback_store.get_stats()
        count_before = stats.get('total', 0)
        
        success = feedback_store.clear_all()
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Cleared {count_before} feedback entries',
                'deleted_count': count_before
            })
        else:
            return jsonify({'error': 'Failed to clear feedback'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/<feedback_id>', methods=['DELETE'])
def delete_single_feedback(feedback_id):
    """Delete a single feedback entry by ID"""
    if not feedback_store:
        return jsonify({'error': 'Feedback store not initialized'}), 500
    
    try:
        success = feedback_store.delete_feedback(feedback_id)
        
        if success:
            return jsonify({'success': True, 'message': f'Deleted feedback {feedback_id}'})
        else:
            return jsonify({'error': 'Feedback not found or delete failed'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    config = Config()
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

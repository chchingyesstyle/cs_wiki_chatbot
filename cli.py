#!/usr/bin/env python3
"""
Simple CLI interface to test the chatbot
"""
from chatbot import WikiChatbot
import sys

def main():
    print("=" * 60)
    print("MediaWiki Chatbot CLI")
    print("=" * 60)
    print("Initializing chatbot...")
    
    try:
        bot = WikiChatbot()
        print("✓ Chatbot ready!")
        print("\nType your questions (or 'quit' to exit)\n")
        
        while True:
            try:
                question = input("\n🤔 You: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    bot.close()
                    break
                
                if not question:
                    continue
                
                print("\n🤖 Bot: Thinking...", end='\r')
                response = bot.chat(question)
                
                print(f"\n🤖 Bot: {response['answer']}")
                
                if response['sources']:
                    print(f"\n📚 Sources: {', '.join(response['sources'])}")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                bot.close()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

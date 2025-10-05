import asyncio
import os
from typing import List, AsyncGenerator
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    genai = None


class Chat:
    def __init__(self, max_tokens=2000, debug=False) -> None:
        self.debug = debug
        self.max_tokens = max_tokens
        
        if not HAS_GEMINI:
            raise ImportError("google-generativeai package is not installed. Please install it with: pip install google-generativeai")
        
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Initialize the model (using Gemini 2.5 Flash)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.7,
            top_p=1.0,
        )

    def __call__(self, chat_list: List):
        return self.chat(chat_list)

    def _format_chat_for_gemini(self, chat_list: List) -> str:
        """Convert chat list format to a single prompt for Gemini"""
        formatted_prompt = ""
        
        for role, content in chat_list:
            if role == 'system':
                formatted_prompt += f"System Instructions: {content}\n\n"
            elif role == 'user':
                formatted_prompt += f"User: {content}\n\n"
            elif role == 'assistant':
                formatted_prompt += f"Assistant: {content}\n\n"
        
        formatted_prompt += "Assistant: "
        return formatted_prompt

    async def chat(self, chat_list: List) -> AsyncGenerator[str, None]:
        """Generate streaming response from Gemini"""
        try:
            # Format the chat for Gemini
            prompt = self._format_chat_for_gemini(chat_list)
            
            # Generate response with streaming
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                stream=True
            )
            
            # Convert synchronous streaming to async
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    if self.debug:
                        print(chunk.text, end='')
                    yield chunk.text
                # Add a small delay to allow other async operations
                await asyncio.sleep(0.001)
            
            if self.debug:
                print('')
                
        except Exception as e:
            if self.debug:
                print(f"Error in chat: {e}")
            yield f"Error: {str(e)}"


if __name__ == '__main__':
    async def test_chat():
        from core import Person
        from prompts import BACKGROUND, EVENTS, RULES
        person = Person()
        chat = Chat(debug=True)
        chat_list = [RULES, BACKGROUND, ('user', str(person))]
        
        print("Testing Gemini integration...")
        async for text in chat.chat(chat_list):
            pass  # Text is already printed in debug mode
    
    asyncio.run(test_chat())

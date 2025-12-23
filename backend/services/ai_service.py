"""AI Service pentru traducere și rescriere știri"""
import logging
import os
from typing import Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    """Service pentru traducere și rescriere știri cu AI"""
    
    def __init__(self):
        # Try both key names
        self.api_key = os.getenv('EMERGENT_LLM_KEY') or os.getenv('EMERGENT_UNIVERSAL_KEY')
        self.model_provider = "openai"
        self.model_name = "gpt-4o-mini"
    
    async def translate_and_rewrite_article(self, article: dict) -> dict:
        """Traduce și rescrie un articol în română"""
        try:
            if not self.api_key:
                logger.warning("EMERGENT_LLM_KEY not found, returning original article")
                return article
            
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # Combine text for translation
            text_to_translate = f"""
Titlu: {title}

Descriere: {description}

Conținut: {content}
"""
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"translate_{hash(title)}",
                system_message="""Ești un jurnalist financiar profesionist care scrie în limba română. 
Trebuie să traduci și să rescrii articolele financiare în română, păstrând informațiile esențiale dar reformulând textul pentru a fi unic.

Regulile tale:
1. Traduce TOTUL în română
2. Rescrie textul în propriile tale cuvinte, nu traduce mot-a-mot
3. Păstrează toate datele și cifrele exacte
4. Folosește un stil jurnalistic profesional
5. Răspunde DOAR cu JSON în formatul: {"titlu": "...", "descriere": "...", "continut": "..."}
6. Nu adăuga comentarii sau explicații, doar JSON-ul"""
            ).with_model(self.model_provider, self.model_name)
            
            user_message = UserMessage(
                text=f"Traduce și rescrie acest articol financiar în română:\n\n{text_to_translate}"
            )
            
            response = await chat.send_message(user_message)
            
            # Parse JSON response
            import json
            try:
                # Clean response - remove markdown code blocks if present
                clean_response = response.strip()
                if clean_response.startswith('```'):
                    clean_response = clean_response.split('\n', 1)[1]
                if clean_response.endswith('```'):
                    clean_response = clean_response.rsplit('```', 1)[0]
                clean_response = clean_response.strip()
                
                translated = json.loads(clean_response)
                
                # Update article with translated content
                article['title_ro'] = translated.get('titlu', title)
                article['description_ro'] = translated.get('descriere', description)
                article['content_ro'] = translated.get('continut', content)
                article['is_translated'] = True
                article['language'] = 'ro'
                
                logger.info(f"Successfully translated article: {title[:50]}...")
                
            except json.JSONDecodeError:
                # If JSON parsing fails, use raw response
                article['content_ro'] = response
                article['is_translated'] = True
                logger.warning(f"JSON parsing failed, using raw response for: {title[:50]}...")
            
            return article
            
        except Exception as e:
            logger.error(f"Error translating article: {e}")
            article['is_translated'] = False
            return article
    
    async def get_news_summary(self, topic: str) -> Optional[str]:
        """Generează un sumar despre un topic (pentru pagina de detalii indici)"""
        try:
            if not self.api_key:
                return None
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"summary_{hash(topic)}",
                system_message="""Ești un analist financiar expert. Oferă informații scurte și relevante în limba română."""
            ).with_model(self.model_provider, self.model_name)
            
            user_message = UserMessage(
                text=f"Oferă un paragraf scurt (2-3 propoziții) despre {topic} din perspectiva pieței financiare actuale."
            )
            
            response = await chat.send_message(user_message)
            return response
            
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return None

ai_service = AIService()

import requests
import json
import streamlit as st
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION_DEEP = """
You are a top-tier senior clinical researcher and medical academic.
Your task is to write a highly detailed, comprehensive, and exhaustive literature review based on deep web research.

Structure of the Deep Literature Review:
1. Scientific Introduction: Establish the background, clinical significance, and current debate.
2. Comprehensive Literature Review & Synthesis:
   - Organize into logical sub-topics/themes.
   - For each theme, synthesize findings from multiple papers, clinical guidelines (e.g., ACC/AHA, ESC, ADA, WHO), or clinical trials.
   - Cite specific trials, researchers, or years mentioned in the source web results to make the report rigorous and believable.
3. Methodological and Clinical Gaps: What are the limitations of current studies, or what remains controversial?
4. Future Research Directions & Clinical Practice Impact: Practical takeaway for clinicians.
5. Rigorous References: Provide a detailed reference list with titles, active URLs, and brief annotations.

Tone and Language: Professional, clinical, and precise. Use the language of the user's query unless specified.
"""

def optimize_search_prompt_with_gemini(user_query: str, api_key: str, model_name: str = "gemini-2.5-flash") -> str:
    """
    Step 1: Uses Gemini to analyze the user's Vietnamese/English query,
    translate it into an optimized, highly-specific English academic search query
    containing medical terminology, MeSH terms, and search operators.
    """
    client = genai.Client(api_key=api_key)
    system_prompt = (
        "You are a medical research expert. Translate and optimize the user's query into "
        "a highly effective English search query for medical literature (like PubMed/Google Scholar). "
        "Include medical keywords, scientific terminology, synonyms, and search syntax if useful. "
        "Return ONLY the optimized search string. No introduction, no quotes."
    )
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=f"Optimize this search: {user_query}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
        )
        return response.text.strip()
    except Exception as e:
        # Fallback to simple English translation
        return user_query

def deep_search_with_perplexity(optimized_query: str, perplexity_key: str) -> dict:
    """
    Calls Perplexity AI API (sonar model) for deep literature search.
    """
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {perplexity_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert medical search engine. Answer the medical literature query in detail, citing scientific articles and including real URLs of research papers (from PubMed, Lancet, NEJM, Nature, etc.). Be extremely accurate, avoid any hallucination of links or citations."
            },
            {
                "role": "user",
                "content": f"Provide a comprehensive medical literature search and scientific report on: {optimized_query}"
            }
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        res_data = response.json()
        
        answer = res_data['choices'][0]['message']['content']
        citations = res_data.get('citations', [])
        
        # Format the citations as list of sources
        sources = []
        for idx, cite in enumerate(citations):
            sources.append({
                "title": f"Tài liệu tham khảo [{idx + 1}]",
                "url": cite
            })
            
        return {
            "success": True,
            "report": answer,
            "sources": sources,
            "engine": "Perplexity AI (Sonar Pro)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def deep_search_with_gemini(optimized_query: str, api_key: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Hybrid Deep Search: Uses Gemini 3.7 Flash with Google Search Grounding with optimized academic query.
    """
    client = genai.Client(api_key=api_key)
    prompt = (
        f"Hãy thực hiện một nghiên cứu y khoa chuyên sâu và viết một bài tổng quan tài liệu y học (Literature Review) "
        f"chi tiết, chất lượng cao về chủ đề sau:\n\n{optimized_query}\n\n"
        f"Hãy chắc chắn viết một bài viết hoàn chỉnh, khoa học, có cấu trúc học thuật rõ ràng, "
        f"và sử dụng chú thích nguồn [1], [2]..."
    )
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction=SYSTEM_INSTRUCTION_DEEP,
                temperature=0.3,
                max_output_tokens=8192,
            )
        )
        
        grounding_metadata = getattr(response.candidates[0], 'grounding_metadata', None)
        sources = []
        if grounding_metadata:
            grounding_chunks = getattr(grounding_metadata, 'grounding_chunks', [])
            for chunk in grounding_chunks:
                web = getattr(chunk, 'web', None)
                if web:
                    sources.append({
                        "title": getattr(web, 'title', 'Tài liệu tìm thấy'),
                        "url": getattr(web, 'uri', '')
                    })
                    
        return {
            "success": True,
            "report": response.text,
            "sources": sources,
            "engine": "Gemini Deep Search Engine"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

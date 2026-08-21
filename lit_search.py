import streamlit as st
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION_SEARCH = """
You are an expert scientific research assistant specializing in medicine, public health, and clinical research.
Your task is to analyze the user's research query, perform a thorough literature search using Google Search, and write a high-quality, comprehensive scientific review/report.

Requirements:
1. Scientific Tone: Use formal, objective, and precise scientific language (Vietnamese or English as requested by the query).
2. Evidence-Based: Every major medical claim, statistic, or clinical guideline MUST be backed by actual retrieved search results. Do not invent details.
3. Structure of the Report:
   - Executive Summary / Tóm tắt: A brief 3-4 sentence overview.
   - Key Findings / Các phát hiện chính: Detailed scientific points with inline citations (e.g., [1], [2]).
   - Discussion & Clinical Implications / Thảo luận & Ứng dụng lâm sàng: Deep scientific analysis of the topic.
   - References / Tài liệu tham khảo: List the exact websites, journals, or reports with titles and URLs.
4. Citation Integrity: Use inline citations [1], [2], etc., corresponding to the sources. Do NOT hallucinate sources. Only cite what was actually retrieved.
"""

def perform_literature_search(query: str, api_key: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Performs literature search using Gemini with Google Search Grounding.
    Returns a dictionary with the structured text report and list of source chunks with links.
    """
    if not api_key:
        raise ValueError("API Key is required.")
        
    client = genai.Client(api_key=api_key)
    
    # Prompting Gemini to research and write the report
    prompt = f"Hãy thực hiện tìm kiếm tài liệu khoa học và viết một báo cáo tổng quan y học chi tiết về chủ đề sau:\n\n{query}\n\nYêu cầu viết báo cáo hoàn chỉnh, có các phần rõ ràng, sử dụng chú thích nguồn [1], [2]..."
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction=SYSTEM_INSTRUCTION_SEARCH,
                temperature=0.3,
                max_output_tokens=8192,
            )
        )
        
        # Extract grounding metadata
        grounding_metadata = getattr(response.candidates[0], 'grounding_metadata', None)
        sources = []
        search_queries = []
        
        if grounding_metadata:
            # Get search queries used by Gemini
            web_queries = getattr(grounding_metadata, 'web_search_queries', [])
            if web_queries:
                search_queries = list(web_queries)
                
            # Get grounding chunks (sources)
            grounding_chunks = getattr(grounding_metadata, 'grounding_chunks', [])
            for chunk in grounding_chunks:
                web = getattr(chunk, 'web', None)
                if web:
                    sources.append({
                        "title": getattr(web, 'title', 'Nguồn tìm kiếm'),
                        "url": getattr(web, 'uri', '')
                    })
                    
        return {
            "report": response.text,
            "sources": sources,
            "queries": search_queries
        }
    except Exception as e:
        return {
            "report": f"Đã xảy ra lỗi khi tìm kiếm tài liệu: {str(e)}",
            "sources": [],
            "queries": []
        }

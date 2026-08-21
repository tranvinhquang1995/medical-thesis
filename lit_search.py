import streamlit as st
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION_SEARCH = """
You are an expert scientific research assistant specializing in medicine, public health, and clinical research.
Your task is to analyze the optimized research query (which contains both Vietnamese and English academic terms), perform a thorough literature search, and write a high-quality, comprehensive scientific review/report.

Requirements:
1. Scientific Tone: Use formal, objective, and precise scientific language (Vietnamese or English as requested by the query).
2. Evidence-Based: Every major medical claim, statistic, or clinical guideline MUST be backed by actual retrieved search results. Do not invent details.
3. Structure of the Report:
   - Executive Summary / Tóm tắt: A brief 3-4 sentence overview of the current status of research on this topic.
   - Key Findings / Các phát hiện chính: Detailed scientific points with inline citations (e.g., [1], [2]).
   - Discussion & Clinical Implications / Thảo luận & Ứng dụng lâm sàng: Deep scientific analysis of the topic.
   - References / Tài liệu tham khảo: List the exact websites, journals, or reports with titles and URLs.
4. Citation Integrity: Use inline citations [1], [2], etc., corresponding to the sources. Do NOT hallucinate sources. Only cite what was actually retrieved.
"""

def optimize_bilingual_search_prompt(user_query: str, api_key: str, model_name: str = "gemini-3.7-flash") -> str:
    """
    Analyzes the user's Vietnamese/English query,
    translates and expands it into a highly effective bilingual (English and Vietnamese)
    scientific search query for medical literature.
    """
    client = genai.Client(api_key=api_key)
    system_prompt = (
        "You are a medical research search expert. Your task is to analyze the user's research query "
        "(which could be in Vietnamese or English) and expand/optimize it into a highly effective "
        "bilingual (English and Vietnamese) scientific search query. "
        "Include scientific terms, key synonyms, and medical classifications in both English and Vietnamese "
        "so that the search can retrieve the best international and local clinical trials, reports, and papers. "
        "Return ONLY the optimized search string, combining English and Vietnamese medical terms "
        "naturally using standard search terms or basic boolean-like phrasing. Do not include quotes or explanations."
    )
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=f"Optimize this scientific search query into a bilingual EN/VI search query: {user_query}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"{user_query} medical literature clinical trials"

def perform_literature_search(query: str, api_key: str, model_name: str = "gemini-3.7-flash") -> dict:
    """
    Performs literature search using an AI engine with web search grounding.
    Returns a dictionary with the structured text report, the optimized query, and list of source chunks with links.
    """
    if not api_key:
        raise ValueError("Yêu cầu khóa API để thực hiện tìm kiếm.")
        
    client = genai.Client(api_key=api_key)
    
    # Step 1: Optimize prompt into bilingual terms
    optimized_query = optimize_bilingual_search_prompt(query, api_key, model_name)
    
    # Step 2: Prompt with Web Grounding
    prompt = (
        f"Hãy thực hiện tìm kiếm tài liệu khoa học và viết một báo cáo tổng quan y học chi tiết về chủ đề: {query}\\n\\n"
        f"Bạn có thể sử dụng chuỗi truy vấn đã được tối ưu hóa sau đây để tìm kiếm trên mạng:\\n"
        f"`{optimized_query}`\\n\\n"
        f"Yêu cầu viết báo cáo hoàn chỉnh, có các phần rõ ràng theo hướng dẫn hệ thống, sử dụng chú thích nguồn [1], [2]..."
    )
    
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
            # Get search queries used
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
            "optimized_query": optimized_query,
            "report": response.text,
            "sources": sources,
            "queries": search_queries
        }
    except Exception as e:
        return {
            "optimized_query": optimized_query,
            "report": f"Đã xảy ra lỗi khi tìm kiếm tài liệu: {str(e)}",
            "sources": [],
            "queries": []
        }

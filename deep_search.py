import requests
import json
import streamlit as st
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION_DEEP = """
You are a top-tier senior clinical researcher and medical academic.
Your task is to write a highly detailed, comprehensive, and exhaustive literature review based on deep scientific web research.

Structure of the Deep Literature Review:
1. Scientific Introduction: Establish the background, clinical significance, and current debate.
2. Comprehensive Literature Review & Synthesis:
   - Organize into logical sub-topics/themes.
   - For each theme, synthesize findings from multiple papers, clinical guidelines, or clinical trials.
   - Cite specific trials, researchers, or years mentioned in the source results to make the report rigorous and believable.
3. Methodological and Clinical Gaps: What are the limitations of current studies, or what remains controversial?
4. Future Research Directions & Clinical Practice Impact: Practical takeaway for clinicians.
5. Rigorous References: Provide a detailed reference list with titles, active URLs, and brief annotations.

Tone and Language: Professional, clinical, and precise. Use the language of the user's query unless specified.
"""

def optimize_search_prompt(user_query: str, api_key: str, model_name: str = "gemini-2.5-flash") -> str:
    """
    Step 1: Uses AI to analyze the user's Vietnamese/English query,
    translate it into an optimized, highly-specific English academic search query
    containing medical terminology, MeSH terms, and search syntax.
    """
    client = genai.Client(api_key=api_key)
    system_prompt = (
        "You are a medical research expert. Translate and optimize the user's query into "
        "a highly effective English search query for medical literature. "
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
        return user_query

def deep_search_with_gemini(optimized_query: str, api_key: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Hybrid Deep Search: Uses AI with web search grounding and optimized academic query.
    """
    client = genai.Client(api_key=api_key)
    prompt = (
        f"Hãy thực hiện một nghiên cứu y khoa chuyên sâu và viết một bài tổng quan tài liệu y học (Literature Review) "
        f"chi tiết, chất lượng cao về chủ đề sau:\\n\\n{optimized_query}\\n\\n"
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
            "engine": "Công cụ phân tích dữ liệu mạng chuyên sâu"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def deep_search_with_academic_db(optimized_query: str, api_key: str, model_name: str = "gemini-2.5-flash", limit: int = 5, db_api_key: str = None) -> dict:
    """
    Calls international academic database API to search for peer-reviewed papers, then feeds abstracts
    into AI to synthesize a structured Literature Review with active links.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": optimized_query,
        "limit": limit,
        "fields": "title,url,abstract,year,authors,citationCount,journal"
    }
    
    headers = {}
    if db_api_key:
        headers["x-api-key"] = db_api_key
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        papers = data.get("data", [])
        
        if not papers:
            return {
                "success": True,
                "report": f"Không tìm thấy bài báo y khoa nào khớp với từ khóa '{optimized_query}' trên cơ sở dữ liệu học thuật quốc tế.",
                "sources": [],
                "engine": "Cơ sở dữ liệu học thuật chuyên sâu"
            }
            
        papers_context = ""
        sources = []
        for idx, paper in enumerate(papers):
            title = paper.get("title", "No Title")
            paper_id = paper.get("paperId", "")
            paper_url = paper.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}"
            year = paper.get("year", "N/A")
            journal_info = paper.get("journal", {})
            journal_name = journal_info.get("name", "N/A") if journal_info else "N/A"
            citation_count = paper.get("citationCount", 0)
            abstract = paper.get("abstract") or "Abstract not available."
            
            authors_list = paper.get("authors", [])
            authors_str = ", ".join([a.get("name", "") for a in authors_list[:3]])
            if len(authors_list) > 3:
                authors_str += " et al."
                
            sources.append({
                "title": f"{title} ({year})",
                "url": paper_url
            })
            
            papers_context += (
                f"Paper [{idx + 1}]:\n"
                f"- Title: {title}\n"
                f"- Authors: {authors_str}\n"
                f"- Year: {year}\n"
                f"- Journal: {journal_name}\n"
                f"- Citations: {citation_count}\n"
                f"- URL: {paper_url}\n"
                f"- Abstract: {abstract}\n\n"
            )
            
        # Synthesize with AI
        client = genai.Client(api_key=api_key)
        prompt = (
            f"Dưới đây là {len(papers)} bài báo khoa học đã qua bình duyệt (peer-reviewed) "
            f"được tìm thấy trên hệ thống cơ sở dữ liệu học thuật cho truy vấn '{optimized_query}':\n\n"
            f"{papers_context}\n"
            f"Nhiệm vụ của bạn là đóng vai trò một giáo sư đầu ngành, viết một bài Tổng quan tài liệu y học (Literature Review) "
            f"bằng tiếng Việt chi tiết và khoa học dựa TRÊN VĂN BẢN của các bài báo trên.\n\n"
            f"Yêu cầu:\n"
            f"1. Bài viết phải có bố cục rõ ràng (Đặt vấn đề, Tổng quan & Phân tích chuyên sâu các nghiên cứu trên, So sánh/Đối chiếu, Khoảng trống nghiên cứu & Đề xuất thực hành lâm sàng).\n"
            f"2. BẮT BUỘC chỉ sử dụng thông tin từ các bài báo được cung cấp ở trên. Trích dẫn chính xác bằng số [1], [2]... tương ứng với mã số bài báo.\n"
            f"3. Trong mỗi đoạn phân tích, hãy cố gắng liên kết và tổng hợp thông tin từ nhiều bài báo cùng lúc để thấy được sự thống nhất hoặc khác biệt trong kết quả của các nghiên cứu.\n"
            f"4. Giữ nguyên thuật ngữ y khoa chuyên ngành, tên thuốc và các chữ viết tắt.\n"
            f"5. Đưa ra một phần tài liệu tham khảo liệt kê đầy đủ tiêu đề, năm xuất bản, tác giả và đường link URL của cả {len(papers)} bài báo trên."
        )
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION_DEEP,
                temperature=0.3,
                max_output_tokens=8192,
            )
        )
        
        return {
            "success": True,
            "report": response.text,
            "sources": sources,
            "engine": "Cơ sở dữ liệu học thuật quốc tế"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

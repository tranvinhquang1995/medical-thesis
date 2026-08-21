import os
import streamlit as st
from translator_text import translate_medical_text
from translator_file import translate_docx, translate_pdf
from lit_search import perform_literature_search
from deep_search import optimize_search_prompt, deep_search_with_gemini, deep_search_with_academic_db

# Set page configuration
st.set_page_config(
    page_title="Medical Thesis - Trợ Lý Nghiên Cứu Y Khoa",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Medical Theme (Teal and Blue)
st.markdown("""
<style>
    .main {
        background-color: #f7fafc;
    }
    .stApp {
        background-color: #f7fafc;
    }
    h1 {
        color: #0f4c5c;
        font-family: 'Segoe UI', sans-serif;
    }
    h2 {
        color: #e36414;
    }
    .stButton>button {
        background-color: #0f4c5c;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #fb8b24;
        color: white;
    }
    .api-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #ffeeba;
    }
</style>
""", unsafe_allow_html=True)

# Main Title and Description
st.title("🏥 Medical Thesis - Trợ Lý Nghiên Cứu Y Khoa")
st.markdown("---")

# Sidebar - Elegant Visual Header (Using emojis and CSS - NO external broken images!)
st.sidebar.markdown("""
<div style='text-align: center; margin-top: -20px;'>
    <span style='font-size: 5rem;'>🏥</span>
    <h2 style='color: #0f4c5c; font-size: 1.6rem; margin-top: 10px; margin-bottom: 5px; font-weight: 700;'>Medical Thesis</h2>
    <p style='color: #888888; font-size: 0.9rem; font-style: italic; margin-bottom: 25px;'>Trợ lý khoa học chuyên nghiệp</p>
</div>
""", unsafe_allow_html=True)

# --- BACKGROUND SECRETS & KEY INGESTION (Zero UI Clutter) ---
gemini_api_key = ""
s2_api_key = ""

try:
    if "GEMINI_API_KEY" in st.secrets:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
    elif "gemini_api_key" in st.secrets:
        gemini_api_key = st.secrets["gemini_api_key"]
except Exception:
    pass

try:
    if "SEMANTIC_SCHOLAR_API_KEY" in st.secrets:
        s2_api_key = st.secrets["SEMANTIC_SCHOLAR_API_KEY"]
    elif "semantic_scholar_api_key" in st.secrets:
        s2_api_key = st.secrets["semantic_scholar_api_key"]
except Exception:
    pass

# Default Model Selection (Handled in the background)
model_choice = "gemini-2.5-flash"

# --- SIDEBAR TAB NAVIGATION (Using beautiful, highlighted buttons) ---
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "📝 Dịch thuật văn bản"

st.sidebar.markdown("<h4 style='color: #0f4c5c; font-weight: 600; margin-bottom: 10px;'>📋 CHỨC NĂNG ỨNG DỤNG</h4>", unsafe_allow_html=True)

# Four interactive buttons for navigation
btn_text = "📝 Dịch thuật văn bản"
btn_file = "📂 Dịch file Docx, PDF"
btn_lit = "🔍 Tìm kiếm tài liệu"
btn_deep = "💡 Tìm kiếm chuyên sâu"

if st.sidebar.button(
    btn_text, 
    use_container_width=True, 
    type="primary" if st.session_state.current_tab == btn_text else "secondary"
):
    st.session_state.current_tab = btn_text

if st.sidebar.button(
    btn_file, 
    use_container_width=True, 
    type="primary" if st.session_state.current_tab == btn_file else "secondary"
):
    st.session_state.current_tab = btn_file

if st.sidebar.button(
    btn_lit, 
    use_container_width=True, 
    type="primary" if st.session_state.current_tab == btn_lit else "secondary"
):
    st.session_state.current_tab = btn_lit

if st.sidebar.button(
    btn_deep, 
    use_container_width=True, 
    type="primary" if st.session_state.current_tab == btn_deep else "secondary"
):
    st.session_state.current_tab = btn_deep

st.sidebar.markdown("---")
st.sidebar.info("""
**Medical Thesis** là ứng dụng hỗ trợ đắc lực cho sinh viên, bác sĩ, và nhà nghiên cứu y học trong việc dịch thuật tài liệu y văn và tổng hợp nghiên cứu khoa học chính xác.
""")

# Copyright notice added
st.sidebar.markdown(
    "<div style='text-align: center; color: #888888; font-size: 0.85rem; font-weight: 500; margin-top: 20px;'>"
    "Developed by Nobita"
    "</div>", 
    unsafe_allow_html=True
)

# Check API Key and halt main execution if missing
if not gemini_api_key:
    st.markdown("""
    <div class="api-warning">
        ⚠️ <strong>Yêu cầu cấu hình:</strong> Không tìm thấy <strong>Khóa dịch vụ chính (GEMINI_API_KEY)</strong> trong hệ thống secrets.<br>
        Vui lòng tạo tệp tin <code>.streamlit/secrets.toml</code> trong thư mục dự án của bạn và cấu hình như sau:<br>
        <pre>GEMINI_API_KEY = "Khóa_API_Của_Bạn"</pre>
    </div>
    """, unsafe_allow_html=True)
    st.info("Để lấy khóa dịch vụ miễn phí, vui lòng truy cập [AI Studio](https://aistudio.google.com/).")
    st.stop()

# --- FUNCTIONALITIES DISPATCH ---
if st.session_state.current_tab == btn_text:
    st.header("📝 Dịch thuật văn bản chuyên ngành")
    st.write("Sử dụng AI dịch thuật tối ưu hóa cho lĩnh vực y tế, giữ nguyên thuật ngữ viết tắt, biệt dược và tên thuốc.")
    
    col1, col2 = st.columns(2)
    with col1:
        direction = st.selectbox("Chọn chiều dịch:", ["EN -> VI", "VI -> EN"], index=0)
    with col2:
        st.write("")  # Empty spacing
        
    src_text = st.text_area("Nhập văn bản cần dịch:", height=250, placeholder="Nhập câu hoặc đoạn văn y khoa vào đây...")
    
    if st.button("Bắt đầu dịch"):
        if not src_text.strip():
            st.warning("Vui lòng nhập văn bản cần dịch.")
        else:
            with st.spinner("Đang tiến hành dịch thuật chuẩn y văn..."):
                translated = translate_medical_text(src_text, direction, gemini_api_key, model_choice)
                
                st.markdown("### Kết quả dịch thuật:")
                st.write(translated)
                st.success("Dịch hoàn tất!")
                st.download_button(
                    label="Tải kết quả về dạng file Text (.txt)",
                    data=translated,
                    file_name="medical_translation.txt",
                    mime="text/plain"
                )

elif st.session_state.current_tab == btn_file:
    st.header("📂 Dịch thuật tài liệu y khoa (DOCX, PDF)")
    st.write("Dịch thuật toàn bộ file tài liệu, giữ nguyên cấu trúc định dạng cơ bản và đảm bảo tính thống nhất ngữ cảnh thông qua hệ thống dịch thuật chuỗi.")
    
    direction = st.selectbox("Chọn chiều dịch file:", ["EN -> VI", "VI -> EN"], index=0)
    uploaded_file = st.file_uploader("Tải lên file tài liệu (chấp nhận .docx, .pdf):", type=["docx", "pdf"])
    
    if uploaded_file is not None:
        st.write(f"📁 Đang chọn file: **{uploaded_file.name}**")
        
        if st.button("Dịch file tài liệu"):
            # Create scratch directories
            os.makedirs("/workspace/scratch/downloads", exist_ok=True)
            
            # Save uploaded file to temp path
            temp_input_path = os.path.join("/workspace/scratch/downloads", uploaded_file.name)
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            progress_bar = st.progress(0, text="Đang chuẩn bị file...")
            
            # File translation process
            try:
                if uploaded_file.name.endswith(".docx"):
                    output_filename = f"translated_{uploaded_file.name}"
                    temp_output_path = os.path.join("/workspace/scratch/downloads", output_filename)
                    
                    with st.spinner("Đang dịch file Word tuần tự..."):
                        translate_docx(temp_input_path, temp_output_path, direction, gemini_api_key, model_choice, progress_bar)
                    
                elif uploaded_file.name.endswith(".pdf"):
                    # Translate PDF to translated Word file (highly recommended)
                    output_filename = f"translated_{uploaded_file.name.replace('.pdf', '.docx')}"
                    temp_output_path = os.path.join("/workspace/scratch/downloads", output_filename)
                    
                    with st.spinner("Đang chuyển đổi và dịch trang PDF tuần tự..."):
                        translate_pdf(temp_input_path, temp_output_path, direction, gemini_api_key, model_choice, progress_bar)
                
                # Check file size to verify output
                if os.path.exists(temp_output_path) and os.path.getsize(temp_output_path) > 0:
                    progress_bar.progress(1.0, text="Dịch hoàn tất!")
                    st.success("Tài liệu của bạn đã dịch thành công!")
                    
                    with open(temp_output_path, "rb") as file:
                        st.download_button(
                            label="📥 Tải xuống bản dịch (.docx)",
                            data=file,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Xử lý file thất bại hoặc file đầu ra trống.")
                    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình xử lý file: {str(e)}")

elif st.session_state.current_tab == btn_lit:
    st.header("🔍 Tìm kiếm tài liệu học thuật")
    st.write("Nhập từ khóa hoặc câu hỏi y học để hệ thống thực hiện tìm kiếm học thuật trực tuyến song ngữ Anh - Việt. Kết quả trả ra cam kết kèm theo nguồn gốc rõ ràng.")
    
    search_query = st.text_input("Nhập chủ đề hoặc từ khóa y văn cần tìm kiếm:", placeholder="Ví dụ: Thử nghiệm lâm sàng của thuốc điều trị ung thư phổi...")
    
    if st.button("Tìm kiếm tài liệu"):
        if not search_query.strip():
            st.warning("Vui lòng nhập từ khóa tìm kiếm.")
        else:
            with st.spinner("Hệ thống đang rà soát dữ liệu khoa học toàn cầu và tổng hợp báo cáo..."):
                results = perform_literature_search(search_query, gemini_api_key, model_choice)
                
                st.markdown("### 📊 Báo cáo tổng hợp tài liệu học thuật:")
                st.markdown(results["report"])
                
                # Show sources explicitly
                if results["sources"]:
                    st.markdown("---")
                    st.markdown("### 🔗 Các nguồn tài liệu uy tín tìm thấy:")
                    # Deduplicate sources
                    seen = set()
                    unique_sources = []
                    for s in results["sources"]:
                        if s["url"] not in seen:
                            seen.add(s["url"])
                            unique_sources.append(s)
                            
                    for idx, src in enumerate(unique_sources):
                        st.markdown(f"**[{idx+1}]** [{src['title']}]({src['url']})")
                else:
                    st.info("Không phát hiện thêm nguồn cụ thể từ siêu dữ liệu.")

elif st.session_state.current_tab == btn_deep:
    st.header("💡 Tìm kiếm tài liệu chuyên sâu")
    st.write("Hệ thống AI sẽ tự động phân tích câu hỏi, tối ưu hóa thành thuật ngữ tiếng Anh chuyên môn quốc tế và tiến hành truy cập trực tiếp cơ sở dữ liệu để tổng hợp báo cáo y văn chất lượng cao.")
    
    deep_query = st.text_area("Nhập yêu cầu nghiên cứu/câu hỏi khóa luận y văn của bạn:", height=100, placeholder="Ví dụ: Cơ chế tác dụng của vắc xin mRNA trong phòng ngừa biến chủng...")
    
    if st.button("Bắt đầu tìm kiếm chuyên sâu"):
        if not deep_query.strip():
            st.warning("Vui lòng điền nội dung nghiên cứu.")
        else:
            with st.status("Đang phân tích và tối ưu hóa từ khóa chuyên ngành...", expanded=True) as status:
                st.write("🤖 Đang dịch thuật và biên soạn sang thuật ngữ tiếng Anh chuyên môn...")
                optimized_eng_query = optimize_search_prompt(deep_query, gemini_api_key, model_choice)
                st.write(f"🔑 **Từ khóa chuyên sâu đã được tối ưu:** `{optimized_eng_query}`")
                
                st.write("🌍 Đang truy cập và khai thác cơ sở dữ liệu học thuật quốc tế...")
                
                # Call search with academic db
                results = deep_search_with_academic_db(
                    optimized_query=optimized_eng_query, 
                    api_key=gemini_api_key, 
                    model_name=model_choice,
                    db_api_key=s2_api_key if s2_api_key else None
                )
                
                status.update(label="Truy xuất hoàn tất!", state="complete", expanded=False)
                
            if results.get("success", False):
                st.markdown(f"### 🛡️ Báo cáo Tổng quan tài liệu y văn chuyên sâu:")
                st.markdown(results["report"])
                
                # Show sources explicitly
                if results["sources"]:
                    st.markdown("---")
                    st.markdown("### 📚 Danh mục bài báo khoa học chính xác:")
                    seen = set()
                    unique_sources = []
                    for s in results["sources"]:
                        if s["url"] not in seen and s["url"]:
                            seen.add(s["url"])
                            unique_sources.append(s)
                            
                    for idx, src in enumerate(unique_sources):
                        st.markdown(f"**[{idx+1}]** [{src['title']}]({src['url']})")
            else:
                st.error(f"Đã xảy ra lỗi: {results.get('error', 'Không xác định')}")

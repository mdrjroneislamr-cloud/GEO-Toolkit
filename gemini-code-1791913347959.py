import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from openai import OpenAI

# Page Title & Config
st.set_page_config(page_title="Automated GEO Toolkit", layout="wide")
st.title("🤖 GEO (Generative Engine Optimization) Toolkit")

st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

tab1, tab2, tab3 = st.tabs(["🔍 Technical & Schema Auditor", "🤖 AI Citation Tracker", "📄 llms.txt Generator"])

# -------------------------------------------------------------
# TAB 1: Technical & Schema Auditor
# -------------------------------------------------------------
with tab1:
    st.header("1. Technical & Schema Audit")
    url_input = st.text_input("Enter Website URL (e.g. https://example.com/page)")
    
    if st.button("Run Audit"):
        if url_input:
            with st.spinner("Analyzing web page..."):
                results = []
                
                # Check llms.txt
                base_url = "/".join(url_input.split("/")[:3])
                llm_url = f"{base_url}/llms.txt"
                try:
                    res = requests.get(llm_url, timeout=5)
                    llm_status = "✅ Found" if res.status_code == 200 else "❌ Not Found"
                except:
                    llm_status = "❌ Connection Failed"
                
                # Check Schema & Content
                try:
                    page = requests.get(url_input, timeout=5)
                    soup = BeautifulSoup(page.content, 'html.parser')
                    schemas = soup.find_all('script', type='application/ld+json')
                    headings = len(soup.find_all(['h1', 'h2', 'h3']))
                    
                    st.success("Audit Completed!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("llms.txt File", llm_status)
                    col2.metric("Schema Blocks Found", len(schemas))
                    col3.metric("Headings Count (H1-H3)", headings)
                    
                    if schemas:
                        st.subheader("Detected JSON-LD Schemas:")
                        for idx, s in enumerate(schemas):
                            try:
                                json_data = json.loads(s.string)
                                st.json(json_data)
                            except:
                                st.write(f"Schema {idx+1}: Raw Text (Parse Error)")
                    else:
                        st.warning("No JSON-LD Schema markup found on this page.")
                        
                except Exception as e:
                    st.error(f"Error checking site: {e}")

# -------------------------------------------------------------
# TAB 2: AI Citation Tracker
# -------------------------------------------------------------
with tab2:
    st.header("2. AI Citation & Share of Voice Tracker")
    brand_name = st.text_input("Your Brand/Website Name", "MyBrand")
    target_query = st.text_input("Target Query/Question", "What are the best tools for SEO?")
    
    if st.button("Check AI Citation"):
        if not api_key:
            st.error("Please provide your OpenAI API Key in the sidebar.")
        else:
            with st.spinner("Prompting GPT-4o..."):
                try:
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": target_query}]
                    )
                    ai_answer = response.choices[0].message.content
                    
                    is_cited = brand_name.lower() in ai_answer.lower()
                    
                    if is_cited:
                        st.success(f"🎉 Great news! '{brand_name}' was cited/mentioned in the AI answer.")
                    else:
                        st.warning(f"⚠️ '{brand_name}' was NOT mentioned in the AI response.")
                        
                    st.subheader("AI Generated Response:")
                    st.write(ai_answer)
                except Exception as e:
                    st.error(f"Error: {e}")

# -------------------------------------------------------------
# TAB 3: llms.txt Generator
# -------------------------------------------------------------
with tab3:
    st.header("3. Generate llms.txt")
    site_title = st.text_input("Site Title", "My Business Name")
    site_desc = st.text_area("Short Description", "Providing high-quality services.")
    links_text = st.text_area("Key Page URLs (One per line)", "https://example.com/about\nhttps://example.com/services")
    
    if st.button("Generate File"):
        links_list = links_text.split('\n')
        markdown_content = f"# {site_title}\n\n> {site_desc}\n\n## Core Resources\n"
        for link in links_list:
            if link.strip():
                markdown_content += f"- [{link.strip()}]({link.strip()})\n"
                
        st.subheader("Your `llms.txt` Content:")
        st.code(markdown_content, language="markdown")
        
        st.download_button(
            label="Download llms.txt",
            data=markdown_content,
            file_name="llms.txt",
            mime="text/plain"
        )
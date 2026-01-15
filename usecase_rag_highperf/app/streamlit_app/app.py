import streamlit as st
import asyncio
from api_client import check_health, search_api
from ui_presets import PRESETS

st.set_page_config(page_title="RAG High-Perf Demo", layout="wide")

st.title("🚀 RAG High-Perf Demo")
st.markdown("FastAPI + Valkey (Vector + Text) Hybrid Search Demo")

# Sidebar
with st.sidebar:
    st.header("Search Settings")
    
    # Check Health
    if st.button("Check Backend Health"):
        with st.spinner("Checking..."):
            health = asyncio.run(check_health())
            if health.get("status") == "ok":
                st.success(f"Connected! Ollama: {health.get('ollama')}")
            else:
                st.error(f"Failed: {health}")

    mode = st.radio("Search Mode", ["semantic", "keyword", "hybrid"], index=0)
    top_k = st.selectbox("Top K", [5, 10, 20, 50], index=0)
    
    weights = None
    if mode == "hybrid":
        st.subheader("Hybrid Weights")
        sem_w = st.slider("Semantic Weight", 0.0, 1.0, 0.5, 0.1)
        key_w = 1.0 - sem_w
        st.caption(f"Keyword Weight: {key_w:.1f}")
        weights = {"semantic": sem_w, "keyword": key_w}
        
    debug_mode = st.checkbox("Debug Mode", value=False)

# Main Area
if "query_input_widget" not in st.session_state:
    st.session_state.query_input_widget = ""

# Presets
st.subheader("Presets")
cols = st.columns(3)
for i, preset in enumerate(PRESETS):
    with cols[i % 3]:
        if st.button(f"{preset['label']}", help=preset['query'], use_container_width=True):
            st.session_state.query_input_widget = preset['query']
            st.rerun()

# Search Input
query = st.text_input("Enter your query:", key="query_input_widget")

if st.button("Search", type="primary") or query:
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner(f"Searching ({mode})..."):
            resp = asyncio.run(search_api(query, mode, top_k, weights))
            
            if "error" in resp:
                st.error(f"{resp['error']}: {resp.get('detail')}")
            else:
                results = resp.get("results", [])
                total = resp.get("total_found", 0)
                
                st.success(f"Found {total} results.")
                
                for r in results:
                    with st.container(border=True):
                        col1, col2 = st.columns([1, 10])
                        with col1:
                            st.metric("Rank", r["rank"])
                            score_key = "final" if mode == "hybrid" else ("vector" if mode == "semantic" else "bm25")
                            val = r["scores"].get(score_key, 0.0)
                            st.caption(f"Score: {val:.4f}")
                            
                        with col2:
                            st.markdown(f"**Doc ID:** `{r['doc_id']}`")
                            st.markdown(r['snippet'])
                            
                            if debug_mode:
                                st.json(r["scores"])

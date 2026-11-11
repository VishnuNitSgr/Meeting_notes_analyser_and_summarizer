import streamlit as st
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from decision_extractor import DecisionExtractor
from knowledge_graph import KnowledgeGraph
from simulator import ScenarioSimulator

st.set_page_config(page_title="🧠 AI Decision Simulator", layout="wide")

st.title("🧠 AI Meeting → Future Action Simulator")
st.markdown("*Extract decisions from meetings and simulate future consequences*")

# Initialization
if 'extractor' not in st.session_state:
    st.session_state.extractor = DecisionExtractor()
if 'graph' not in st.session_state:
    st.session_state.graph = KnowledgeGraph()
if 'simulator' not in st.session_state:
    st.session_state.simulator = ScenarioSimulator()
if 'extracted' not in st.session_state:
    st.session_state.extracted = None

# Sample transcript
sample_transcript = """
Meeting Date: 2024-09-07
Attendees: Product Manager, Engineering Lead, Marketing Head

Discussion:
- We will launch the product next Friday.
- Backend needs to be ready by Wednesday.
- Testing must be completed by Thursday.
- Marketing assets need to be ready by Wednesday.
- Deployment pipeline must be finalized by Thursday.

Risks discussed:
- Testing may be incomplete if backend is delayed.
- Marketing assets might be missing.
"""

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("### 📋 Input")
    transcript = st.text_area("Meeting Transcript", value=sample_transcript, height=300)
    
    if st.button("🔍 Extract Decisions", type="primary"):
        with st.spinner("Extracting decisions..."):
            extracted = st.session_state.extractor.extract(transcript)
            st.session_state.extracted = extracted
            st.session_state.graph.build(extracted)
        st.success("✅ Extraction Complete!")

# Main area startd here
if st.session_state.extracted:
    extracted = st.session_state.extracted
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Decisions")
        for d in extracted.get("decisions", []):
            st.write(f"✅ {d}")
        
        st.subheader("🔗 Dependencies")
        for decision, deps in extracted.get("dependencies", {}).items():
            st.write(f"**{decision}**")
            for dep in deps:
                st.write(f"  - {dep}")
        
        st.subheader("⚠️ Risks")
        for r in extracted.get("risks", []):
            st.write(f"⚠️ {r}")
    
    with col2:
        st.subheader("📊 Knowledge Graph")
        img_buf = st.session_state.graph.draw_graph()
        st.image(img_buf, use_container_width=True)
        
        graph_info = st.session_state.graph.get_graph_info()
        st.caption(f"Nodes: {graph_info['num_nodes']} | Edges: {graph_info['num_edges']}")
    
    st.markdown("---")
    st.subheader("🎬 Scenario Simulation")
    
    col_a, col_b = st.columns(2)
    with col_a:
        decision = st.selectbox("Select Decision", extracted.get("decisions", []))
        dependencies = extracted.get("dependencies", {}).get(decision, [])
        st.write("Dependencies:", ", ".join(dependencies))
    
    with col_b:
        change = st.text_input("What if...", "Backend delayed 2 days")
    
    if st.button("🚀 Simulate Future", type="primary"):
        with st.spinner("Simulating..."):
            result = st.session_state.simulator.simulate(
                decision, dependencies, extracted.get("risks", []), change
            )
        
        st.success("✅ Simulation Complete!")
        
        st.markdown("### 📉 Scenario")
        st.write(result.get("scenario", ""))
        
        st.markdown("### 🔗 Impact Chain")
        for i, step in enumerate(result.get("chain", [])):
            st.write(f"{i+1}. {step}")
        
        risk_level = result.get("risk_level", "UNKNOWN")
        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(risk_level, "⚪")
        st.metric("Risk Level", f"{risk_emoji} {risk_level}")
        
        st.markdown("### 💡 Recommendation")
        st.info(result.get("recommendation", ""))
        
        st.markdown("### 🛡️ Mitigation")
        st.warning(result.get("mitigation", ""))

else:
    st.info("👈 Paste a meeting transcript and click 'Extract Decisions' to begin.")

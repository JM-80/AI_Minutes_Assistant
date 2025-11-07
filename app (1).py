import os
import streamlit as st

# Optional import for LLM mode
try:
    import google.generativeai as genai
except Exception:
    genai = None

st.set_page_config(page_title="AI Meeting Minutes & Action Items", page_icon="📝")
st.title("📝 AI Meeting Minutes & Action Items")

st.markdown(
    "Paste raw meeting notes below. I’ll summarize key points, extract action items, "
    "and list risks/decisions. Works with **Gemini free API key** or in **Demo Mode** (no key)."
)

# --- Safe API key detection (works in Colab + Streamlit Cloud) ---
def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""

API_KEY = get_api_key()

# --- Input area ---
notes = st.text_area(
    "Paste meeting notes (bullets, rough text, or transcript)",
    height=220,
    placeholder="- Discussed onboarding delays...\n- Need ROI sheet by Friday...\n- Customer asked for RAG chatbot demo..."
)

col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Tone", ["Crisp professional", "Executive brief", "Detailed"])
with col2:
    include_due = st.checkbox("Suggest due dates", value=True)

run = st.button("Generate Summary & Actions")

# ---- demo-mode fallback extractor (no LLM) ----
def demo_extract(text: str, include_due: bool = True):
    lines = [ln.strip("-• ").strip() for ln in text.splitlines() if ln.strip()]
    actions = [ln for ln in lines if any(x in ln.lower() for x in ["need to", "action", "assign", "follow up", "deliver", "prepare", "send"])]
    risks   = [ln for ln in lines if any(x in ln.lower() for x in ["risk", "block", "issue", "delay", "concern"])]
    decisions = [ln for ln in lines if any(x in ln.lower() for x in ["decided", "agreed", "approved", "finalized"])]

    summary = lines[:5]
    if include_due and actions:
        actions = [a + " — **(suggested due: Fri EOW)**" for a in actions]

    return {
        "summary": summary if summary else ["(No obvious summary points found.)"],
        "actions": actions if actions else ["(No clear action items detected.)"],
        "risks": risks if risks else ["(No explicit risks/issues mentioned.)"],
        "decisions": decisions if decisions else ["(No explicit decisions captured.)"],
    }

# ---- LLM prompting (Gemini) ----
LLM_PROMPT = '''You are a Business Analyst assistant.
Given the raw meeting notes delimited by <notes>...</notes>, produce:

1) Executive Summary (4-8 bullets, {tone})
2) Action Items (bullet list with owner placeholder and {due})
3) Risks/Issues (bullet list)
4) Decisions (bullet list)

Keep it concise, professional, and structured in Markdown.
<notes>
{notes}
</notes>
'''

def llm_extract(text: str, tone_label: str, include_due_dates: bool):
    if not genai:
        raise RuntimeError("google-generativeai not installed.")
    if not API_KEY:
        raise RuntimeError("No GEMINI_API_KEY found in secrets or environment.")

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    due_phrase = "include suggested due dates" if include_due_dates else "no due dates necessary"
    prompt = LLM_PROMPT.format(tone=tone_label, due=due_phrase, notes=text)

    resp = model.generate_content(prompt)
    return resp.text if hasattr(resp, "text") else str(resp)

# ---- Run button ----
if run:
    if not notes.strip():
        st.warning("Please paste some notes first.")
    else:
        if API_KEY:
            try:
                st.info("Using Gemini LLM (API key detected).")
                output_md = llm_extract(notes, tone, include_due)
                st.markdown(output_md)
            except Exception as e:
                st.error(f"LLM mode failed: {e}")
                st.info("Falling back to Demo Mode (no LLM).")
                result = demo_extract(notes, include_due)
                st.subheader("Executive Summary")
                st.markdown("\n".join([f"- {p}" for p in result["summary"]]))
                st.subheader("Action Items")
                st.markdown("\n".join([f"- {p}" for p in result["actions"]]))
                st.subheader("Risks / Issues")
                st.markdown("\n".join([f"- {p}" for p in result["risks"]]))
                st.subheader("Decisions")
                st.markdown("\n".join([f"- {p}" for p in result["decisions"]]))
        else:
            st.info("No API key found — running in Demo Mode (rule-based).")
            result = demo_extract(notes, include_due)
            st.subheader("Executive Summary")
            st.markdown("\n".join([f"- {p}" for p in result["summary"]]))
            st.subheader("Action Items")
            st.markdown("\n".join([f"- {p}" for p in result["actions"]]))
            st.subheader("Risks / Issues")
            st.markdown("\n".join([f"- {p}" for p in result["risks"]]))
            st.subheader("Decisions")
            st.markdown("\n".join([f"- {p}" for p in result["decisions"]]))
else:
    st.caption("Tip: Try a few rough bullets, then click Generate. Add names to improve action-item extraction.")

import streamlit as st
import requests
import time
import random

# --- CONFIG ---
API_BASE = "https://zlr1ei5pz5.execute-api.us-west-2.amazonaws.com"
GET_PROFILE_URL = f"{API_BASE}/getUserCaseDetails"
SAVE_SUMMARY_URL = f"{API_BASE}/saveSummary"
INVOKE_AGENT_URL = f"{API_BASE}/invokeAgent"

# --- APP TITLE ---
st.set_page_config(page_title="Live Coaching Assistant", layout="wide")
st.title("🧕🏼 Live Coaching Assistant for Specialists")

# --- SESSION STATE ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "case_id" not in st.session_state:
    st.session_state.case_id = ""
if "summary" not in st.session_state:
    st.session_state.summary = None
if "mock_active" not in st.session_state:
    st.session_state.mock_active = False
if "suggested_question" not in st.session_state:
    st.session_state.suggested_question = ""
if "user_msg" not in st.session_state:
    st.session_state.user_msg = ""
if "need_victim_response" not in st.session_state:
    st.session_state.need_victim_response = False
if "need_agent_response" not in st.session_state:
    st.session_state.need_agent_response = False
if "show_custom_victim" not in st.session_state:
    st.session_state.show_custom_victim = False

# --- SIDEBAR CONFIG ---
st.sidebar.title("Case Setup")
st.session_state.case_id = st.sidebar.text_input("🔍 Enter Case ID", value="SA003")

if st.sidebar.button("📂 Load Victim Profile"):
    with st.spinner("Fetching profile..."):
        res = requests.post(GET_PROFILE_URL, json={"caseId": st.session_state.case_id})
        data = res.json()
        st.session_state.summary = data
        st.success("Victim profile loaded")

# --- DISPLAY PROFILE ---
if st.session_state.summary:
    profile = st.session_state.summary.get("profile", {})
    summaries = st.session_state.summary.get("summaries", [])
    latest_summary = summaries[0] if summaries else {}

    if profile:
        victim_info = profile.get("victim", {})
        st.subheader("📝 Victim Profile")
        st.markdown(f"**Name:** {victim_info.get('name', 'N/A')}")
        st.markdown(f"**Age:** {victim_info.get('age', 'N/A')}")
        st.markdown(f"**Nationality:** {victim_info.get('nationality', 'N/A')}")
        st.markdown(f"**Occupation:** {victim_info.get('occupation', 'N/A')}")
        st.markdown(f"**Marital Status:** {victim_info.get('marital_status', 'N/A')}")
        st.markdown(f"**Status:** {profile.get('status', 'N/A')}")
        st.markdown(f"**Latest Narrative:** {profile.get('latest_victim_narrative', 'N/A')}")
        st.markdown(f"**Last Summary:** {latest_summary.get('summaryText', 'No summary')} by {latest_summary.get('specialistName', 'Unknown')} at {latest_summary.get('formattedTimestamp', '-')}")

        if summaries:
            st.subheader("📚 Past Session Summaries")
            for i, summary in enumerate(summaries):
                with st.expander(f"🗂 Summary {i + 1} — {summary.get('formattedTimestamp', '')} by {summary.get('specialistName', 'Unknown')}"):
                    st.markdown(f"**Summary Text:** {summary.get('summaryText', 'N/A')}")
                    st.markdown(f"**Specialist Notes:** {summary.get('specialistNotes', 'N/A')}")
                    st.markdown(f"**Coaching Feedback:** {summary.get('coachingFeedback', 'N/A')}")
                    st.markdown("**Coaching Tips:**")
                    for tip in summary.get("coachingTips", []):
                        st.markdown(f"- {tip}")
                    st.markdown("**Next Steps:**")
                    for step in summary.get("nextSteps", []):
                        st.markdown(f"- {step}")

# --- MOCK MODE START BUTTON ---
st.markdown("---")
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🚀 Start Chatting with Mock Victim", use_container_width=True):
        st.session_state.mock_active = True
        victim_openers = [
            "أنا تعبت من كل يوم أرجع البيت وألقاه واقف تحت.",
            "أخاف أتكلم أحد عن اللي يصير، بس ما أقدر أتحمل أكثر.",
            "أحس ما في أمل، هو يراقبني دايم.",
            "ما عاد أنام زين من كثر التوتر والخوف."
        ]
        victim_msg = random.choice(victim_openers)
        st.session_state.chat.append({"sender": "👩 Victim", "message": victim_msg})
        
        # Set a flag to trigger agent response on next rerun
        st.session_state.need_agent_response = True
        
        # Force a rerun to display the victim message immediately
        st.rerun()

with col2:
    if st.button("🎭 Customize Victim Response", use_container_width=True):
        st.session_state.show_custom_victim = True
        st.rerun()

# --- CUSTOM VICTIM INPUT ---
if st.session_state.get("show_custom_victim", False):
    st.markdown('<div style="background-color: #fff3f3; padding: 15px; border-radius: 10px; border: 1px solid #ffcccc; margin: 15px 0;">', unsafe_allow_html=True)
    st.markdown("### 🎭 Custom Victim Message")
    custom_victim_msg = st.text_area("Type a custom victim message", height=100)
    custom_victim_col1, custom_victim_col2 = st.columns([3, 1])
    with custom_victim_col2:
        if st.button("Send Custom Message", use_container_width=True):
            if custom_victim_msg.strip():
                st.session_state.chat.append({"sender": "👩 Victim", "message": custom_victim_msg})
                st.session_state.show_custom_victim = False  # Hide the custom input after sending
                st.session_state.mock_active = True  # Activate mock mode
                
                # Set flag to trigger agent response on next rerun
                st.session_state.need_agent_response = True
                
                # Force a rerun to display the victim message immediately
                st.rerun()
            else:
                st.error("Please enter a message before sending.")
    with custom_victim_col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_custom_victim = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
# Handle agent response after victim's first message in a separate step
if st.session_state.get("need_agent_response", False):
    # Clear the flag
    st.session_state.need_agent_response = False
    
    # Get the last victim message
    last_victim_msg = None
    for msg in reversed(st.session_state.chat):
        if msg["sender"] == "👩 Victim":
            last_victim_msg = msg
            break
            
    if last_victim_msg:
        with st.spinner("🧠 Assistant is analyzing victim message..."):
            payload = {
                "sessionId": f"{st.session_state.case_id}-session-1",
                "inputText": "coach",
                "victimProfile": profile,
                "priorSummary": latest_summary.get("summaryText", ""),
                "conversationHistory": st.session_state.chat[:-1],
                "latestVictimMessage": last_victim_msg["message"]
            }
            try:
                agent_res = requests.post(INVOKE_AGENT_URL, json=payload)
                response_data = agent_res.json()
                if "message" in response_data:
                    result = response_data["message"]
                else:
                    result = f"No coaching response. API returned: {response_data}"
            except Exception as e:
                result = f"Error processing agent response: {str(e)}"
            
            st.session_state.chat.append({"sender": "🧠 Assistant", "message": result})

            # Extract suggested question
            for line in result.splitlines():
                if line.strip().startswith("فاطمة") or "؟" in line:
                    st.session_state.suggested_question = line.strip()
                    break

# --- CHAT INTERFACE ---
st.subheader("💬 Specialist - Victim Conversation")
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat:
        sender = msg['sender']
        timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        style = {
            "🧠 Assistant": "background-color:#eef2f7;border-left:5px solid #555;",
            "👩 Victim": "background-color:#ffe6e6;border-left:5px solid #d33;",
            "👩‍⚕️ Specialist": "background-color:#e6fff2;border-left:5px solid #2e8b57;"
        }.get(sender, "background-color:#f9f9f9;border-left:5px solid #999;")

        st.markdown(f"""
            <div style='{style}; color:#000; padding:10px; border-radius:6px; margin-bottom:8px;'>
                <b>{sender} <span style='float:right;font-size:12px;color:#555'>{timestamp}</span></b><br>{msg['message']}
            </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        if st.session_state.suggested_question:
            if st.button("💬 Use Suggested Question"):
                st.session_state.user_msg = st.session_state.suggested_question
        user_msg = st.text_input("Send a message to the victim", key="input", value=st.session_state.user_msg)
    with col2:
        send = st.button("Send")

    # Step 1: Handle sending specialist message immediately
    if send and user_msg:
        # Add specialist message immediately
        st.session_state.chat.append({"sender": "👩‍⚕️ Specialist", "message": user_msg})
        st.session_state.user_msg = ""  # clear after sending
        
        # Store that we need to add victim response on next render
        st.session_state.need_victim_response = True
        
        # Force a rerun to display the specialist message immediately
        st.rerun()
    
    # Step 2: Handle victim response and agent coaching separately
    if st.session_state.get("need_victim_response", False):
        # Clear the flag
        st.session_state.need_victim_response = False
        
        # Add victim response
        victim_replies = [
            "ما أعرف وش أسوي، كل يوم أحس بخوف أكثر.",
            "أنا ماني مرتاحة، حتى مع وجود أمر الحماية.",
            "هو يرسل لي رسائل من أرقام غريبة.",
            "أبغى أطلع من هالبيت، بس ما عندي مكان أروح له."
        ]
        mock_reply = random.choice(victim_replies)
        st.session_state.chat.append({"sender": "👩 Victim", "message": mock_reply})
        
        # Set flag to trigger agent response on next rerun
        st.session_state.need_agent_response = True
        
        # Force another rerun to display the victim message immediately
        st.rerun()

# --- END SESSION ---
st.markdown("---")
if st.button("📤 End Session & Summarize"):
    with st.spinner("Summarizing session..."):
        payload = {
            "sessionId": f"{st.session_state.case_id}-session-1",
            "inputText": "summarize the session",
            "victimProfile": profile,
            "priorSummary": latest_summary.get("summaryText", ""),
            "conversationHistory": st.session_state.chat,
            "latestVictimMessage": st.session_state.chat[-1]["message"] if st.session_state.chat else ""
        }
        try:
            agent_res = requests.post(INVOKE_AGENT_URL, json=payload, timeout=60)
            response_data = agent_res.json()
            if "message" in response_data:
                summary_text = response_data["message"]
            else:
                summary_text = f"No summary returned. API returned: {response_data}"
        except Exception as e:
            summary_text = f"Error processing summary: {str(e)}"
        st.session_state.generated_summary = summary_text

if "generated_summary" in st.session_state:
    st.subheader("🧾 Session Summary (Edit if needed)")
    edited = st.text_area("Review and edit before saving", st.session_state.generated_summary, height=250)
    specialist_name = st.text_input("👩‍⚕️ Specialist Name", value="Dr. Noura Al-Fayez")

    if st.button("✅ Confirm and Save Summary"):
        if not edited.strip():
            st.warning("⚠️ Summary text is empty. Please edit before saving.")
        elif not specialist_name.strip():
            st.warning("⚠️ Specialist name is required.")
        else:
            with st.spinner("🔍 Extracting and saving summary..."):
                def extract_between(full, start_marker, end_marker=None):
                    start = full.find(start_marker)
                    if start == -1:
                        return ""
                    start += len(start_marker)
                    if end_marker:
                        end = full.find(end_marker, start)
                        return full[start:end].strip() if end != -1 else full[start:].strip()
                    return full[start:].strip()

                full = edited
                summary_text = extract_between(full, "", "توصيات للمتابعة:").strip()
                coaching_tips_block = extract_between(full, "توصيات للمتابعة:", "ملاحظة للأخصائي:").splitlines()
                coaching_feedback = extract_between(full, "ملاحظة للأخصائي:")

                coaching_tips = [tip.strip("123٤٥٦.- ").strip() for tip in coaching_tips_block if tip.strip()]
                next_steps = coaching_tips

                save_payload = {
                    "caseId": st.session_state.case_id,
                    "summaryText": summary_text,
                    "specialistName": specialist_name,
                    "timestamp": str(int(time.time())),
                    "specialistNotes": "",
                    "coachingFeedback": coaching_feedback,
                    "coachingTips": coaching_tips,
                    "nextSteps": next_steps,
                    "generatedBy": "CoachingAgentV1"
                }

                res = requests.post(SAVE_SUMMARY_URL, json=save_payload)
                if res.status_code == 200:
                    st.success("✅ Summary saved successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save summary.")
                    st.code(res.text)

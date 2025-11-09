import streamlit as st
import random
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import base64
import time
import numpy as np

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Lucky Draw Wheel", layout="wide")
st.audio("audio/Walen - Gameboy (freetouse.com).mp3", format="audio/mpeg", autoplay=True, loop=True)

# --- Initialize Session States ---
if "attendees" not in st.session_state:
    st.session_state.attendees = []
if "remaining" not in st.session_state:
    st.session_state.remaining = []
if "winner" not in st.session_state:
    st.session_state.winner = None
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False
if "rotation" not in st.session_state:
    st.session_state.rotation = 0
if "winners" not in st.session_state:
    st.session_state.winners = []  # store all past winners

# --- Sidebar Input ---
page_title = st.sidebar.text_input("Enter Title", value="Enter Title")
st.title(f"🎡 {page_title}")
st.sidebar.header("Attendees List")
attendee_text = st.sidebar.text_area(
    "Paste attendee names (one per line):",
    height=250,
    placeholder="e.g.\nJohn Doe\nJane Tan\nMarcus Lee\n..."
)
shuffle = st.sidebar.checkbox("Shuffle the List?")
remove = st.sidebar.checkbox("Remove Winner After Each Spin?", value=True)
uploaded_image = st.sidebar.file_uploader("Upload Image for Winner Popup (optional)", type=["png", "jpg", "jpeg"])

if st.sidebar.button("Load Attendees"):
    names = [n.strip() for n in attendee_text.split("\n") if n.strip()]
    if shuffle:
        random.shuffle(names)
    st.session_state.attendees = names
    st.session_state.remaining = names.copy()
    st.session_state.winners = []  # reset winners when reload
    st.sidebar.success(f"Loaded {len(names)} attendees!")

# --- Draw Wheel Function ---
def draw_wheel(names, rotation=0, show_labels=True):
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))
    num = len(names)
    if num == 0:
        ax.text(0, 0, "No attendees", ha='center', va='center', fontsize=14)
        return fig

    colors = plt.cm.tab20.colors
    for i, name in enumerate(names):
        start = 360 * i / num + rotation
        end = 360 * (i + 1) / num + rotation
        wedge = Wedge((0, 0), 1, start, end, facecolor=colors[i % len(colors)], edgecolor="white")
        ax.add_patch(wedge)

        # choose fontsize based on total items
        if num <= 15:
            label_fontsize = 12
        elif num <= 30:
            label_fontsize = 9
        elif num <= 50:
            label_fontsize = 7
        else:
            label_fontsize = 5

        if show_labels:
            mid = (start + end) / 2
            x = 0.7 * math.cos(math.radians(mid))
            y = 0.7 * math.sin(math.radians(mid))
            ax.text(x, y, name, ha='center', va='center', fontsize=label_fontsize, rotation=mid, rotation_mode='anchor')

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")
    return fig

# --- Center layout for the wheel ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.session_state.remaining:
        fig = draw_wheel(st.session_state.remaining, st.session_state.rotation)
        wheel_placeholder = st.pyplot(fig)


    st.markdown("---")

    # IMPORTANT: Only show the Spin button when popup is NOT visible.
    if not st.session_state.show_popup:
        if st.button("🎯 Spin the Wheel!", use_container_width=True):
            n = len(st.session_state.remaining)
            if n == 0:
                st.warning("No more attendees to spin!")
            else:
                # 🎲 True random selection
                winner = random.choice(st.session_state.remaining)
                winner_index = st.session_state.remaining.index(winner)

                # 🎡 Determine rotation to land on winner
                slice_angle = 360 / n
                target_angle = (360 - (winner_index * slice_angle + slice_angle / 2)) % 360
                total_rotation = 5 * 360 + target_angle  # spin several rounds then land exactly

                # 🎬 Spin animation (fast)
                for angle in np.linspace(st.session_state.rotation, st.session_state.rotation + total_rotation, 20):
                    fig = draw_wheel(st.session_state.remaining, angle, show_labels=False)
                    wheel_placeholder.pyplot(fig)
                    time.sleep(0.005)

                st.session_state.rotation = (st.session_state.rotation + total_rotation) % 360

                # 🎉 Announce winner
                st.session_state.winner = winner
                if remove:
                    # remove winner from pool if checkbox set
                    st.session_state.remaining.remove(winner)
                st.session_state.winners.append(winner)
                st.session_state.show_popup = True
                st.balloons()
    else:
        # If popup is visible, inform user to close it
        st.info("Winner announced — close the popup to continue.")

# --- Display Winner Popup (robust close button inside popup feel) ---
if st.session_state.show_popup and st.session_state.winner:
    # prepare image HTML
    if uploaded_image is not None:
        img_bytes = uploaded_image.read()
        img_base64 = base64.b64encode(img_bytes).decode()
        image_html = f'<img src="data:image/png;base64,{img_base64}" class="popup-image" />'
    else:
        try:
            with open("img/default_confetti.png", "rb") as f:
                img_bytes = f.read()
                img_base64 = base64.b64encode(img_bytes).decode()
                image_html = f'<img src="data:image/png;base64,{img_base64}" class="popup-image" />'
        except Exception:
            # fallback external image
            image_html = '<img src="https://upload.wikimedia.org/wikipedia/commons/5/5a/Confetti.svg" class="popup-image" />'

    # popup HTML + CSS (popup box centered)
    popup_css = """
    <style>
    .popup-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.45);
        display: flex; align-items: center; justify-content: center;
        z-index: 9998;
    }
    .popup-box {
        background: #fff;
        border-radius: 18px;
        padding: 32px;
        width: min(90%, 900px);
        max-height: 90vh;
        overflow: auto;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.25);
        position: relative;
    }
    .popup-image {
        width: 80%;
        max-width: 600px;
        height: auto;
        border-radius: 12px;
        margin-top: 16px;
    }
    .popup-close {
        position: absolute;
        top: 12px;
        right: 12px;
        background: #ff4b4b;
        color: white;
        border: none;
        padding: 6px 10px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 18px;
    }
    </style>
    """

    popup_html = f"""
    <div class="popup-overlay" id="popup_overlay">
      <div class="popup-box" id="popup_box">
        <div style="font-size:28px; margin:0 0 8px 0;">🎉 Congratulations 🎉</div>
        <div style="font-size:44px; color:#2c7be5; font-weight:700; margin-bottom:10px;">{st.session_state.winner}</div>
        {image_html}
        <button class="popup-close" id="popup_close_html">✖</button>
      </div>
    </div>
    """

    # render popup HTML
    st.markdown(popup_css + popup_html, unsafe_allow_html=True)

    # Render a real Streamlit button that closes popup (server-side) and sits visually near top-right.
    # We render it AFTER the popup HTML, but we WILL NOT position it over the popup - instead we provide a clear button below the popup.
    # This button ensures server-side state is cleared when clicked (robust).
    if st.button("Close", key="popup_close_btn"):
        st.session_state.show_popup = False
        st.session_state.winner = None

    # Provide a small JS snippet that will forward clicks on the HTML '✖' button to click the Streamlit 'Close' button.
    # This avoids click-through issues and keeps server-side closing robust.
    js_bridge = """
    <script>
    (function() {
        const htmlBtn = window.parent.document.getElementById('popup_close_html');
        if (!htmlBtn) return;
        htmlBtn.addEventListener('click', () => {
            // find the Close button rendered by Streamlit and click it
            // The Streamlit button will be inside the iframe's document; we need to find it by label.
            const allButtons = Array.from(window.parent.document.querySelectorAll('button'));
            // find the one with innerText 'Close' (the Streamlit button)
            const streamlitCloseBtn = allButtons.find(b => b.innerText.trim() === 'Close');
            if (streamlitCloseBtn) {
                streamlitCloseBtn.click();
            } else {
                // fallback: hide popup visually (not server-side)
                const overlay = window.parent.document.getElementById('popup_overlay');
                if (overlay) overlay.style.display = 'none';
            }
        });
    })();
    </script>
    """
    st.components.v1.html(js_bridge, height=0)

# --- Remaining Count Display ---
if st.session_state.remaining:
    st.info(f"🧮 Remaining attendees: {len(st.session_state.remaining)}")
    show_remaining = st.checkbox("Show remaining attendees?")
    if show_remaining:
        st.write(st.session_state.remaining)
else:
    st.warning("No attendees left. Please reload a new list to start again.")

# --- Winner History Section ---
if st.session_state.winners:
    st.markdown("## 🏆 Selected Winners")
    cols = st.columns(min(len(st.session_state.winners), 5))  # up to 5 per row
    for i, winner in enumerate(st.session_state.winners):
        with cols[i % 5]:
            st.success(winner)

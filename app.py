import streamlit as st
import random
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import base64
import time
import numpy as np

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="NUP SAS Day 2025", layout="wide")
st.title("🎡 NUP SAS Day 2025 Lucky Draw")
st.audio("Walen - Gameboy (freetouse.com).mp3", format="audio/mpeg", autoplay=True, loop=True)

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
st.sidebar.header("Attendees List")
attendee_text = st.sidebar.text_area(
    "Paste attendee names (one per line):",
    height=250,
    placeholder="e.g.\nJohn Doe\nJane Tan\nMarcus Lee\n..."
)
uploaded_image = st.sidebar.file_uploader("Upload Image for Winner Popup (optional)", type=["png", "jpg", "jpeg"])

if st.sidebar.button("Load Attendees"):
    names = [n.strip() for n in attendee_text.split("\n") if n.strip()]
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

        if num > 30:
            label_fontsize = 14
        else:
            label_fontsize = 22

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

                # 🎬 Spin animation
                for angle in np.linspace(st.session_state.rotation, st.session_state.rotation + total_rotation, 20):
                    fig = draw_wheel(st.session_state.remaining, angle, show_labels=False)
                    wheel_placeholder.pyplot(fig)
                    time.sleep(0.0001)

                st.session_state.rotation = (st.session_state.rotation + total_rotation) % 360

                # 🎉 Announce winner
                st.session_state.winner = winner
                st.session_state.remaining.remove(winner)
                st.session_state.winners.append(winner)
                st.session_state.show_popup = True
                st.balloons()

# --- Winner Popup ---
if st.session_state.show_popup and st.session_state.winner:
    if uploaded_image is not None:
        img_bytes = uploaded_image.read()
        img_base64 = base64.b64encode(img_bytes).decode()
        image_html = f'<img src="data:image/png;base64,{img_base64}" width="500" style="border-radius:15px;margin-top:10px;">'
    else:
        with open("default_img.png", "rb") as f:
            img_bytes = f.read()
            img_base64 = base64.b64encode(img_bytes).decode()
            image_html = f'<img src="data:image/png;base64,{img_base64}" width="500" style="border-radius:15px;margin-top:10px;">'

    popup_css = """
    <style>
    .popup-overlay {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-color: rgba(0,0,0,0.35);
        display: flex; align-items: center; justify-content: center;
        z-index: 9999;
        pointer-events: none;
    }
    .popup-box {
        background: white;
        border-radius: 18px;
        padding: 24px 30px;
        text-align: center;
        box-shadow: 0 6px 30px rgba(0,0,0,0.25);
        pointer-events: auto;
        width: 800px;
        height: 800px;
        max-width: 1040px;
    }
    .popup-title { margin: 0 0 6px 0; font-size: 30px; }
    .popup-name { margin: 6px 0 12px 0; font-size: 50px; font-weight: bold; color: #2c7be5; }
    </style>
    """

    popup_html = f"""
    <div class="popup-overlay" id="popup_overlay">
      <div class="popup-box">
        <div class="popup-title">🎉 Congratulations 🎉</div>
        <div class="popup-name">{st.session_state.winner}</div>
        {image_html}
      </div>
    </div>
    """

    st.markdown(popup_css + popup_html, unsafe_allow_html=True)

    if st.button("OK", key="close_popup_btn"):
        st.session_state.show_popup = False
        st.session_state.winner = None

# --- Remaining Count Display ---
if st.session_state.remaining:
    st.info(f"🧮 Remaining attendees: {len(st.session_state.remaining)}")
else:
    st.warning("No attendees left. Please reload a new list to start again.")

# --- Winner History Section ---
if st.session_state.winners:
    st.markdown("## 🏆 Selected Winners")
    cols = st.columns(min(len(st.session_state.winners), 5))  # up to 5 per row
    for i, winner in enumerate(st.session_state.winners):
        with cols[i % 5]:
            st.success(winner)
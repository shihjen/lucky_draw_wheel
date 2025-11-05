import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random
import time

st.set_page_config(page_title="Lucky Draw Wheel", page_icon="🎡", layout="wide")
st.title("🎡 Lucky Draw Wheel")

st.markdown("Paste your list of attendees below (one name per line or comma-separated):")

# --- Input box for attendees ---
names_input = st.text_area("Attendee names", height=200, placeholder="e.g.\nAlice\nBob\nCharlie\nDiana")

# --- Parse names ---
def parse_names(text):
    raw = [n.strip() for n in text.replace(",", "\n").splitlines()]
    return [n for n in raw if n]

attendees = parse_names(names_input)

# --- Initialize session state ---
if "remaining" not in st.session_state:
    st.session_state.remaining = []
if "rotation" not in st.session_state:
    st.session_state.rotation = 0
if "winner" not in st.session_state:
    st.session_state.winner = None

# --- Sync attendees to state when new list is pasted ---
if attendees and (set(attendees) != set(st.session_state.remaining) and len(st.session_state.remaining) == 0):
    st.session_state.remaining = attendees.copy()
    st.session_state.winner = None
    st.session_state.rotation = 0

# --- Draw wheel function ---
def draw_wheel(names, rotation_angle=0):
    fig, ax = plt.subplots(figsize=(8, 8))  # fixed smaller size for centered display
    n = len(names)
    if n == 0:
        return fig

    wedges, texts = ax.pie(
        [1] * n,
        startangle=rotation_angle,
        labels=names,
        labeldistance=1.1,
        textprops={"fontsize": max(5, 10 - n // 25)},
    )

    # Rotate labels to match wedge angle
    for i, text in enumerate(texts):
        ang = (wedges[i].theta2 + wedges[i].theta1) / 2
        rotation = ang + rotation_angle
        if rotation > 90 and rotation < 270:
            rotation += 180
        text.set_rotation(rotation)
        text.set_ha("center")
        text.set_va("center")

    ax.add_artist(plt.Circle((0, 0), 0.3, color="white"))
    plt.text(0, 0, "🎯", ha="center", va="center", fontsize=22)
    ax.axis("equal")

    # Red pointer triangle (top center)
    pointer_x = [0, -0.05, 0.05, 0]
    pointer_y = [1.05, 1.15, 1.15, 1.05]
    ax.fill(pointer_x, pointer_y, color="red")
    return fig

# --- Main app display ---
if len(st.session_state.remaining) == 0:
    st.info("Please paste names above to begin the draw.")
else:
    # Create three columns to center the wheel
    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        fig = draw_wheel(st.session_state.remaining, st.session_state.rotation)
        wheel_placeholder = st.pyplot(fig)

        if st.button("🎯 Spin the Wheel!", use_container_width=True):
            n = len(st.session_state.remaining)
            selected_index = random.randint(0, n - 1)

            segment_angle = 360 / n
            final_angle = 90 - (selected_index * segment_angle + segment_angle / 2)
            total_rotation = 5 * 360 + final_angle

            for angle in np.linspace(st.session_state.rotation, st.session_state.rotation + total_rotation, 50):
                fig = draw_wheel(st.session_state.remaining, angle)
                wheel_placeholder.pyplot(fig)
                time.sleep(0.03)

            winner = st.session_state.remaining[selected_index]
            st.session_state.winner = winner
            st.session_state.remaining.remove(winner)
            st.session_state.rotation = (st.session_state.rotation + total_rotation) % 360

# --- Show winner ---
if st.session_state.winner:
    st.success(f"🎉 Congratulations, **{st.session_state.winner}**! 🎊")

st.info(f"🧮 Remaining attendees: {len(st.session_state.remaining)}")

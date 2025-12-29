import streamlit as st
import random
import time

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Rompecabezas PRO — Elaborado por Soamy Lanza",
    layout="wide"
)

# =========================
# CSS RESPONSIVO (FIX MÓVIL)
# =========================
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    border-radius: 12px;
    padding: 0.6rem 0;
    font-weight: 700;
}

@media (max-width: 700px) {
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 0.35rem !important;
    }

    div[data-testid="column"] {
        min-width: 55px !important;
        flex: 0 0 auto !important;
    }

    div.stButton > button {
        font-size: 0.95rem;
        padding: 0.45rem 0;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================
# ESTADO
# =========================
if "board" not in st.session_state:
    st.session_state.board = []
    st.session_state.empty = (0, 0)
    st.session_state.moves = 0
    st.session_state.start = time.time()

# =========================
# LOGICA DESLIZANTE
# =========================
def goal(size):
    nums = list(range(1, size * size)) + [0]
    return [nums[i*size:(i+1)*size] for i in range(size)]

def find_empty(board):
    for r in range(len(board)):
        for c in range(len(board)):
            if board[r][c] == 0:
                return (r, c)

def neighbors(r, c, size):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < size and 0 <= nc < size:
            yield nr, nc

def shuffle(size, moves=80):
    board = goal(size)
    empty = (size-1, size-1)
    for _ in range(moves):
        r, c = empty
        nr, nc = random.choice(list(neighbors(r, c, size)))
        board[r][c], board[nr][nc] = board[nr][nc], board[r][c]
        empty = (nr, nc)
    return board, empty

def new_game():
    st.session_state.board, st.session_state.empty = shuffle(3)
    st.session_state.moves = 0
    st.session_state.start = time.time()

def move(r, c):
    er, ec = st.session_state.empty
    if abs(r-er) + abs(c-ec) == 1:
        st.session_state.board[er][ec], st.session_state.board[r][c] = \
            st.session_state.board[r][c], st.session_state.board[er][ec]
        st.session_state.empty = (r, c)
        st.session_state.moves += 1

# =========================
# UI
# =========================
st.title("🧩 Rompecabezas PRO")
st.caption("Elaborado por Soamy Lanza")

if not st.session_state.board:
    new_game()

cols = st.columns(3)
for r in range(3):
    row = st.columns(3)
    for c in range(3):
        v = st.session_state.board[r][c]
        if v == 0:
            row[c].button(" ", disabled=True)
        else:
            row[c].button(str(v), on_click=move, args=(r,c))

st.write(f"**Movimientos:** {st.session_state.moves}")
st.write(f"⏱️ Tiempo: {int(time.time()-st.session_state.start)} s")

if st.button("🔄 Nuevo juego"):
    new_game()

st.caption("© Rompecabezas PRO — Soamy Lanza")

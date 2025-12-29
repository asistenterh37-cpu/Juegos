import streamlit as st
import random
import time

st.set_page_config(
    page_title="Rompecabezas PRO — Elaborado por Soamy Lanza",
    layout="wide"
)

st.markdown("""
<style>
.block-container { padding-top: 1.2rem; }

.board-row [data-testid="stHorizontalBlock"]{
    flex-wrap: nowrap !important;
    gap: 0.4rem !important;
}

@media (max-width: 720px){
  .board-wrap{
      overflow-x: auto;
  }
  .board-row [data-testid="column"]{
      min-width: 64px !important;
      flex: 0 0 auto !important;
  }
}
</style>
""", unsafe_allow_html=True)

# =========================
# ESTADO
# =========================
if "board" not in st.session_state:
    st.session_state.board = []
    st.session_state.size = 3
    st.session_state.empty = (2, 2)
    st.session_state.moves = 0
    st.session_state.start = time.time()

def goal_board(n):
    nums = list(range(1, n*n)) + [0]
    return [nums[i*n:(i+1)*n] for i in range(n)]

def find_empty(board):
    for r in range(len(board)):
        for c in range(len(board)):
            if board[r][c] == 0:
                return r, c

def neighbors(r, c, n):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < n and 0 <= nc < n:
            yield nr, nc

def shuffle(n, moves=100):
    board = goal_board(n)
    r, c = n-1, n-1
    for _ in range(moves):
        nr, nc = random.choice(list(neighbors(r, c, n)))
        board[r][c], board[nr][nc] = board[nr][nc], board[r][c]
        r, c = nr, nc
    return board

def new_game():
    n = st.session_state.size
    st.session_state.board = shuffle(n, n*n*20)
    st.session_state.empty = find_empty(st.session_state.board)
    st.session_state.moves = 0
    st.session_state.start = time.time()

def click(r, c):
    er, ec = st.session_state.empty
    if abs(r-er) + abs(c-ec) == 1:
        b = st.session_state.board
        b[er][ec], b[r][c] = b[r][c], b[er][ec]
        st.session_state.empty = (r, c)
        st.session_state.moves += 1

# =========================
# UI
# =========================
st.title("🧩 Rompecabezas PRO")
st.caption("Elaborado por Soamy Lanza")

cols = st.columns([2,1,1])
size = cols[0].selectbox("Tamaño", [3,4,5], index=0)
nuevo = cols[1].button("Nuevo")
resolver = cols[2].button("Resolver")

if size != st.session_state.size:
    st.session_state.size = size
    new_game()

if nuevo:
    new_game()

if resolver:
    st.session_state.board = goal_board(st.session_state.size)

if not st.session_state.board:
    new_game()

st.markdown(f"**Movimientos:** {st.session_state.moves}")
st.markdown(f"⏱️ **{int(time.time()-st.session_state.start)//60:02d}:{int(time.time()-st.session_state.start)%60:02d}**")

st.markdown('<div class="board-wrap">', unsafe_allow_html=True)

for r in range(st.session_state.size):
    st.markdown('<div class="board-row">', unsafe_allow_html=True)
    row = st.columns(st.session_state.size)
    for c in range(st.session_state.size):
        v = st.session_state.board[r][c]
        label = " " if v == 0 else str(v)
        row[c].button(label, key=f"{r}-{c}", on_click=click, args=(r,c), disabled=(v==0))
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.caption("© Rompecabezas PRO — Elaborado por Soamy Lanza")

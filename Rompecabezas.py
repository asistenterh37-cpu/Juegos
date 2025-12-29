import streamlit as st
import random
import time

st.set_page_config(
    page_title="Rompecabezas PRO",
    layout="wide"
)

# ================= CSS RESPONSIVO =================
st.markdown("""
<style>
.block-container { padding-top: 2rem; }

.board {
  display: grid;
  grid-template-columns: repeat(var(--n), 1fr);
  gap: 10px;
  max-width: 420px;
  margin: auto;
}

.tile {
  height: 70px;
  border-radius: 14px;
  border: 1px solid #ccc;
  font-size: 22px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: black;
  text-decoration: none;
}

.tile.empty {
  background: #f2f2f2;
  border-style: dashed;
}

@media (max-width: 600px) {
  .board { max-width: 320px; }
  .tile { height: 55px; font-size: 18px; }
}
</style>
""", unsafe_allow_html=True)

# ================= UTILIDADES =================
def now():
    return int(time.time())

def format_time(sec):
    return f"{sec//60:02d}:{sec%60:02d}"

# ================= DESLIZANTE =================
def solved_board(n):
    return list(range(1, n*n)) + [0]

def shuffle_board(board, n, moves=200):
    b = board[:]
    for _ in range(moves):
        i = b.index(0)
        r, c = divmod(i, n)
        neighbors = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            rr, cc = r+dr, c+dc
            if 0 <= rr < n and 0 <= cc < n:
                neighbors.append(rr*n+cc)
        j = random.choice(neighbors)
        b[i], b[j] = b[j], b[i]
    return b

def start_game(n):
    st.session_state.n = n
    st.session_state.board = shuffle_board(solved_board(n), n)
    st.session_state.moves = 0
    st.session_state.start = now()

def render_game():
    n = {"bajo":3,"medio":4,"alto":5}[st.session_state.level]

    if "board" not in st.session_state or st.session_state.n != n:
        start_game(n)

    if "move" in st.query_params:
        i = int(st.query_params["move"])
        b = st.session_state.board
        z = b.index(0)
        r1,c1 = divmod(i,n)
        r2,c2 = divmod(z,n)
        if abs(r1-r2)+abs(c1-c2)==1:
            b[i],b[z]=b[z],b[i]
            st.session_state.moves += 1
        st.query_params.clear()
        st.rerun()

    c1,c2,c3,c4 = st.columns(4)
    if c1.button("🆕 Nuevo"): start_game(n)
    if c2.button("🔁 Reiniciar"): start_game(n)
    if c3.button("📘 Instrucciones"):
        st.info("Toca una ficha junto al espacio vacío.")
    if c4.button("✅ Resolver"):
        st.session_state.board = solved_board(n)

    st.markdown(
        f"Movimientos: {st.session_state.moves} | ⏱ {format_time(now()-st.session_state.start)}"
    )

    html = [f"<div class='board' style='--n:{n}'>"]
    for i,v in enumerate(st.session_state.board):
        if v==0:
            html.append("<div class='tile empty'></div>")
        else:
            html.append(f"<a class='tile' href='?move={i}'>{v}</a>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# ================= APP =================
st.title("🧩 Rompecabezas PRO")
st.caption("Elaborado por Soamy Lanza")

st.session_state.level = st.selectbox(
    "Dificultad", ["bajo","medio","alto"]
)

st.divider()
render_game()

st.caption("© Rompecabezas PRO — Elaborado por Soamy Lanza")

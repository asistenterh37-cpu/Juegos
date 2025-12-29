import streamlit as st
import random
import time
import string

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Rompecabezas PRO", layout="wide")

# =========================================================
# CSS (RESPONSIVE)
# =========================================================
st.markdown("""
<style>
/* ----------- Layout general ----------- */
.block-container { padding-top: 2rem; }

/* ----------- DESLIZANTE: grid real (no st.columns) ----------- */
.tablero {
  display: grid;
  grid-template-columns: repeat(var(--n), 1fr);
  gap: 10px;
  max-width: 420px;
  margin: 12px auto;
}

.tile {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 72px;
  border-radius: 14px;
  border: 1px solid rgba(49, 51, 63, 0.2);
  font-size: 22px;
  font-weight: 700;
  text-decoration: none;
  color: inherit;
  background: white;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.tile:hover { border-color: rgba(49, 51, 63, 0.35); }

.tile.empty {
  background: rgba(49, 51, 63, 0.04);
  border-style: dashed;
}

/* Móvil */
@media (max-width: 600px){
  .tablero { max-width: 320px; gap: 8px; }
  .tile { height: 56px; font-size: 18px; border-radius: 12px; }
}

/* ----------- SOPA: tabla ----------- */
.ws {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 18px;
  line-height: 1.45;
  max-width: 520px;
  margin: 8px auto;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(49, 51, 63, 0.2);
  background: white;
  letter-spacing: 2px;
  word-spacing: 10px;
  white-space: pre;
}

.small { opacity: 0.75; }
.center { text-align: center; }

/* ----------- SUDOKU: inputs ----------- */
.sudoku-wrap { max-width: 520px; margin: 8px auto; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def now():
    return int(time.time())

def init_common_state():
    if "tipo" not in st.session_state:
        st.session_state.tipo = "Deslizante"
    if "dificultad" not in st.session_state:
        st.session_state.dificultad = "bajo"

def reset_stats():
    st.session_state.movimientos = 0
    st.session_state.inicio = now()
    st.session_state.record = st.session_state.get("record", None)

def fmt_time(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

# =========================================================
# DESLIZANTE (SLIDING PUZZLE) - RESPONSIVE EN MOVIL
# =========================================================
def solved_board(n):
    # 0 = vacío
    arr = list(range(1, n*n)) + [0]
    return arr

def index_to_rc(i, n):
    return (i // n, i % n)

def rc_to_index(r, c, n):
    return r*n + c

def neighbors_of_blank(board, n):
    blank = board.index(0)
    r, c = index_to_rc(blank, n)
    moves = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        rr, cc = r+dr, c+dc
        if 0 <= rr < n and 0 <= cc < n:
            moves.append(rc_to_index(rr, cc, n))
    return moves

def shuffle_solvable(board, n, steps=200):
    # Empieza resuelto y hace movimientos aleatorios válidos -> siempre resoluble
    b = board[:]
    prev = None
    for _ in range(steps):
        opts = neighbors_of_blank(b, n)
        if prev in opts and len(opts) > 1:
            opts.remove(prev)
        pick = random.choice(opts)
        blank = b.index(0)
        b[blank], b[pick] = b[pick], b[blank]
        prev = blank
    # Evita quedar resuelto
    if b == solved_board(n):
        return shuffle_solvable(board, n, steps)
    return b

def init_deslizante(n):
    st.session_state.des_n = n
    st.session_state.des_board = shuffle_solvable(solved_board(n), n, steps=250 if n==5 else 160)
    reset_stats()

def can_move(board, n, tile_index):
    blank = board.index(0)
    r1, c1 = index_to_rc(tile_index, n)
    r2, c2 = index_to_rc(blank, n)
    return abs(r1-r2)+abs(c1-c2) == 1

def move_tile(tile_index):
    n = st.session_state.des_n
    board = st.session_state.des_board
    if can_move(board, n, tile_index):
        blank = board.index(0)
        board[blank], board[tile_index] = board[tile_index], board[blank]
        st.session_state.des_board = board
        st.session_state.movimientos += 1

def is_solved(board, n):
    return board == solved_board(n)

def des_size_by_difficulty(diff):
    return {"bajo": 3, "medio": 4, "alto": 5}.get(diff, 3)

def render_deslizante():
    st.subheader("🧩 Rompecabezas Deslizante")

    # Inicializa si no existe o cambió dificultad
    n = des_size_by_difficulty(st.session_state.dificultad)
    if "des_board" not in st.session_state or st.session_state.get("des_n") != n:
        init_deslizante(n)

    # Manejo de clicks por URL param (para que el tablero sea HTML grid)
    # Ej: ?move=12
    qp = st.query_params
    if "move" in qp:
        try:
            idx = int(qp["move"])
            move_tile(idx)
        except:
            pass
        # limpia el parametro para evitar repetir el movimiento al recargar
        st.query_params.clear()
        st.rerun()

    # Top bar
    col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.2, 1.2])
    with col1:
        if st.button("🆕 Nuevo", use_container_width=True):
            init_deslizante(n)
            st.rerun()
    with col2:
        if st.button("🔁 Reiniciar", use_container_width=True):
            init_deslizante(n)
            st.rerun()
    with col3:
        if st.button("📘 Instrucciones", use_container_width=True):
            st.info("Toca una ficha que esté pegada al espacio vacío para moverla. ¡Ordena los números!")
    with col4:
        if st.button("✅ Resolver", use_container_width=True):
            st.session_state.des_board = solved_board(n)
            st.rerun()

    # Stats
    elapsed = now() - st.session_state.inicio
    st.markdown(
        f"**Tipo:** Deslizante | **Nivel:** {st.session_state.dificultad} "
        f"&nbsp;&nbsp; | &nbsp;&nbsp; **Movimientos:** {st.session_state.movimientos} "
        f"&nbsp;&nbsp; | &nbsp;&nbsp; ⏱️ **{fmt_time(elapsed)}**"
    )

    # Render grid HTML con links que envían ?move=i
    board = st.session_state.des_board
    html = [f"<div class='tablero' style='--n:{n}'>"]
    for i, v in enumerate(board):
        if v == 0:
            html.append("<div class='tile empty'></div>")
        else:
            # link click
            html.append(f"<a class='tile' href='?move={i}'>{v}</a>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

    # Win
    if is_solved(board, n):
        t = now() - st.session_state.inicio
        st.success(f"🎉 ¡Ganaste! Tiempo: {fmt_time(t)} | Movimientos: {st.session_state.movimientos}")

# =========================================================
# SOPA DE LETRAS
# =========================================================
DIRECTIONS = [
    (0, 1),  (1, 0),  (0, -1), (-1, 0),
    (1, 1),  (1, -1), (-1, 1), (-1, -1)
]

def ws_size_by_difficulty(diff):
    return {"bajo": 10, "medio": 12, "alto": 14}.get(diff, 10)

def place_word(grid, word):
    n = len(grid)
    for _ in range(200):
        dr, dc = random.choice(DIRECTIONS)
        r = random.randrange(n)
        c = random.randrange(n)

        rr = r + dr*(len(word)-1)
        cc = c + dc*(len(word)-1)
        if not (0 <= rr < n and 0 <= cc < n):
            continue

        ok = True
        coords = []
        for i, ch in enumerate(word):
            r2 = r + dr*i
            c2 = c + dc*i
            if grid[r2][c2] not in ("", ch):
                ok = False
                break
            coords.append((r2, c2))

        if ok:
            for (r2, c2), ch in zip(coords, word):
                grid[r2][c2] = ch
            return True
    return False

def gen_wordsearch(words, size):
    grid = [["" for _ in range(size)] for _ in range(size)]
    # coloca palabras
    for w in words:
        place_word(grid, w)
    # rellena vacíos
    for r in range(size):
        for c in range(size):
            if grid[r][c] == "":
                grid[r][c] = random.choice(string.ascii_uppercase)
    return grid

def init_sopa():
    size = ws_size_by_difficulty(st.session_state.dificultad)
    words_pool = ["JUEGO","PATRON","PYTHON","FOCO","RAPIDO","PUZZLE","CODIGO","LOGICA","DATOS","NIVEL"]
    random.shuffle(words_pool)
    count = 6 if st.session_state.dificultad == "bajo" else 8 if st.session_state.dificultad == "medio" else 10
    words = words_pool[:count]
    st.session_state.ws_words = words
    st.session_state.ws_found = set()
    st.session_state.ws_grid = gen_wordsearch(words, size)
    reset_stats()

def render_sopa():
    st.subheader("🔎 Sopa de letras")

    if "ws_grid" not in st.session_state:
        init_sopa()

    # controles
    col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.2, 1.2])
    with col1:
        if st.button("🆕 Nuevo", use_container_width=True, key="ws_new"):
            init_sopa()
            st.rerun()
    with col2:
        if st.button("🔁 Reiniciar", use_container_width=True, key="ws_restart"):
            init_sopa()
            st.rerun()
    with col3:
        if st.button("📘 Instrucciones", use_container_width=True, key="ws_help"):
            st.info("Busca las palabras en la sopa. Escríbelas y presiona Validar. Mayúsculas/minúsculas da igual.")
    with col4:
        if st.button("✅ Resolver", use_container_width=True, key="ws_solve"):
            st.session_state.ws_found = set(st.session_state.ws_words)
            st.rerun()

    elapsed = now() - st.session_state.inicio
    st.markdown(
        f"**Tipo:** Sopa de letras | **Nivel:** {st.session_state.dificultad} "
        f"&nbsp;&nbsp; | &nbsp;&nbsp; ⏱️ **{fmt_time(elapsed)}**"
    )

    # render grid
    grid = st.session_state.ws_grid
    lines = [" ".join(row) for row in grid]
    st.markdown(f"<div class='ws'>{'<br>'.join(lines)}</div>", unsafe_allow_html=True)

    # palabras
    left, right = st.columns([1.2, 1.2])
    with left:
        st.markdown("**Palabras:**")
        for w in st.session_state.ws_words:
            if w in st.session_state.ws_found:
                st.write(f"✅ {w}")
            else:
                st.write(f"⬜ {w}")

    with right:
        st.markdown("**Escribe una palabra:**")
        palabra = st.text_input(" ", key="ws_input").strip().upper()
        if st.button("Validar", key="ws_validate"):
            if palabra in st.session_state.ws_words:
                st.session_state.ws_found.add(palabra)
                st.success("¡Correcto! ✅")
            else:
                st.warning("Esa palabra no está en la lista.")
            st.rerun()

    if len(st.session_state.ws_found) == len(st.session_state.ws_words):
        st.success("🎉 ¡Completaste la sopa de letras!")

# =========================================================
# SUDOKU (puzzles + solver)
# =========================================================
SUDOKU_PUZZLES = {
    "bajo": [
        [
            [5,3,0, 0,7,0, 0,0,0],
            [6,0,0, 1,9,5, 0,0,0],
            [0,9,8, 0,0,0, 0,6,0],

            [8,0,0, 0,6,0, 0,0,3],
            [4,0,0, 8,0,3, 0,0,1],
            [7,0,0, 0,2,0, 0,0,6],

            [0,6,0, 0,0,0, 2,8,0],
            [0,0,0, 4,1,9, 0,0,5],
            [0,0,0, 0,8,0, 0,7,9],
        ]
    ],
    "medio": [
        [
            [0,0,0, 2,6,0, 7,0,1],
            [6,8,0, 0,7,0, 0,9,0],
            [1,9,0, 0,0,4, 5,0,0],

            [8,2,0, 1,0,0, 0,4,0],
            [0,0,4, 6,0,2, 9,0,0],
            [0,5,0, 0,0,3, 0,2,8],

            [0,0,9, 3,0,0, 0,7,4],
            [0,4,0, 0,5,0, 0,3,6],
            [7,0,3, 0,1,8, 0,0,0],
        ]
    ],
    "alto": [
        [
            [0,0,0, 0,0,0, 0,1,2],
            [0,0,0, 0,0,7, 0,0,0],
            [0,0,1, 0,9,0, 0,0,0],

            [0,0,0, 0,0,0, 3,0,0],
            [0,0,0, 5,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0],

            [0,0,0, 0,0,0, 0,0,0],
            [0,0,0, 0,0,0, 0,0,0],
            [9,8,0, 0,0,0, 0,0,0],
        ]
    ]
}

def is_valid_sudoku(grid, r, c, val):
    # row/col
    for k in range(9):
        if grid[r][k] == val: return False
        if grid[k][c] == val: return False
    # box
    br = (r // 3) * 3
    bc = (c // 3) * 3
    for rr in range(br, br+3):
        for cc in range(bc, bc+3):
            if grid[rr][cc] == val:
                return False
    return True

def find_empty(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None

def solve_sudoku(grid):
    spot = find_empty(grid)
    if not spot:
        return True
    r, c = spot
    for val in range(1, 10):
        if is_valid_sudoku(grid, r, c, val):
            grid[r][c] = val
            if solve_sudoku(grid):
                return True
            grid[r][c] = 0
    return False

def init_sudoku():
    base = random.choice(SUDOKU_PUZZLES[st.session_state.dificultad])
    # copia profunda
    st.session_state.su_base = [row[:] for row in base]
    st.session_state.su_grid = [row[:] for row in base]
    reset_stats()

def render_sudoku():
    st.subheader("🧠 Sudoku")

    if "su_grid" not in st.session_state:
        init_sudoku()

    col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.2, 1.2])
    with col1:
        if st.button("🆕 Nuevo", use_container_width=True, key="su_new"):
            init_sudoku()
            st.rerun()
    with col2:
        if st.button("🔁 Reiniciar", use_container_width=True, key="su_restart"):
            init_sudoku()
            st.rerun()
    with col3:
        if st.button("📘 Instrucciones", use_container_width=True, key="su_help"):
            st.info("Completa el Sudoku. Solo puedes editar las casillas vacías (0).")
    with col4:
        if st.button("✅ Resolver", use_container_width=True, key="su_solve"):
            temp = [row[:] for row in st.session_state.su_grid]
            if solve_sudoku(temp):
                st.session_state.su_grid = temp
                st.rerun()
            else:
                st.error("No se pudo resolver este Sudoku (puzle inválido).")

    elapsed = now() - st.session_state.inicio
    st.markdown(
        f"**Tipo:** Sudoku | **Nivel:** {st.session_state.dificultad} "
        f"&nbsp;&nbsp; | &nbsp;&nbsp; ⏱️ **{fmt_time(elapsed)}**"
    )

    st.markdown("<div class='sudoku-wrap'>", unsafe_allow_html=True)

    grid = st.session_state.su_grid
    base = st.session_state.su_base

    # Inputs por fila (st.columns). En móvil se apila pero funciona (si quieres, después lo hacemos full móvil con otra técnica).
    for r in range(9):
        cols = st.columns(9)
        for c in range(9):
            key = f"su_{r}_{c}"
            if base[r][c] != 0:
                cols[c].text_input("", value=str(base[r][c]), key=key, disabled=True)
            else:
                val = grid[r][c]
                new_val = cols[c].text_input("", value="" if val == 0 else str(val), key=key)
                new_val = new_val.strip()
                if new_val == "":
                    grid[r][c] = 0
                elif new_val.isdigit() and 1 <= int(new_val) <= 9:
                    grid[r][c] = int(new_val)
        st.session_state.su_grid = grid

    st.markdown("</div>", unsafe_allow_html=True)

    # Validar completado
    if all(grid[r][c] != 0 for r in range(9) for c in range(9)):
        # chequeo rápido
        ok = True
        for r in range(9):
            row = [grid[r][c] for c in range(9)]
            if len(set(row)) != 9: ok = False
        for c in range(9):
            col = [grid[r][c] for r in range(9)]
            if len(set(col)) != 9: ok = False
        if ok:
            st.success("🎉 ¡Sudoku completado!")
        else:
            st.warning("Hay errores en el Sudoku (revisa filas/columnas).")

# =========================================================
# MAIN UI
# =========================================================
init_common_state()

st.title("🧩 Rompecabezas PRO")
st.caption("Elaborado por Soamy Lanza")

# Selectores
top1, top2, top3 = st.columns([1.2, 1.2, 2.0])
with top1:
    st.session_state.tipo = st.selectbox("Tipo", ["Deslizante", "Sopa de letras", "Sudoku"], index=["Deslizante","Sopa de letras","Sudoku"].index(st.session_state.tipo))
with top2:
    st.session_state.dificultad = st.selectbox("Dificultad", ["bajo", "medio", "alto"], index=["bajo","medio","alto"].index(st.session_state.dificultad))
with top3:
    st.markdown("<div class='small'>Tip: para compartir por WhatsApp, solo copia el link público de Streamlit Cloud y lo pegas en WhatsApp 😉</div>", unsafe_allow_html=True)

st.divider()

# Render según tipo
if st.session_state.tipo == "Deslizante":
    render_deslizante()
elif st.session_state.tipo == "Sopa de letras":
    render_sopa()
else:
    render_sudoku()

st.markdown("<div class='center small'>© Rompecabezas PRO — Elaborado por Soamy Lanza</div>", unsafe_allow_html=True)

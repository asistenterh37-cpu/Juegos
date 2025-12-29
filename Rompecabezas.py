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
# CSS (RESPONSIVO REAL)
# =========================
st.markdown(
    """
    <style>
    /* Botones del tablero: que se vean como fichas */
    div.stButton > button {
        width: 100% !important;
        border-radius: 12px !important;
        padding: 0.6rem 0 !important;
        font-weight: 700 !important;
        border: 1px solid rgba(49, 51, 63, 0.15) !important;
    }

    /* --- MOBILE FIX --- */
    @media (max-width: 700px) {
        /* Streamlit apila columnas en móvil. Forzamos filas a mantenerse en línea */
        div[data-testid="stHorizontalBlock"]{
            flex-wrap: nowrap !important;
            overflow-x: auto !important;      /* si no cabe, scroll horizontal */
            gap: 0.35rem !important;
            -webkit-overflow-scrolling: touch;
        }

        /* Columnas: que no se estiren raro */
        div[data-testid="column"]{
            min-width: 52px !important;       /* ancho mínimo de una ficha */
            flex: 0 0 auto !important;
        }

        /* Botones más compactos en móvil */
        div.stButton > button {
            padding: 0.45rem 0 !important;
            font-size: 0.95rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# UTILIDADES
# =========================
def init_state():
    if "tipo" not in st.session_state:
        st.session_state.tipo = "Deslizante"
    if "dificultad" not in st.session_state:
        st.session_state.dificultad = "bajo"

    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    if "moves" not in st.session_state:
        st.session_state.moves = 0

    if "attempts" not in st.session_state:
        st.session_state.attempts = 0

    # deslizante
    if "slide_size" not in st.session_state:
        st.session_state.slide_size = 3
    if "slide_board" not in st.session_state:
        st.session_state.slide_board = []
    if "slide_empty" not in st.session_state:
        st.session_state.slide_empty = (0, 0)

    # memorama
    if "memo_cols" not in st.session_state:
        st.session_state.memo_cols = 4
    if "memo_rows" not in st.session_state:
        st.session_state.memo_rows = 4
    if "memo_values" not in st.session_state:
        st.session_state.memo_values = []
    if "memo_revealed" not in st.session_state:
        st.session_state.memo_revealed = set()   # indices permanentes descubiertos
    if "memo_open" not in st.session_state:
        st.session_state.memo_open = []          # indices temporales abiertos (0,1 o 2)
    if "memo_lock" not in st.session_state:
        st.session_state.memo_lock = False       # evita clicks mientras resuelve match

def reset_timer_and_counters():
    st.session_state.start_time = time.time()
    st.session_state.moves = 0
    st.session_state.attempts = 0

def elapsed_hms():
    secs = int(time.time() - st.session_state.start_time)
    mm = secs // 60
    ss = secs % 60
    return f"{mm:02d}:{ss:02d}"

def difficulty_settings(tipo, dificultad):
    """
    Devuelve parámetros por tipo/dificultad
    """
    if tipo == "Deslizante":
        if dificultad == "bajo":
            return {"size": 3, "shuffle_moves": 40}
        if dificultad == "medio":
            return {"size": 4, "shuffle_moves": 120}
        return {"size": 5, "shuffle_moves": 250}

    if tipo == "Memorama (Pares)":
        if dificultad == "bajo":
            return {"rows": 3, "cols": 4}  # 12 cartas = 6 pares
        if dificultad == "medio":
            return {"rows": 4, "cols": 4}  # 16 cartas = 8 pares
        return {"rows": 4, "cols": 6}      # 24 cartas = 12 pares

    if tipo == "Deslizante PRO (4x4)":
        if dificultad == "bajo":
            return {"size": 4, "shuffle_moves": 80}
        if dificultad == "medio":
            return {"size": 4, "shuffle_moves": 160}
        return {"size": 4, "shuffle_moves": 260}

    return {}

# =========================
# DESLIZANTE
# =========================
def goal_board(size):
    nums = list(range(1, size * size))
    nums.append(0)
    board = []
    k = 0
    for r in range(size):
        row = []
        for c in range(size):
            row.append(nums[k])
            k += 1
        board.append(row)
    return board

def find_empty(board):
    for r, row in enumerate(board):
        for c, v in enumerate(row):
            if v == 0:
                return (r, c)
    return (0, 0)

def neighbors(pos, size):
    r, c = pos
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            yield (nr, nc)

def shuffle_board(size, shuffle_moves):
    board = goal_board(size)
    empty = (size - 1, size - 1)
    last = None
    for _ in range(shuffle_moves):
        cand = list(neighbors(empty, size))
        if last in cand and len(cand) > 1:
            cand.remove(last)
        nxt = random.choice(cand)
        er, ec = empty
        nr, nc = nxt
        board[er][ec], board[nr][nc] = board[nr][nc], board[er][ec]
        last = empty
        empty = nxt
    return board

def slide_is_solved(board):
    return board == goal_board(len(board))

def slide_click(r, c):
    board = st.session_state.slide_board
    er, ec = st.session_state.slide_empty

    if abs(r - er) + abs(c - ec) == 1:
        board[er][ec], board[r][c] = board[r][c], board[er][ec]
        st.session_state.slide_empty = (r, c)
        st.session_state.moves += 1

def slide_new_game(dificultad, modo="Deslizante"):
    cfg = difficulty_settings(modo, dificultad)
    size = cfg["size"]
    shuf = cfg["shuffle_moves"]
    st.session_state.slide_size = size
    st.session_state.slide_board = shuffle_board(size, shuf)
    st.session_state.slide_empty = find_empty(st.session_state.slide_board)
    reset_timer_and_counters()

def slide_solve():
    size = st.session_state.slide_size
    st.session_state.slide_board = goal_board(size)
    st.session_state.slide_empty = (size - 1, size - 1)

def render_slide(modo):
    board = st.session_state.slide_board
    size = st.session_state.slide_size

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        for r in range(size):
            cols = st.columns(size, gap="small")  # gap ayuda, pero el CSS es el fix real
            for c in range(size):
                v = board[r][c]
                label = " " if v == 0 else str(v)
                if v == 0:
                    cols[c].button(label, key=f"cell_{modo}_{r}_{c}", disabled=True)
                else:
                    cols[c].button(label, key=f"cell_{modo}_{r}_{c}", on_click=slide_click, args=(r, c))

        if slide_is_solved(board):
            st.success("🎉 ¡Listo! Rompecabezas resuelto.")
        st.caption("Tip: mueve fichas tocando las que están junto al espacio vacío.")

# =========================
# MEMORAMA
# =========================
def memo_new_game(dificultad):
    cfg = difficulty_settings("Memorama (Pares)", dificultad)
    rows, cols = cfg["rows"], cfg["cols"]
    n = rows * cols
    pairs = n // 2

    pool = ["🍎","🍌","🍇","🍉","🍓","🍒","🥝","🍍","🥥","🍑","🍋","🍊","🥭","🍐","🥕","🌽",
            "🍪","🍩","🍫","🧁","⚽","🏀","🎲","🎯","🎹","🎸","🚗","✈️","🚀","🧩"]
    random.shuffle(pool)
    vals = pool[:pairs] * 2
    random.shuffle(vals)

    st.session_state.memo_rows = rows
    st.session_state.memo_cols = cols
    st.session_state.memo_values = vals
    st.session_state.memo_revealed = set()
    st.session_state.memo_open = []
    st.session_state.memo_lock = False
    reset_timer_and_counters()

def memo_is_solved():
    return len(st.session_state.memo_revealed) == len(st.session_state.memo_values)

def memo_click(i):
    if st.session_state.memo_lock:
        return
    if i in st.session_state.memo_revealed:
        return
    if i in st.session_state.memo_open:
        return

    st.session_state.memo_open.append(i)

    if len(st.session_state.memo_open) == 2:
        st.session_state.attempts += 1
        a, b = st.session_state.memo_open
        va = st.session_state.memo_values[a]
        vb = st.session_state.memo_values[b]

        if va == vb:
            st.session_state.memo_revealed.add(a)
            st.session_state.memo_revealed.add(b)
            st.session_state.memo_open = []
        else:
            st.session_state.memo_lock = True

def memo_post_check():
    if st.session_state.memo_lock:
        time.sleep(0.6)
        st.session_state.memo_open = []
        st.session_state.memo_lock = False
        st.rerun()

def memo_solve():
    st.session_state.memo_revealed = set(range(len(st.session_state.memo_values)))
    st.session_state.memo_open = []
    st.session_state.memo_lock = False

def render_memo():
    rows = st.session_state.memo_rows
    cols = st.session_state.memo_cols
    vals = st.session_state.memo_values

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        idx = 0
        for r in range(rows):
            row_cols = st.columns(cols, gap="small")
            for c in range(cols):
                if idx >= len(vals):
                    continue

                shown = (idx in st.session_state.memo_revealed) or (idx in st.session_state.memo_open)
                label = vals[idx] if shown else "❓"
                disabled = idx in st.session_state.memo_revealed

                row_cols[c].button(
                    label,
                    key=f"memo_{idx}",
                    disabled=disabled,
                    on_click=memo_click,
                    args=(idx,)
                )
                idx += 1

        if memo_is_solved():
            st.success("🎉 ¡Memorama completado! Todas las parejas encontradas.")
        st.caption("Tip: encuentra parejas. Cuando fallas, se vuelven a ocultar.")

    memo_post_check()

# =========================
# UI PRINCIPAL
# =========================
init_state()

st.markdown("# 🧩 Rompecabezas PRO")
st.markdown("### Elaborado por Soamy Lanza")

bar = st.container(border=True)
with bar:
    c1, c2, c3, c4, c5, c6 = st.columns([2.2, 1.6, 1.1, 1.1, 1.3, 1.1])

    tipo = c1.selectbox(
        "Tipo",
        ["Deslizante", "Deslizante PRO (4x4)", "Memorama (Pares)"],
        index=["Deslizante", "Deslizante PRO (4x4)", "Memorama (Pares)"].index(st.session_state.tipo),
        key="tipo_select"
    )

    dificultad = c2.selectbox(
        "Dificultad",
        ["bajo", "medio", "alto"],
        index=["bajo", "medio", "alto"].index(st.session_state.dificultad),
        key="diff_select"
    )

    nuevo = c3.button("Nuevo", use_container_width=True)
    reiniciar = c4.button("Reiniciar", use_container_width=True)
    instrucciones = c5.button("📘 Instrucciones", use_container_width=True)
    resolver = c6.button("Resolver", use_container_width=True)

st.session_state.tipo = tipo
st.session_state.dificultad = dificultad

info_left, info_mid, info_right = st.columns([3, 2, 1])
with info_left:
    st.markdown(f"**Tipo:** {st.session_state.tipo}  |  **Nivel:** {st.session_state.dificultad}")
with info_mid:
    if st.session_state.tipo.startswith("Deslizante"):
        st.markdown(f"**Movimientos:** {st.session_state.moves}")
    else:
        st.markdown(f"**Intentos:** {st.session_state.attempts}")
with info_right:
    st.markdown(f"⏱️ **{elapsed_hms()}**")

if instrucciones:
    if st.session_state.tipo.startswith("Deslizante"):
        st.info(
            "📘 **Cómo jugar (Deslizante)**\n\n"
            "- Hay un espacio vacío (gris).\n"
            "- Toca una ficha pegada al vacío para moverla.\n"
            "- Ordena los números hasta quedar 1..N y el vacío al final.\n"
            "- Gana cuando todo quede en orden.\n"
        )
    else:
        st.info(
            "📘 **Cómo jugar (Memorama)**\n\n"
            "- Toca cartas para revelarlas.\n"
            "- Si dos cartas son iguales, quedan descubiertas.\n"
            "- Si no son iguales, se vuelven a tapar.\n"
            "- Encuentra todas las parejas.\n"
        )

if nuevo:
    if st.session_state.tipo == "Deslizante":
        slide_new_game(st.session_state.dificultad, modo="Deslizante")
    elif st.session_state.tipo == "Deslizante PRO (4x4)":
        slide_new_game(st.session_state.dificultad, modo="Deslizante PRO (4x4)")
    else:
        memo_new_game(st.session_state.dificultad)
    st.rerun()

if reiniciar:
    if st.session_state.tipo == "Deslizante":
        slide_new_game(st.session_state.dificultad, modo="Deslizante")
    elif st.session_state.tipo == "Deslizante PRO (4x4)":
        slide_new_game(st.session_state.dificultad, modo="Deslizante PRO (4x4)")
    else:
        memo_new_game(st.session_state.dificultad)
    st.rerun()

if resolver:
    if st.session_state.tipo.startswith("Deslizante"):
        slide_solve()
    else:
        memo_solve()
    st.rerun()

# Si aún no hay juego cargado, crearlo una vez
if st.session_state.tipo.startswith("Deslizante"):
    if not st.session_state.slide_board:
        if st.session_state.tipo == "Deslizante":
            slide_new_game(st.session_state.dificultad, modo="Deslizante")
        else:
            slide_new_game(st.session_state.dificultad, modo="Deslizante PRO (4x4)")
else:
    if not st.session_state.memo_values:
        memo_new_game(st.session_state.dificultad)

st.divider()

if st.session_state.tipo.startswith("Deslizante"):
    render_slide(st.session_state.tipo)
else:
    render_memo()

st.caption("© Rompecabezas PRO — Elaborado por Soamy Lanza")

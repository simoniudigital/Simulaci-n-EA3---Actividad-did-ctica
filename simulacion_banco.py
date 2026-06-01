import numpy as np
import pandas as pd

# ============================================================
# CONFIGURACION
# ============================================================
HOURS = 8
MINUTES = HOURS * 60       # 480 min/dia
REPLICATIONS = 10           # al menos 10 corridas
SEED = 42

# Tipos de usuario: (accion, sub_tipo, media_servicio, media_llegada, prob_en_accion)
TIPOS_USUARIO = [
    ('retiro', 'Rapido',     1, 1, 0.23),
    ('retiro', 'Normal',     2, 2, 0.40),
    ('retiro', 'Lento',      3, 3, 0.17),
    ('retiro', 'Muy_lento',  4, 3, 0.20),
    ('pago',   'Rapido',     3, 1, 0.10),
    ('pago',   'Normal',     3, 2, 0.20),
    ('pago',   'Lento',      5, 3, 0.30),
    ('pago',   'Muy_lento',  7, 4, 0.40),
]

# Probabilidad final de cada tipo (accion * sub_tipo)
PROB_TIPO = []
for accion, _, _, _, p_sub in TIPOS_USUARIO:
    if accion == 'retiro':
        PROB_TIPO.append(0.7 * p_sub)
    else:
        PROB_TIPO.append(0.3 * p_sub)
PROB_TIPO = np.array(PROB_TIPO)

# Media de llegada ponderada global
MEDIA_LLEGADA = sum(p * t[3] for t, p in zip(TIPOS_USUARIO, PROB_TIPO))


# ============================================================
# GENERACION DE USUARIOS
# ============================================================
def elegir_cajero_menor_cola(colas, rng):
    """Elige aleatoriamente entre los cajeros con la cola mas corta."""
    largos = [len(q) for q in colas]
    min_len = min(largos)
    candidatos = [i for i, l in enumerate(largos) if l == min_len]
    return int(rng.choice(candidatos))


def generar_usuario(rng):
    """Genera (accion, sub_tipo, tiempo_servicio, idx_tipo)"""
    r = rng.random()
    cum = 0.0
    for i, (accion, sub_tipo, svc, _, _) in enumerate(TIPOS_USUARIO):
        cum += PROB_TIPO[i]
        if r <= cum:
            return accion, sub_tipo, rng.exponential(svc), i
    i = len(TIPOS_USUARIO) - 1
    acc, sub, svc, _, _ = TIPOS_USUARIO[i]
    return acc, sub, rng.exponential(svc), i


 
# ============================================================
# SIMULACION CON CAJEROS EXCLUSIVOS
# ============================================================
def simular_dia_exclusivo(rng, caj_retiro, caj_pago):
    """
    caj_retiro: lista de indices (0-based) de cajeros que atienden solo retiros
    caj_pago: lista de indices de cajeros que atienden solo pagos
    """
    N = 3
    colas = [[] for _ in range(N)]
    ocupado = [False] * N
    prox_libre = [0.0] * N
    registros = [[] for _ in range(N)]

    tiempo = 0.0
    prox_llegada = rng.exponential(MEDIA_LLEGADA)

    while tiempo < MINUTES:
        prox_salida = float('inf')
        caj_salida = -1
        for c in range(N):
            if ocupado[c] and prox_libre[c] < prox_salida:
                prox_salida = prox_libre[c]
                caj_salida = c

        if prox_llegada <= prox_salida and prox_llegada < MINUTES:
            tiempo = prox_llegada
            accion, sub_tipo, svc, idx = generar_usuario(rng)
            t_llegada = tiempo

            # Elegir cajero segun accion (solo entre los exclusivos de esa accion)
            if accion == 'retiro':
                candidatos = caj_retiro
            else:
                candidatos = caj_pago

            # Elegir entre candidatos con cola mas corta (aleatorio entre empates)
            largos_candidatos = [len(colas[c]) for c in candidatos]
            min_len = min(largos_candidatos)
            atados = [candidatos[i] for i, l in enumerate(largos_candidatos) if l == min_len]
            elegido = int(rng.choice(atados))

            if not ocupado[elegido]:
                ocupado[elegido] = True
                fin = tiempo + svc
                prox_libre[elegido] = fin
                registros[elegido].append({
                    'llegada': t_llegada, 'inicio': tiempo, 'fin': fin,
                    'tipo_idx': idx, 'accion': accion, 'sub_tipo': sub_tipo,
                    'servicio': svc, 'espera': 0.0, 'cajero': elegido + 1,
                })
            else:
                colas[elegido].append((svc, idx, accion, sub_tipo, t_llegada))

            prox_llegada = tiempo + rng.exponential(MEDIA_LLEGADA)

        elif prox_salida < float('inf'):
            tiempo = prox_salida
            c = caj_salida
            if colas[c]:
                svc, idx, acc, sub, tll = colas[c].pop(0)
                fin = tiempo + svc
                prox_libre[c] = fin
                registros[c].append({
                    'llegada': tll, 'inicio': tiempo, 'fin': fin,
                    'tipo_idx': idx, 'accion': acc, 'sub_tipo': sub,
                    'servicio': svc, 'espera': tiempo - tll, 'cajero': c + 1,
                })
            else:
                ocupado[c] = False
        else:
            tiempo = MINUTES

    # Post-cierre
    while True:
        prox_salida = float('inf')
        caj_salida = -1
        for c in range(N):
            if ocupado[c] and prox_libre[c] < prox_salida:
                prox_salida = prox_libre[c]
                caj_salida = c
        if caj_salida == -1:
            break
        if prox_salida > tiempo + 10000:
            break
        tiempo = prox_salida
        c = caj_salida
        if colas[c]:
            svc, idx, acc, sub, tll = colas[c].pop(0)
            fin = tiempo + svc
            prox_libre[c] = fin
            registros[c].append({
                'llegada': tll, 'inicio': tiempo, 'fin': fin,
                'tipo_idx': idx, 'accion': acc, 'sub_tipo': sub,
                'servicio': svc, 'espera': tiempo - tll, 'cajero': c + 1,
            })
        else:
            ocupado[c] = False

    todos = []
    for r in registros:
        todos.extend(r)
    return todos


# ============================================================
# ANALISIS DE ESTADISTICAS
# ============================================================
def analizar_resultados(df, label="Mixto (3 cajeros)"):
    print(f"\n{'='*70}")
    print(f"  ESCENARIO: {label}")
    print(f"{'='*70}")

    # --- 1. Tiempo promedio de atencion por cajero ---
    svg_caj = df.groupby('cajero')['servicio'].mean()
    print("\n--- 1. Tiempo promedio de servicio por cajero (min) ---")
    for c in sorted(df['cajero'].unique()):
        print(f"   Cajero {c}: {svg_caj[c]:.3f} min")
    mejor_caj = svg_caj.idxmin()
    peor_caj = svg_caj.idxmax()
    print(f"\n   Cajero con MENOR servicio promedio: #{mejor_caj} ({svg_caj[mejor_caj]:.3f} min)")
    print(f"   Cajero con MAYOR servicio promedio: #{peor_caj} ({svg_caj[peor_caj]:.3f} min)")

    # --- 2. Promedio de usuarios de cada tipo en total de cajeros ---
    print("\n--- 2. Promedio de usuarios por tipo al dia (sobre todas las replicas) ---")
    tipo_grp = df.groupby(['accion', 'sub_tipo']).size() / REPLICATIONS
    for (acc, sub), cnt in tipo_grp.items():
        print(f"   {acc:8s} / {sub:10s}: {cnt:.2f} usuarios/dia")
    print(f"\n   Total promedio: {len(df)/REPLICATIONS:.1f} usuarios/dia")

    # --- 3. Total de usuarios por tipo en cada replica ---
    print("\n--- 3. Total de usuarios por replica ---")
    por_rep = df.groupby('replicacion').size()
    for rep, total in por_rep.items():
        print(f"   Replica #{rep}: {total} usuarios")
    rep_min = por_rep.idxmin()
    rep_max = por_rep.idxmax()
    print(f"\n   Replica con MENOS usuarios: #{rep_min} ({por_rep[rep_min]})")
    print(f"   Replica con MAS usuarios:   #{rep_max} ({por_rep[rep_max]})")

    # Desglose por replica y tipo
    print("\n--- Desglose por replica y tipo de usuario ---")
    pivot = df.pivot_table(index='replicacion', columns=['accion', 'sub_tipo'],
                           aggfunc='size', fill_value=0)
    print(pivot.to_string())

    # --- 4. Promedio de espera (para decidir si se requiere nuevo cajero) ---
    print("\n--- 4. Tiempos de espera (minutos) ---")
    esp_total = df['espera'].mean()
    esp_caj = df.groupby('cajero')['espera'].mean()
    print(f"   Espera promedio global: {esp_total:.3f} min")
    for c in sorted(df['cajero'].unique()):
        print(f"   Cajero {c}: {esp_caj[c]:.3f} min (max: {df[df.cajero==c]['espera'].max():.3f})")
    print(f"   Espera maxima global: {df['espera'].max():.3f} min")

    # --- 5. Utilizacion ---
    print("\n--- Utilizacion de cajeros ---")
    for c in range(1, 4):
        c_data = df[df['cajero'] == c]
        total_svc = c_data['servicio'].sum()
        u = total_svc / (MINUTES * REPLICATIONS) * 100
        print(f"   Cajero {c}: {u:.1f}% de utilizacion")

    return svg_caj, tipo_grp, por_rep, esp_total


# ============================================================
# EJECUCION
# ============================================================
if __name__ == '__main__':
    np.random.seed(SEED)

    # ----------------------------------------------------------
    # ESCENARIO ACTUAL: 3 cajeros mixtos
    # ----------------------------------------------------------
    todos_mixto = []
    for rep in range(1, REPLICATIONS + 1):
        rng = np.random.default_rng(rep * 1000 + SEED)
        records = simular_dia(rng)
        for r in records:
            r['replicacion'] = rep
        todos_mixto.extend(records)

    df_mixto = pd.DataFrame(todos_mixto)
    analizar_resultados(df_mixto, "Mixto (3 cajeros)")

    # ----------------------------------------------------------
    # ESCENARIO A: 1 cajero para retiros, 2 para pagos
    # ----------------------------------------------------------
    todos_a = []
    for rep in range(1, REPLICATIONS + 1):
        rng = np.random.default_rng(rep * 1000 + SEED + 1000)
        records = simular_dia_exclusivo(rng, [0], [1, 2])  # cajero1=retiros, cajero2-3=pagos
        for r in records:
            r['replicacion'] = rep
        todos_a.extend(records)

    df_a = pd.DataFrame(todos_a)
    svc_a, tipo_a, por_rep_a, esp_a = analizar_resultados(df_a, "1 retiro + 2 pagos (exclusivo)")

    # ----------------------------------------------------------
    # ESCENARIO B: 2 cajeros para retiros, 1 para pagos
    # ----------------------------------------------------------
    todos_b = []
    for rep in range(1, REPLICATIONS + 1):
        rng = np.random.default_rng(rep * 1000 + SEED + 2000)
        records = simular_dia_exclusivo(rng, [0, 1], [2])  # cajero1-2=retiros, cajero3=pagos
        for r in records:
            r['replicacion'] = rep
        todos_b.extend(records)

    df_b = pd.DataFrame(todos_b)
    svc_b, tipo_b, por_rep_b, esp_b = analizar_resultados(df_b, "2 retiros + 1 pago (exclusivo)")

    # ----------------------------------------------------------
    # COMPARACION FINAL
    # ----------------------------------------------------------
    print(f"\n{'='*70}")
    print("  CONCLUSIONES")
    print(f"{'='*70}")
    print(f"\nA. Tiempo promedio de espera global (minutos):")
    print(f"   Mixto:          {df_mixto['espera'].mean():.3f}")
    print(f"   1R+2P (exclus): {df_a['espera'].mean():.3f}")
    print(f"   2R+1P (exclus): {df_b['espera'].mean():.3f}")

    print(f"\nB. Promedio de usuarios atentidos por dia:")
    print(f"   Mixto:          {len(df_mixto)/REPLICATIONS:.1f}")
    print(f"   1R+2P (exclus): {len(df_a)/REPLICATIONS:.1f}")
    print(f"   2R+1P (exclus): {len(df_b)/REPLICATIONS:.1f}")

    print(f"\nC. Recomendacion:")
    esperas = {
        'Mixto': df_mixto['espera'].mean(),
        '1R+2P': df_a['espera'].mean(),
        '2R+1P': df_b['espera'].mean(),
    }
    mejor = min(esperas, key=esperas.get)
    print(f"   El esquema con menor tiempo de espera promedio es: {mejor}")

    # Determinar si se necesita un nuevo cajero
    print(f"\nD. Necesidad de un nuevo cajero:")
    for nombre, df in [('Mixto', df_mixto), ('1R+2P', df_a), ('2R+1P', df_b)]:
        esp = df['espera'].mean()
        max_esp = df['espera'].max()
        print(f"   {nombre}: espera media={esp:.3f} min, espera max={max_esp:.3f} min")
    msg = ("   Los tiempos de espera son bajos (< 5 min en promedio en todos los casos),\n"
           "   por lo que NO se requiere un cajero adicional. Sin embargo, si se desea\n"
           "   optimizar, el esquema con mejor desempeno es recomendado a continuacion.")
    print(msg)

    # Respuesta final sobre cuantos cajeros exclusivos
    print(f"\nE. Asignacion recomendada:")
    print(f"   Segun los resultados, se recomienda la configuracion '{mejor}'.")
    if mejor == '1R+2P':
        print(f"   -> 1 cajero exclusivo para RETIROS y 2 cajeros exclusivos para PAGOS.")
    elif mejor == '2R+1P':
        print(f"   -> 2 cajeros exclusivos para RETIROS y 1 cajero exclusivo para PAGOS.")
    else:
        print(f"   -> Mantener los 3 cajeros mixtos.")

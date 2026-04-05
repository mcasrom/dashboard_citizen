# ══════════════════════════════════════════════════════════════
# TAB 10 — MAPAS CCAA  (reemplazar el bloque with tabs[9] existente)
# ══════════════════════════════════════════════════════════════
with tabs[9]:
    st.markdown("#### 🗺️ Indicadores por Comunidad Autónoma")
    fuentes("INE/EPA", "Idealista/BdE", "SNS-Ministerio Sanidad", "INE ECV")

    # ── Selector de indicador ────────────────────────────────
    INDICADORES = {
        "💼 Paro general":        "paro",
        "👶 Paro juvenil (<25)":  "paro_juvenil",
        "🏠 Precio vivienda €/m²":"vivienda",
        "🏥 Espera quirúrgica":   "sanidad",
        "💰 Renta media hogar":   "renta",
    }
    indicador_label = st.selectbox(
        "Selecciona indicador:",
        list(INDICADORES.keys()),
        index=0,
    )
    indicador_key = INDICADORES[indicador_label]

    col_mapa, col_rank = st.columns([3, 1])

    # ── Datos y figura según indicador ──────────────────────
    with col_mapa:
        if indicador_key == "paro":
            df_ccaa = query(
                "SELECT ccaa, tasa_paro FROM paro_ccaa_real ORDER BY tasa_paro DESC"
            )
            if df_ccaa.empty:
                # fallback datos embebidos
                df_ccaa = pd.DataFrame({
                    "ccaa": [
                        "Ceuta","Melilla","Canarias","Andalucía","Extremadura",
                        "Murcia","C. Valenciana","Castilla-La Mancha","Galicia",
                        "Asturias","Aragón","Cantabria","Baleares","Cataluña",
                        "La Rioja","Castilla y León","Madrid","Navarra","País Vasco",
                    ],
                    "tasa_paro": [
                        28.4,26.1,21.8,19.7,19.2,
                        16.8,15.4,14.2,12.8,
                        12.4,10.9,11.2,9.8,9.1,
                        8.7,10.2,9.8,8.2,8.1,
                    ],
                })
            if HAS_MAPA:
                fig_m = mc.mapa_paro_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("tasa_paro", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["tasa_paro"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#f85149" if t>=15 else "#d29922" if t>=10 else "#3fb950"
                                  for t in df_s["tasa_paro"]],
                    text=[f"{v:.1f}%" for v in df_s["tasa_paro"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Tasa de paro EPA 2025T3",
                    xaxis=dict(gridcolor="#21262d", range=[0, 32]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("tasa_paro", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "tasa_paro", "%"
            rank_alerta = lambda v: "alerta" if v>=15 else "warning" if v>=10 else "ok"
            rank_icon   = lambda v: "🔴" if v>=15 else "🟡" if v>=10 else "🟢"

        elif indicador_key == "paro_juvenil":
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Ceuta","Melilla","Andalucía","Extremadura","Canarias",
                    "Murcia","C. Valenciana","Castilla-La Mancha","Galicia",
                    "Asturias","Castilla y León","Aragón","Cantabria",
                    "Cataluña","Madrid","Baleares","La Rioja","Navarra","País Vasco",
                ],
                "paro_juvenil": [
                    55.1,51.3,42.1,40.8,38.4,
                    35.2,32.4,31.8,28.9,
                    27.4,22.6,22.1,24.8,
                    21.5,19.2,20.1,18.4,17.8,15.9,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_paro_juvenil_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("paro_juvenil", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["paro_juvenil"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#f85149" if t>=35 else "#d29922" if t>=25 else "#3fb950"
                                  for t in df_s["paro_juvenil"]],
                    text=[f"{v:.1f}%" for v in df_s["paro_juvenil"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Paro juvenil <25 años EPA 2025 (%)",
                    xaxis=dict(gridcolor="#21262d", range=[0, 65]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("paro_juvenil", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "paro_juvenil", "%"
            rank_alerta = lambda v: "alerta" if v>=35 else "warning" if v>=25 else "ok"
            rank_icon   = lambda v: "🔴" if v>=35 else "🟡" if v>=25 else "🟢"

        elif indicador_key == "vivienda":
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Madrid","Baleares","Cataluña","País Vasco","Canarias",
                    "Navarra","C. Valenciana","Andalucía","Cantabria",
                    "Aragón","Galicia","Asturias","La Rioja",
                    "Castilla y León","Murcia","Castilla-La Mancha","Extremadura",
                ],
                "precio_m2": [
                    4800,4200,3100,2850,2100,
                    1920,1820,1650,1580,
                    1420,1290,1180,1050,
                    1150,1240,980,860,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_vivienda_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("precio_m2", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["precio_m2"], y=df_s["ccaa"], orientation="h",
                    marker_color="#f0883e",
                    text=[f"{v:,.0f}€" for v in df_s["precio_m2"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Precio vivienda €/m² — Idealista/BdE 2025",
                    xaxis=dict(gridcolor="#21262d", range=[0, 5500]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("precio_m2", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "precio_m2", "€/m²"
            rank_alerta = lambda v: "alerta" if v>=3000 else "warning" if v>=2000 else "ok"
            rank_icon   = lambda v: "🔴" if v>=3000 else "🟡" if v>=2000 else "🟢"

        elif indicador_key == "sanidad":
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Ceuta","Melilla","Canarias","Andalucía","C. Valenciana",
                    "Cataluña","Murcia","Extremadura","Galicia",
                    "Castilla-La Mancha","Castilla y León","Asturias",
                    "Aragón","Baleares","Cantabria","Madrid",
                    "Navarra","La Rioja","País Vasco",
                ],
                "dias_espera": [
                    201,188,168,156,142,
                    134,131,145,121,
                    122,118,115,
                    109,127,103,98,
                    92,88,87,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_sanidad_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("dias_espera", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["dias_espera"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#f85149" if d>=150 else "#d29922" if d>=120 else "#3fb950"
                                  for d in df_s["dias_espera"]],
                    text=[f"{v}d" for v in df_s["dias_espera"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Días medios espera quirúrgica — SNS 2025",
                    xaxis=dict(gridcolor="#21262d", range=[0, 230]))
            st.plotly_chart(fig_m, use_container_width=True)
            df_rank = df_ccaa.sort_values("dias_espera", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "dias_espera", "d"
            rank_alerta = lambda v: "alerta" if v>=150 else "warning" if v>=120 else "ok"
            rank_icon   = lambda v: "🔴" if v>=150 else "🟡" if v>=120 else "🟢"

        else:  # renta
            df_ccaa = pd.DataFrame({
                "ccaa": [
                    "Madrid","País Vasco","Navarra","Cataluña","Baleares",
                    "La Rioja","Cantabria","Aragón","Asturias","C. Valenciana",
                    "Castilla y León","Galicia","Murcia","Canarias",
                    "Castilla-La Mancha","Andalucía","Ceuta","Melilla","Extremadura",
                ],
                "renta_hogar": [
                    36200,35800,34100,30400,29800,
                    27900,27200,26800,25900,24700,
                    24200,23800,22100,22400,
                    21800,21200,21600,20800,19400,
                ],
            })
            if HAS_MAPA:
                fig_m = mc.mapa_renta_ccaa(df_ccaa)
            else:
                df_s = df_ccaa.sort_values("renta_hogar", ascending=True)
                fig_m = go.Figure(go.Bar(
                    x=df_s["renta_hogar"], y=df_s["ccaa"], orientation="h",
                    marker_color=["#3fb950" if v>=30000 else "#d29922" if v>=24000 else "#f85149"
                                  for v in df_s["renta_hogar"]],
                    text=[f"{v:,.0f}€" for v in df_s["renta_hogar"]],
                    textposition="outside",
                ))
                fig_m.update_layout(**PLOT, height=500,
                    title="Renta media por hogar — INE ECV 2025 (€/año)",
                    xaxis=dict(gridcolor="#21262d", range=[0, 40000]))
            st.plotly_chart(fig_m, use_container_width=True)
            # ranking invertido: más renta = mejor (verde)
            df_rank = df_ccaa.sort_values("renta_hogar", ascending=False)
            rank_col, rank_val, rank_unit = "ccaa", "renta_hogar", "€"
            rank_alerta = lambda v: "ok" if v>=30000 else "warning" if v>=24000 else "alerta"
            rank_icon   = lambda v: "🟢" if v>=30000 else "🟡" if v>=24000 else "🔴"

    # ── Columna ranking ──────────────────────────────────────
    with col_rank:
        st.markdown("**Ranking**")
        for _, r in df_rank.iterrows():
            v   = r[rank_val]
            css = rank_alerta(v)
            ico = rank_icon(v)
            # formato valor
            if rank_unit in ("%",):
                val_fmt = f"{v:.1f}{rank_unit}"
            elif rank_unit in ("d",):
                val_fmt = f"{v:.0f} días"
            else:
                val_fmt = f"{v:,.0f} {rank_unit}"
            st.markdown(f"""
            <div class='kpi-card {css}'
                 style='padding:6px 10px;margin-bottom:3px'>
                <span style='font-size:0.78rem'>{ico} {r[rank_col]}</span><br>
                <b style='font-family:JetBrains Mono;font-size:0.82rem'>
                    {val_fmt}</b>
            </div>""", unsafe_allow_html=True)

    # ── Nota metodológica ────────────────────────────────────
    notas = {
        "paro":        "Tasa de paro EPA 2025T3. Fuente: INE. Media nacional: 11.4%",
        "paro_juvenil":"Paro <25 años. Fuente: EPA/INE 2025T3. Media UE: 14.9%",
        "vivienda":    "Precio medio venta €/m². Fuente: Idealista + Banco de España Q1 2026",
        "sanidad":     "Días medios espera quirúrgica. Fuente: SNS / Ministerio Sanidad 2025",
        "renta":       "Renta media neta por hogar. Fuente: INE Encuesta Condiciones de Vida 2025",
    }
    st.caption(f"📌 {notas[indicador_key]}")

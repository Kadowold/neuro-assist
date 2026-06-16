import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF

def obtener_coleccion(db, coleccion, paciente):
    try:
        docs = db.collection(coleccion).where(
            "paciente", "==", paciente
        ).order_by("fecha", direction="DESCENDING").stream()
        registros = []
        for doc in docs:
            datos = doc.to_dict()
            if "fecha" in datos and datos["fecha"] is not None:
                try:
                    datos["fecha"] = datos["fecha"].strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            registros.append(datos)
        return registros
    except:
        return []


def generar_pdf_expediente(paciente, datos_paciente, sintomas, calculadoras, pediatria, eeg_lista):
    pdf = FPDF()
    pdf.add_page()

    # Encabezado
    pdf.set_fill_color(45, 106, 159)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "NeuroApp - Expediente Clinico", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 10, f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(10)

    # Datos del paciente
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(45, 106, 159)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "DATOS DEL PACIENTE", ln=True, fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    for clave, valor in datos_paciente.items():
        pdf.cell(60, 7, f"{clave}:", border=0)
        pdf.cell(0, 7, str(valor), ln=True)
    pdf.ln(5)

    def seccion(titulo, registros, campos):
        pdf.set_fill_color(45, 106, 159)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, titulo, ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        if not registros:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 7, "Sin registros.", ln=True)
        else:
            pdf.set_font("Helvetica", "B", 8)
            ancho = 190 // len(campos)
            for campo in campos:
                pdf.cell(ancho, 7, campo.upper(), border=1, fill=False)
            pdf.ln()
            pdf.set_font("Helvetica", "", 8)
            fill = False
            for reg in registros[:10]:
                pdf.set_fill_color(235, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
                for campo in campos:
                    valor = str(reg.get(campo, "-"))[:20]
                    pdf.cell(ancho, 6, valor, border=1, fill=fill)
                pdf.ln()
                fill = not fill
        pdf.ln(4)

    seccion("SINTOMAS NEUROLOGICOS", sintomas,
            ["fecha", "tipo_sintoma", "intensidad", "duracion", "desencadenante"])

    seccion("CALCULADORAS CLINICAS", calculadoras,
            ["fecha", "escala", "puntaje", "interpretacion"])

    seccion("HISTORIAL PEDIATRICO - TRIAJE", 
            [p for p in pediatria if p.get("nivel_triaje")],
            ["fecha", "nivel_triaje", "temperatura", "sato2"])

    seccion("HISTORIAL PEDIATRICO - DESARROLLO",
            [p for p in pediatria if p.get("porcentaje")],
            ["fecha", "edad", "hitos_cumplidos", "interpretacion"])

    seccion("ANALISIS EEG",
            eeg_lista,
            ["fecha", "estado", "interpretacion"])

    return pdf


def expediente_clinico(db):
    st.header("Expediente Clinico")
    st.markdown("> Historial unificado completo del paciente.")
    st.divider()

    paciente = st.text_input("Buscar paciente", placeholder="Nombre exacto del paciente")

    if not paciente:
        st.info("Escribe el nombre del paciente para ver su expediente.")
        return

    if st.button("Cargar expediente"):
        st.session_state.expediente_paciente = paciente

    if "expediente_paciente" not in st.session_state:
        return

    paciente = st.session_state.expediente_paciente

    with st.spinner("Cargando expediente completo..."):
        sintomas = obtener_coleccion(db, "sintomas", paciente)
        calculadoras = obtener_coleccion(db, "calculadoras", paciente)
        triaje = obtener_coleccion(db, "triaje", paciente)
        desarrollo = obtener_coleccion(db, "desarrollo", paciente)
        crecimiento = obtener_coleccion(db, "crecimiento", paciente)
        dosis = obtener_coleccion(db, "dosis", paciente)
        eeg_lista = obtener_coleccion(db, "eeg", paciente)
        pediatria = triaje + desarrollo + crecimiento + dosis

    st.divider()

    # Resumen general
    st.subheader("Resumen del paciente")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sintomas", len(sintomas))
    col2.metric("Calculadoras", len(calculadoras))
    col3.metric("Pediatria", len(pediatria))
    col4.metric("EEG", len(eeg_lista))
    st.divider()

    # Datos del paciente para PDF
    datos_paciente = {
        "Nombre": paciente,
        "Total de registros": len(sintomas) + len(calculadoras) + len(pediatria) + len(eeg_lista),
        "Primer registro": sintomas[-1].get("fecha", "-") if sintomas else "-",
        "Ultimo registro": sintomas[0].get("fecha", "-") if sintomas else "-",
    }

    # Tabs por sección
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧠 Sintomas",
        "📊 Calculadoras",
        "👶 Pediatria",
        "🔬 EEG",
        "📄 Exportar PDF"
    ])

    with tab1:
        st.subheader("Historial de sintomas neurologicos")
        if sintomas:
            df = pd.DataFrame(sintomas)
            cols = [c for c in ["fecha", "tipo_sintoma", "intensidad", "duracion", "desencadenante", "notas"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)
        else:
            st.info("Sin registros de sintomas.")

    with tab2:
        st.subheader("Resultados de calculadoras clinicas")
        if calculadoras:
            df = pd.DataFrame(calculadoras)
            cols = [c for c in ["fecha", "escala", "puntaje", "interpretacion"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)
        else:
            st.info("Sin resultados de calculadoras.")

    with tab3:
        st.subheader("Historial pediatrico")
        if triaje:
            st.markdown("**Triaje**")
            df = pd.DataFrame(triaje)
            cols = [c for c in ["fecha", "nivel_triaje", "temperatura", "fc", "fr", "sato2"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)

        if desarrollo:
            st.markdown("**Desarrollo infantil**")
            df = pd.DataFrame(desarrollo)
            cols = [c for c in ["fecha", "edad", "hitos_cumplidos", "total_hitos", "porcentaje", "interpretacion"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)

        if crecimiento:
            st.markdown("**Curvas de crecimiento**")
            df = pd.DataFrame(crecimiento)
            cols = [c for c in ["fecha", "edad_meses", "peso_kg", "talla_cm", "imc", "peso_interpretacion"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)

        if dosis:
            st.markdown("**Medicamentos calculados**")
            df = pd.DataFrame(dosis)
            cols = [c for c in ["fecha", "medicamento", "peso", "dosis_calculada_mg"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)

        if not pediatria:
            st.info("Sin registros pediatricos.")

    with tab4:
        st.subheader("Analisis EEG")
        if eeg_lista:
            df = pd.DataFrame(eeg_lista)
            cols = [c for c in ["fecha", "estado", "interpretacion", "picos_detectados"] if c in df.columns]
            st.dataframe(df[cols], use_container_width=True)

            for eeg in eeg_lista[:3]:
                if "bandas" in eeg and eeg["bandas"]:
                    st.markdown(f"**EEG del {eeg.get('fecha', '')}**")
                    bandas = eeg["bandas"]
                    cols_b = st.columns(len(bandas))
                    for i, (banda, valor) in enumerate(bandas.items()):
                        cols_b[i].metric(banda.split("(")[0], f"{valor}%")
                    st.divider()
        else:
            st.info("Sin analisis EEG registrados.")

    with tab5:
        st.subheader("Exportar expediente completo en PDF")
        st.markdown("El PDF incluira todos los registros del paciente en un documento profesional.")

        if st.button("Generar PDF del expediente"):
            with st.spinner("Generando PDF..."):
                pdf = generar_pdf_expediente(
                    paciente, datos_paciente,
                    sintomas, calculadoras, pediatria, eeg_lista
                )
                pdf_bytes = bytes(pdf.output())
                st.download_button(
                    label="Descargar expediente PDF",
                    data=pdf_bytes,
                    file_name=f"expediente_{paciente}.pdf",
                    mime="application/pdf"
                )

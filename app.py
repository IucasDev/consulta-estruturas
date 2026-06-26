"""
Consulta de Estruturas Elétricas - Neoenergia Elektro
DIS-NOR-013 | DIS-NOR-014 | DIS-NOR-018

Para rodar: streamlit run app.py
"""

import io, subprocess, tempfile, os, glob, json, re
import streamlit as st
from PIL import Image

# ─────────────────────────────────────────────────────────────────
# CAMINHOS DOS PDFs — buscados na mesma pasta do app
# ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_013 = os.path.join(BASE_DIR, "DIS-NOR-013_Projeto_de_Rede_de_Distribuição_Compacta.pdf")
PDF_014 = os.path.join(BASE_DIR, "DIS-NOR-014-Projeto-Rede-Distribuicao-Aerea-Multiplexada-Baixa-Tensao-REV03.pdf")
PDF_018 = os.path.join(BASE_DIR, "DIS-NOR-018_Estruturas_para_Redes_de_Distribuição_Aéreas_com_Condutores_Nus_até_36_2_kV.pdf")

DPI = 220

# ─────────────────────────────────────────────────────────────────
# MAPA DE ESTRUTURAS
# Formato: código_exibido → (pdf_path, página_início, título, norma)
# A página é a página REAL do PDF (começa em 1)
# Cada estrutura tem 3 páginas: desenho, variação, relação de materiais
# ─────────────────────────────────────────────────────────────────

ESTRUTURAS = {
    # ── DIS-NOR-013 (181 páginas) ───────────────────────────────
    # Páginas das estruturas = número da página no documento (coincidem pois doc e PDF têm mesma numeração)
    "CE1":               (PDF_013, 42,  "Est.1 – CE1",                                    "DIS-NOR-013"),
    "CE1A":              (PDF_013, 45,  "Est.2 – CE1A",                                   "DIS-NOR-013"),
    "CE1A-PU":           (PDF_013, 48,  "Est.3 – CE1A-PU",                                "DIS-NOR-013"),
    "CEJ1":              (PDF_013, 51,  "Est.4 – CEJ1",                                   "DIS-NOR-013"),
    "CEJ1 SAH":          (PDF_013, 54,  "Est.5 – CEJ1 SAH",                               "DIS-NOR-013"),
    "CE2":               (PDF_013, 57,  "Est.6 – CE2",                                    "DIS-NOR-013"),
    "CE2-PU":            (PDF_013, 60,  "Est.7 – CE2-PU",                                 "DIS-NOR-013"),
    "CEJ2":              (PDF_013, 63,  "Est.8 – CEJ2",                                   "DIS-NOR-013"),
    "CEJ2 SAH":          (PDF_013, 66,  "Est.9 – CEJ2 SAH",                               "DIS-NOR-013"),
    "CE3":               (PDF_013, 69,  "Est.10 – CE3",                                   "DIS-NOR-013"),
    "CE3-PU":            (PDF_013, 72,  "Est.11 – CE3-PU",                                "DIS-NOR-013"),
    "CE4":               (PDF_013, 75,  "Est.12 – CE4",                                   "DIS-NOR-013"),
    "CE4-PU":            (PDF_013, 78,  "Est.13 – CE4-PU",                                "DIS-NOR-013"),
    "CE3-CE3":           (PDF_013, 81,  "Est.14 – CE3-CE3",                               "DIS-NOR-013"),
    "CE3PU-CE3PU":       (PDF_013, 84,  "Est.15 – CE3PU-CE3PU",                           "DIS-NOR-013"),
    "CE2.3":             (PDF_013, 87,  "Est.16 – CE2.3",                                 "DIS-NOR-013"),
    "CE2.CE3":           (PDF_013, 90,  "Est.17 – CE2.CE3",                               "DIS-NOR-013"),
    "CE2-CE3":           (PDF_013, 93,  "Est.18 – CE2-CE3",                               "DIS-NOR-013"),
    "CE2-CE3 CF":        (PDF_013, 96,  "Est.19 – CE2-CE3 CF",                            "DIS-NOR-013"),
    "CE2-CE3 CF LP":     (PDF_013, 99,  "Est.20 – CE2-CE3 CF LP",                         "DIS-NOR-013"),
    "CE2-N3 CF":         (PDF_013, 102, "Est.21 – CE2-N3 CF",                             "DIS-NOR-013"),
    "CE2 DS":            (PDF_013, 105, "Est.22 – CE2 DS",                                "DIS-NOR-013"),
    "CE3 DS":            (PDF_013, 108, "Est.23 – CE3 DS",                                "DIS-NOR-013"),
    "N3.CE3":            (PDF_013, 111, "Est.24 – N3.CE3",                                "DIS-NOR-013"),
    "N3.CE3 SUH":        (PDF_013, 114, "Est.25 – N3.CE3 SUH",                            "DIS-NOR-013"),
    "N3.CE3 SUI":        (PDF_013, 117, "Est.26 – N3.CE3 SUI",                            "DIS-NOR-013"),
    "B3.CE3":            (PDF_013, 120, "Est.27 – B3.CE3",                                "DIS-NOR-013"),
    "B3.CE3 SUI":        (PDF_013, 123, "Est.28 – B3.CE3 SUI",                            "DIS-NOR-013"),
    "CE3-I":             (PDF_013, 126, "Est.29 – CE3-I",                                 "DIS-NOR-013"),
    "CE3-I SUI":         (PDF_013, 129, "Est.30 – CE3-I SUI",                             "DIS-NOR-013"),
    "CE2 PR":            (PDF_013, 132, "Est.31 – CE2 PR",                                "DIS-NOR-013"),
    "CE4 CF":            (PDF_013, 135, "Est.32 – CE4 CF",                                "DIS-NOR-013"),
    "CE4 CF SAH":        (PDF_013, 138, "Est.33 – CE4 CF SAH",                            "DIS-NOR-013"),
    "CE4 SUH":           (PDF_013, 141, "Est.34 – CE4 SUH",                               "DIS-NOR-013"),
    "CE4 SUI":           (PDF_013, 144, "Est.35 – CE4 SUI",                               "DIS-NOR-013"),
    "CE2 TR":            (PDF_013, 147, "Est.36 – CE2 TR",                                "DIS-NOR-013"),
    "CE3 TR":            (PDF_013, 150, "Est.37 – CE3 TR",                                "DIS-NOR-013"),
    "CE3 TRSC":          (PDF_013, 153, "Est.38 – CE3 TRSC",                              "DIS-NOR-013"),
    "CE4 TR":            (PDF_013, 156, "Est.39 – CE4 TR",                                "DIS-NOR-013"),
    "AT Condutor Ext":   (PDF_013, 159, "Est.40 – Aterramento Condutor Externo",          "DIS-NOR-013"),
    "AT Condutor Int":   (PDF_013, 162, "Est.41 – Aterramento Condutor Interno",          "DIS-NOR-013"),
    "Bifásicas Básicas":  (PDF_013, 172, "Est.42 – Bifásicas Básicas",                    "DIS-NOR-013"),
    "Bifásica Derivação": (PDF_013, 173, "Est.43 – Bifásicas de Derivação",               "DIS-NOR-013"),
    "Bifásica Transição": (PDF_013, 174, "Est.44 – Bifásicas de Transição",               "DIS-NOR-013"),
    "Bifásica CF":        (PDF_013, 175, "Est.45 – Bifásica para Chaves Fusíveis",        "DIS-NOR-013"),
    "Bifásica Para-raios":(PDF_013, 176, "Est.46 – Bifásica para Para-raios",             "DIS-NOR-013"),
    "Bifásica TR sob Rede":(PDF_013,177, "Est.47 – Bifásica TR sob a Rede",               "DIS-NOR-013"),
    "Bifásica TR Fim Rede":(PDF_013,178, "Est.48 – Bifásica TR em Fim de Rede",           "DIS-NOR-013"),
    "Bifásica TR sem CF": (PDF_013, 179, "Est.49 – Bifásica TR sem Chaves Fusíveis",      "DIS-NOR-013"),
    "Monofásicas Básicas":(PDF_013, 180, "Est.50 – Monofásicas Básicas",                  "DIS-NOR-013"),
    "Monofásicas Deriv.": (PDF_013, 181, "Est.51 – Monofásicas de Derivação",             "DIS-NOR-013"),

    # ── DIS-NOR-014 (53 páginas) ────────────────────────────────
    # Estruturas começam na página 15 do PDF
    "STBI":              (PDF_014, 15,  "Est.1 – STBI",                                   "DIS-NOR-014"),
    "SMBI":              (PDF_014, 16,  "Est.2 – SMBI",                                   "DIS-NOR-014"),
    "FLABIT":            (PDF_014, 17,  "Est.3 – FLABIT",                                 "DIS-NOR-014"),
    "FLABIM":            (PDF_014, 18,  "Est.4 – FLABIM",                                 "DIS-NOR-014"),
    "FLABIDT":           (PDF_014, 19,  "Est.5 – FLABIDT",                                "DIS-NOR-014"),
    "FLABIDM":           (PDF_014, 20,  "Est.6 – FLABIDM",                                "DIS-NOR-014"),
    "FLBIT":             (PDF_014, 21,  "Est.7 – FLBIT",                                  "DIS-NOR-014"),
    "FLBIM":             (PDF_014, 22,  "Est.8 – FLBIM",                                  "DIS-NOR-014"),
    "FLBIT NI":          (PDF_014, 23,  "Est.9 – FLBIT NI",                               "DIS-NOR-014"),
    "FLBIM NI":          (PDF_014, 24,  "Est.10 – FLBIM NI",                              "DIS-NOR-014"),
    "SDBIT":             (PDF_014, 25,  "Est.11 – SDBIT",                                 "DIS-NOR-014"),
    "SDBIM":             (PDF_014, 27,  "Est.12 – SDBIM",                                 "DIS-NOR-014"),
    "SDANI":             (PDF_014, 29,  "Est.13 – SDANI",                                 "DIS-NOR-014"),
    "SPBI":              (PDF_014, 30,  "Est.14 – SPBI",                                  "DIS-NOR-014"),
    "SAB":               (PDF_014, 31,  "Est.15 – SAB",                                   "DIS-NOR-014"),
    "CAB":               (PDF_014, 32,  "Est.16 – CAB",                                   "DIS-NOR-014"),
    "IBI":               (PDF_014, 33,  "Est.17 – IBI",                                   "DIS-NOR-014"),
    "AT Ext (014)":      (PDF_014, 34,  "Est.18 – Aterramento Condutor Externo",          "DIS-NOR-014"),
    "AT Int (014)":      (PDF_014, 35,  "Est.19 – Aterramento Condutor Interno",          "DIS-NOR-014"),
    "LCM":               (PDF_014, 36,  "Est.20 – LCM",                                   "DIS-NOR-014"),
    "IT-R":              (PDF_014, 37,  "Est.21 – IT-R",                                  "DIS-NOR-014"),
    "ITF-R":             (PDF_014, 38,  "Est.22 – ITF-R",                                 "DIS-NOR-014"),

    # ── DIS-NOR-018 (222 páginas) ───────────────────────────────
    # Offset: página do doc = página do PDF (numeração coincide)
    "U1":                (PDF_018, 11,  "Est.1 – U1",                                     "DIS-NOR-018"),
    "U2":                (PDF_018, 12,  "Est.2 – U2",                                     "DIS-NOR-018"),
    "U3":                (PDF_018, 13,  "Est.3 – U3",                                     "DIS-NOR-018"),
    "U3-3":              (PDF_018, 14,  "Est.4 – U3-3",                                   "DIS-NOR-018"),
    "U4":                (PDF_018, 15,  "Est.5 – U4",                                     "DIS-NOR-018"),
    "N1":                (PDF_018, 16,  "Est.6 – N1",                                     "DIS-NOR-018"),
    "N3 (018)":          (PDF_018, 17,  "Est.7 – N3",                                     "DIS-NOR-018"),
    "N4":                (PDF_018, 18,  "Est.8 – N4",                                     "DIS-NOR-018"),
    "N3-N3 (018)":       (PDF_018, 19,  "Est.9 – N3-N3",                                  "DIS-NOR-018"),
    "N4-N3 (018)":       (PDF_018, 20,  "Est.10 – N4-N3",                                 "DIS-NOR-018"),
    "N1-TT":             (PDF_018, 21,  "Est.11 – N1-TT",                                 "DIS-NOR-018"),
    "N3-TT":             (PDF_018, 23,  "Est.12 – N3-TT",                                 "DIS-NOR-018"),
    "N3-TT-SOB":         (PDF_018, 26,  "Est.13 – N3-TT-SOB",                             "DIS-NOR-018"),
    "N4-CFU":            (PDF_018, 28,  "Est.14 – N4-CFU",                                "DIS-NOR-018"),
    "N4-N3-CFU":         (PDF_018, 29,  "Est.15 – N4-N3-CFU",                             "DIS-NOR-018"),
    "TE":                (PDF_018, 30,  "Est.16 – TE",                                    "DIS-NOR-018"),
    "B1":                (PDF_018, 31,  "Est.17 – B1",                                    "DIS-NOR-018"),
    "B3 (018)":          (PDF_018, 32,  "Est.18 – B3",                                    "DIS-NOR-018"),
    "B4":                (PDF_018, 33,  "Est.19 – B4",                                    "DIS-NOR-018"),
    "CFU 1º NÍVEL":      (PDF_018, 34,  "Est.20 – CFU 1º Nível",                          "DIS-NOR-018"),
    "ESTAI NORMAL":      (PDF_018, 35,  "Est.21 – Estai em Terreno Normal",               "DIS-NOR-018"),
    "ESTAI ROCHA":       (PDF_018, 36,  "Est.22 – Estai em Rochas e Pântanos",            "DIS-NOR-018"),
    "ESTAI CONTRAPOSTE": (PDF_018, 37,  "Est.23 – Estaiamento de Contraposte",            "DIS-NOR-018"),
    "PARA-RAIOS 2ºNÍV":  (PDF_018, 38,  "Est.24 – Para-raios em 2º Nível",               "DIS-NOR-018"),
    "TE FIM REDE":       (PDF_018, 47,  "Est.31 – TE Fim de Rede",                        "DIS-NOR-018"),
    "HTE":               (PDF_018, 48,  "Est.32 – HTE",                                   "DIS-NOR-018"),
    "HTE FIM REDE":      (PDF_018, 49,  "Est.33 – HTE Fim de Rede",                       "DIS-NOR-018"),
    "HTC":               (PDF_018, 50,  "Est.34 – HTC",                                   "DIS-NOR-018"),
    "HTC FIM REDE":      (PDF_018, 51,  "Est.35 – HTC Fim de Rede",                       "DIS-NOR-018"),
    "LDE":               (PDF_018, 52,  "Est.36 – LDE",                                   "DIS-NOR-018"),
    "M1-N3":             (PDF_018, 53,  "Est.37 – M1-N3",                                 "DIS-NOR-018"),
    "HTE-N3":            (PDF_018, 54,  "Est.38 – HTE-N3",                                "DIS-NOR-018"),
    "HTC-N3":            (PDF_018, 55,  "Est.39 – HTC-N3",                                "DIS-NOR-018"),
    "HTE-2XN3":          (PDF_018, 56,  "Est.40 – HTE-2xN3",                              "DIS-NOR-018"),
    "HTC-2XN3":          (PDF_018, 58,  "Est.41 – HTC-2xN3",                              "DIS-NOR-018"),
    "M1-N2 FR Chaves":   (PDF_018, 60,  "Est.42 – M1-N2 Fim de Rede com Chaves",          "DIS-NOR-018"),
    "M1-N3 FR Chaves":   (PDF_018, 61,  "Est.43 – M1-N3 Fim de Rede com Chaves",          "DIS-NOR-018"),
    "HTE-1 Deriv N3":    (PDF_018, 158, "Est.101 – Derivação HTE-1 N3",                   "DIS-NOR-018"),
    "HTE-2 Deriv N3":    (PDF_018, 160, "Est.102 – Derivação HTE-2 N3",                   "DIS-NOR-018"),
    "HTC-1 Deriv N3":    (PDF_018, 162, "Est.103 – Derivação HTC-1 N3",                   "DIS-NOR-018"),
    "HTC-2 Deriv N3":    (PDF_018, 164, "Est.104 – Derivação HTC-2 N3",                   "DIS-NOR-018"),
    "AT Descida Ext":    (PDF_018, 172, "Est.109 – Aterramento Primária Condutor Externo", "DIS-NOR-018"),
    "AT Descida Int":    (PDF_018, 173, "Est.110 – Aterramento Primária Condutor Interno", "DIS-NOR-018"),
    "PT Est.M1":         (PDF_018, 174, "Est.111 – PT Estrutura M1",                      "DIS-NOR-018"),
    "PT Est.N3":         (PDF_018, 176, "Est.112 – PT Estrutura N3",                      "DIS-NOR-018"),
    "PT Est.N3 FimRede": (PDF_018, 178, "Est.113 – PT N3 Fim de Rede",                    "DIS-NOR-018"),
    "U1-U3 s/Chaves":    (PDF_018, 181, "Est.115 – U1-U3 Ramal sem Chaves",               "DIS-NOR-018"),
    "U1-U3 c/Chaves":    (PDF_018, 182, "Est.116 – U1-U3 Ramal com Chaves",               "DIS-NOR-018"),
    "PT Est.U1":         (PDF_018, 190, "Est.120 – PT Estrutura U1",                      "DIS-NOR-018"),
    "PT N3 com Chaves":  (PDF_018, 115, "Est.76 – PT N3 com Chaves",                      "DIS-NOR-018"),
    "PT N3 sem Chaves":  (PDF_018, 117, "Est.77 – PT N3 sem Chaves",                      "DIS-NOR-018"),
    "PT N3 sem Chaves 2":(PDF_018, 119, "Est.78 – PT N3 sem Chaves (var.2)",              "DIS-NOR-018"),
    "PT N3 2+ Clientes": (PDF_018, 121, "Est.79 – PT Ligação 2 ou Mais Clientes",         "DIS-NOR-018"),
    "N4 COM CRUZETA":    (PDF_018, 144, "Est.93 – N4 com Cruzeta de Ferro",               "DIS-NOR-018"),
    "M-N2BFR":           (PDF_018, 197, "Est.125 – Derivação M-N2BFR",                    "DIS-NOR-018"),
    "M-N3B":             (PDF_018, 198, "Est.126 – Derivação M-N3B",                      "DIS-NOR-018"),
    "N4 COM CRUZETA":    (PDF_018, 144, "Est.93 – N4 com Cruzeta de Ferro",               "DIS-NOR-018"),
}

CORES_NORMA = {
    "DIS-NOR-013": "#2fbf71",
    "DIS-NOR-014": "#4f8cff",
    "DIS-NOR-018": "#ff8a3d",
}

NOTAS_ESTRUTURAS = {
    "CE1": [
        "Utilizada em tangentes e deflexões da rede até 6°.",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação.",
    ],
    "CE1A": [
        "Utilizada a cada 200 m de rede, em longos trechos com várias estruturas tipo CE1.",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação.",
    ],
    "CE1A-PU": [
        "Utilizada a cada 200 m de rede, em longos trechos com várias estruturas tipo CE1.",
        "Deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária.",
        "Possibilita elevar a altura da rede em 0,5 m quando comparada com a CE1A.",
        "Não se aplica em redes de 34,5 kV.",
    ],
    "CE2": [
        "Utilizada nos casos de deflexão da rede de 7° à 60° para cabos de seções 35 e 70 mm² e 7° à 45° para cabos de 185 e 240 mm².",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação.",
    ],
    "CE3": [
        "Utilizada em fim de rede e em ângulos de deflexão de 60° a 90°.",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação.",
    ],
    "CE4": [
        "Utilizada em fim de rede e em ângulos de deflexão de 60° a 90°.",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação.",
    ],
    "CEJ1": [
        "Utilizada com o objetivo de afastar os condutores de edificações.",
        "Não deve ser utilizada em postes de 200 daN quando a bitola dos condutores for ≥185 mm² (15 kV) ou ≥70 mm² (36 kV).",
    ],
    "STBI": [
        "Redes trifásicas tangentes e ângulos α ≤ 30°.",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.7 desta especificação.",
    ],
    "SMBI": [
        "Redes monofásicas tangentes e ângulos α ≤ 30°.",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.7 desta especificação.",
    ],
    "FLABIT": [
        "Redes trifásicas com ângulos 30° < α ≤ 60°, mudança de seção e alívio de tensão mecânica.",
        "Pode ser usada também para emendas dos cabos.",
    ],
    "FLBIT": ["Fim de linha de rede trifásica."],
    "FLBIM": ["Fim de linha de rede monofásica."],
    "SDBIT": ["Estrutura para derivação de rede trifásica."],
    "SDBIM": ["Estrutura para derivação de rede monofásica."],
    "SAB":   ["Seccionamento aéreo."],
    "CAB":   ["Cruzamento aéreo multiplexado/multiplexado."],
    "IBI":   ["Interligação nu/multiplexado."],
    "U1":    ["Estrutura básica tipo U1 para redes com condutores nus."],
    "N1":    ["Estrutura básica tipo N1 para redes com condutores nus."],
    "N3 (018)": ["Estrutura básica tipo N3 para redes com condutores nus."],
    "HTE":   ["Estrutura HTE utilizada em redes com condutores nus — exclusivo Neoenergia Elektro."],
    "HTC":   ["Estrutura HTC utilizada em redes com condutores nus — exclusivo Neoenergia Elektro."],
}

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES
# ─────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Carregando desenho...")
def extrair_imagem(pdf_path: str, pagina: int, dpi: int = 200) -> bytes | None:
    """Extrai uma página do PDF como imagem PNG."""
    if not os.path.exists(pdf_path):
        return None
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path)
        try:
            page = pdf[pagina - 1]
            img = page.render(scale=dpi / 72).to_pil()
        finally:
            pdf.close()
    except Exception:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                prefix = os.path.join(tmpdir, "pag")
                subprocess.run(
                    ["pdftoppm", "-jpeg", "-r", str(dpi),
                     "-f", str(pagina), "-l", str(pagina),
                     pdf_path, prefix],
                    check=True, capture_output=True,
                )
                arquivos = sorted(glob.glob(f"{prefix}-*.jpg"))
                if not arquivos:
                    return None
                img = Image.open(arquivos[0])
        except Exception:
            return None

    # Cortar cabeçalho (11% do topo — logo, título, código)
    w, h = img.size
    img = img.crop((0, int(h * 0.11), w, h))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def get_paginas(estrutura_key: str) -> list[tuple[int, str]]:
    """Retorna lista de (página, título_coluna) para a estrutura."""
    pdf_path, pag_inicio, titulo, norma = ESTRUTURAS[estrutura_key]
    
    # Estruturas de uma única página (bifásicas/monofásicas no final do 013, AT, etc.)
    paginas_unicas = [
        "Bifásicas Básicas", "Bifásica Derivação", "Bifásica Transição",
        "Bifásica CF", "Bifásica Para-raios", "Bifásica TR sob Rede",
        "Bifásica TR Fim Rede", "Bifásica TR sem CF",
        "Monofásicas Básicas", "Monofásicas Deriv.",
        "AT Condutor Ext", "AT Condutor Int", "AT Ext (014)", "AT Int (014)",
        "AT Descida Ext", "AT Descida Int",
        "SAB", "CAB", "IBI", "LCM", "IT-R", "ITF-R",
        "SDANI", "SPBI", "FLABIDT", "FLABIDM",
        "ESTAI NORMAL", "ESTAI ROCHA", "ESTAI CONTRAPOSTE",
        "PARA-RAIOS 2ºNÍV", "CFU 1º NÍVEL",
        "PARA-RAIOS 2ºNÍV",
    ]
    
    if estrutura_key in paginas_unicas:
        return [(pag_inicio, "Desenho e Relação de Materiais")]
    
    # Padrão: 3 colunas
    return [
        (pag_inicio,     "Estrutura"),
        (pag_inicio + 1, "Variação / Detalhes"),
        (pag_inicio + 2, "Relação de Materiais"),
    ]


@st.cache_data
def load_normative_index():
    """Carrega normatives_text.json se disponível."""
    for path in [
        os.path.join(BASE_DIR, "normatives_text.json"),
        "normatives_text.json",
    ]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return None


def buscar_referencias(keyword: str, normative_data: dict) -> list[dict]:
    if not keyword or not normative_data:
        return []
    pattern = re.compile(re.escape(keyword.strip()), re.IGNORECASE)
    results = []
    seen = set()
    for doc_name, pages_data in normative_data.items():
        for page_info in pages_data:
            content = page_info.get("content", "")
            page_number = page_info.get("page", "")
            for line in content.split('\n'):
                if pattern.search(line):
                    snippet = line.strip()
                    if snippet:
                        key = (doc_name, page_number, snippet[:80])
                        if key not in seen:
                            seen.add(key)
                            results.append({
                                "document": doc_name,
                                "page": page_number,
                                "text": snippet,
                            })
    return results


# ─────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Estruturas Elétricas – Neoenergia Elektro",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg,#07131f 0%,#0f2236 45%,#16324d 100%); color:#f4f7fb; }
.block-container { padding-top:1.5rem; padding-bottom:2rem; }
div[data-testid="stSidebar"] { background:rgba(7,19,31,0.95); border-right:1px solid rgba(255,255,255,0.08); }
.stButton > button { background:linear-gradient(90deg,#2fbf71,#4f8cff); color:white; border:none; border-radius:8px; }
.stButton > button:hover { opacity:0.92; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ Estruturas Elétricas")
    st.caption("Neoenergia Elektro")
    st.divider()

    norma_filtro = st.selectbox(
        "Filtrar por norma",
        ["Todas", "DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"],
    )
    st.divider()

    if "estrutura_ativa" not in st.session_state:
        st.session_state["estrutura_ativa"] = None

    codigos_ordenados = sorted(ESTRUTURAS.keys())
    for norma in ["DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"]:
        if norma_filtro not in ("Todas", norma):
            continue
        cor = CORES_NORMA[norma]
        st.markdown(
            f'<div style="color:{cor};font-weight:bold;font-size:12px;margin-top:8px;margin-bottom:4px;">{norma}</div>',
            unsafe_allow_html=True,
        )
        for codigo in codigos_ordenados:
            pdf_path, pag, titulo, n = ESTRUTURAS[codigo]
            if n != norma:
                continue
            ativo = st.session_state["estrutura_ativa"] == codigo
            label = f"▶ {codigo}" if ativo else codigo
            if st.button(label, key=f"btn_{codigo}", use_container_width=True):
                st.session_state["estrutura_ativa"] = codigo
                st.rerun()

# Área principal
selecionada = st.session_state.get("estrutura_ativa")

if not selecionada:
    st.title("⚡ Estruturas Elétricas — Neoenergia Elektro")
    st.info("👈 Selecione uma estrutura na lista à esquerda.")
else:
    pdf_path, pag_inicio, titulo, norma = ESTRUTURAS[selecionada]
    cor = CORES_NORMA[norma]

    st.markdown(f'<h2 style="color:{cor};margin-bottom:0.2rem;">{titulo}</h2>', unsafe_allow_html=True)
    st.markdown(f'<span style="background:{cor};color:white;padding:3px 12px;border-radius:999px;font-size:13px;">{norma}</span>', unsafe_allow_html=True)
    st.write("")

    # ── Verificar se PDF existe
    if not os.path.exists(pdf_path):
        st.error(f"PDF não encontrado: `{os.path.basename(pdf_path)}`\n\nCertifique-se de que os 3 PDFs estão na mesma pasta do `app.py`.")
    else:
        st.markdown("### 🧩 Desenhos e relação de materiais")
        st.caption("A instalação atual prioriza o poste tubular; o poste DT é mostrado apenas como referência de manutenção.")

        paginas = get_paginas(selecionada)
        cols = st.columns(len(paginas))

        for col, (page_no, titulo_col) in zip(cols, paginas):
            with col:
                st.markdown(f"**{titulo_col}**")
                img_bytes = extrair_imagem(pdf_path, page_no, DPI)
                if img_bytes:
                    st.image(img_bytes, use_container_width=True, output_format="PNG")
                else:
                    st.info(f"Página {page_no} indisponível.")

    # ── Notas
    st.divider()
    st.markdown("### ℹ️ Informações da estrutura")
    notas = NOTAS_ESTRUTURAS.get(selecionada)
    if notas:
        for nota in notas:
            st.markdown(f"- {nota}")
    else:
        st.caption("Consulte sempre as DIS-NORs para critérios completos de aplicação.")

    # ── Referências nos normativos
    st.divider()
    st.markdown("### 📑 Referências nos normativos")
    normative_data = load_normative_index()
    if normative_data:
        refs = buscar_referencias(selecionada.split(" ")[0], normative_data)
        if refs:
            by_doc = {}
            for r in refs:
                by_doc.setdefault(r["document"], []).append(r)
            for doc, items in sorted(by_doc.items()):
                pages = sorted({str(i["page"]) for i in items})
                st.markdown(f"**{doc}** — páginas: {', '.join(pages)}")
                for item in items[:5]:
                    st.caption(f"• Pág. {item['page']} — {item['text'][:120]}")
        else:
            st.info("Nenhuma referência adicional encontrada nos normativos indexados.")
    else:
        st.caption("Índice de normativos (`normatives_text.json`) não encontrado — funcionalidade de busca desativada.")

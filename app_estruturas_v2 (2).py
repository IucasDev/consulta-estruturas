"""
Consulta de Estruturas Elétricas - Neoenergia Elektro
DIS-NOR-013 | DIS-NOR-014 | DIS-NOR-018

Para rodar: streamlit run app_estruturas_v2.py
"""

import io, subprocess, tempfile, os, glob, json, re
import streamlit as st
from PIL import Image

PDF_PATH = "Estruturas_DIS-NOR-013_014_018.pdf"
DPI = 260

# ─────────────────────────────────────────────────────────────────
# MAPA DE ESTRUTURAS  {código_exibido: (página_no_combinado, título_completo, norma)}
# ─────────────────────────────────────────────────────────────────
ESTRUTURAS = {
    # ── DIS-NOR-013 ─────────────────────────────────────────────
    "AT Condutor Ext (013)":  (117, "Est.40 – Aterramento com Condutor Externo",          "DIS-NOR-013"),
    "AT Condutor Int (013)":  (120, "Est.41 – Aterramento com Condutor Interno",           "DIS-NOR-013"),
    "B3.CE3":                 (78,  "Est.27 – B3.CE3",                                     "DIS-NOR-013"),
    "B3.CE3 SUI":             (81,  "Est.28 – B3.CE3 SUI",                                 "DIS-NOR-013"),
    "Bifásica CF":            (133, "Est.45 – Bifásica para Instalação de Chaves",         "DIS-NOR-013"),
    "Bifásica Derivação":     (131, "Est.43 – Bifásicas de Derivação",                     "DIS-NOR-013"),
    "Bifásica Para-raios":    (134, "Est.46 – Bifásica para Instalação de Para-raios",     "DIS-NOR-013"),
    "Bifásica TR Fim Rede":   (136, "Est.48 – Bifásica TR em Fim de Rede",                 "DIS-NOR-013"),
    "Bifásica TR sem CF":     (137, "Est.49 – Bifásica TR sem Chaves Fusíveis",            "DIS-NOR-013"),
    "Bifásica TR sob Rede":   (135, "Est.47 – Bifásica TR sob a Rede",                     "DIS-NOR-013"),
    "Bifásicas Básicas":      (130, "Est.42 – Estruturas Bifásicas Básicas",               "DIS-NOR-013"),
    "Bifásica Transição":     (132, "Est.44 – Bifásicas de Transição de Redes",            "DIS-NOR-013"),
    "CE1":                    (1,   "Est.1 – CE1",                                         "DIS-NOR-013"),
    "CE1A":                   (3,   "Est.2 – CE1A",                                        "DIS-NOR-013"),
    "CE1A-PU":                (6,   "Est.3 – CE1A-PU",                                     "DIS-NOR-013"),
    "CE2":                    (15,  "Est.6 – CE2",                                         "DIS-NOR-013"),
    "CE2 DS":                 (63,  "Est.22 – CE2 DS",                                     "DIS-NOR-013"),
    "CE2 PR":                 (90,  "Est.31 – CE2 PR",                                     "DIS-NOR-013"),
    "CE2 TR":                 (105, "Est.36 – CE2 TR",                                     "DIS-NOR-013"),
    "CE2-CE3":                (51,  "Est.18 – CE2-CE3",                                    "DIS-NOR-013"),
    "CE2-CE3 CF":             (54,  "Est.19 – CE2-CE3 CF",                                 "DIS-NOR-013"),
    "CE2-CE3 CF LP":          (57,  "Est.20 – CE2-CE3 CF LP",                              "DIS-NOR-013"),
    "CE2-N3 CF":              (60,  "Est.21 – CE2-N3 CF",                                  "DIS-NOR-013"),
    "CE2-PU":                 (18,  "Est.7 – CE2-PU",                                      "DIS-NOR-013"),
    "CE2.3":                  (45,  "Est.16 – CE2.3",                                      "DIS-NOR-013"),
    "CE2.CE3":                (49,  "Est.17 – CE2.CE3",                                    "DIS-NOR-013"),
    "CE3":                    (27,  "Est.10 – CE3",                                        "DIS-NOR-013"),
    "CE3 DS":                 (66,  "Est.23 – CE3 DS",                                     "DIS-NOR-013"),
    "CE3 TR":                 (108, "Est.37 – CE3 TR",                                     "DIS-NOR-013"),
    "CE3 TRSC":               (111, "Est.38 – CE3 TRSC",                                   "DIS-NOR-013"),
    "CE3-CE3":                (39,  "Est.14 – CE3-CE3",                                    "DIS-NOR-013"),
    "CE3-I":                  (84,  "Est.29 – CE3-I",                                      "DIS-NOR-013"),
    "CE3-I SUI":              (87,  "Est.30 – CE3-I SUI",                                  "DIS-NOR-013"),
    "CE3-PU":                 (30,  "Est.11 – CE3-PU",                                     "DIS-NOR-013"),
    "CE3PU-CE3PU":            (42,  "Est.15 – CE3PU-CE3PU",                                "DIS-NOR-013"),
    "CE4":                    (33,  "Est.12 – CE4",                                        "DIS-NOR-013"),
    "CE4 CF":                 (93,  "Est.32 – CE4 CF",                                     "DIS-NOR-013"),
    "CE4 CF SAH":             (96,  "Est.33 – CE4 CF SAH",                                 "DIS-NOR-013"),
    "CE4 SUH":                (99,  "Est.34 – CE4 SUH",                                    "DIS-NOR-013"),
    "CE4 SUI":                (102, "Est.35 – CE4 SUI",                                    "DIS-NOR-013"),
    "CE4 TR":                 (114, "Est.39 – CE4 TR",                                     "DIS-NOR-013"),
    "CE4-PU":                 (36,  "Est.13 – CE4-PU",                                     "DIS-NOR-013"),
    "CEJ1":                   (9,   "Est.4 – CEJ1",                                        "DIS-NOR-013"),
    "CEJ1 SAH":               (12,  "Est.5 – CEJ1 SAH",                                    "DIS-NOR-013"),
    "CEJ2":                   (21,  "Est.8 – CEJ2",                                        "DIS-NOR-013"),
    "CEJ2 SAH":               (24,  "Est.9 – CEJ2 SAH",                                    "DIS-NOR-013"),
    "Monofásicas Básicas":    (138, "Est.50 – Estruturas Monofásicas Básicas",             "DIS-NOR-013"),
    "Monofásicas Derivação":  (139, "Est.51 – Monofásicas de Derivação",                   "DIS-NOR-013"),
    "N3.CE3":                 (69,  "Est.24 – N3.CE3",                                     "DIS-NOR-013"),
    "N3.CE3 SUH":             (72,  "Est.25 – N3.CE3 SUH",                                 "DIS-NOR-013"),
    "N3.CE3 SUI":             (75,  "Est.26 – N3.CE3 SUI",                                 "DIS-NOR-013"),
    # ── DIS-NOR-014 ─────────────────────────────────────────────
    "AT Condutor Ext (014)":  (159, "Est.18 – Aterramento: Condutor Externo",              "DIS-NOR-014"),
    "AT Condutor Int (014)":  (160, "Est.19 – Aterramento: Condutor Interno",              "DIS-NOR-014"),
    "CAB":                    (157, "Est.16 – CAB – Cruzamento Aéreo Multiplexado",        "DIS-NOR-014"),
    "FLABIT":                 (142, "Est.3 – FLABIT",                                      "DIS-NOR-014"),
    "FLABIDM":                (145, "Est.6 – FLABIDM",                                     "DIS-NOR-014"),
    "FLABIDT":                (144, "Est.5 – FLABIDT",                                     "DIS-NOR-014"),
    "FLABIM":                 (143, "Est.4 – FLABIM",                                      "DIS-NOR-014"),
    "FLBIM":                  (147, "Est.8 – FLBIM",                                       "DIS-NOR-014"),
    "FLBIM NI":               (149, "Est.10 – FLBIM NI",                                   "DIS-NOR-014"),
    "FLBIT":                  (146, "Est.7 – FLBIT",                                       "DIS-NOR-014"),
    "FLBIT NI":               (148, "Est.9 – FLBIT NI",                                    "DIS-NOR-014"),
    "IBI":                    (158, "Est.17 – IBI – Interligação Nu/Multiplexado",         "DIS-NOR-014"),
    "IT-R":                   (162, "Est.21 – IT-R",                                       "DIS-NOR-014"),
    "ITF-R":                  (163, "Est.22 – ITF-R",                                      "DIS-NOR-014"),
    "LCM":                    (161, "Est.20 – LCM – Ligação Consumidores Multiderivações", "DIS-NOR-014"),
    "SAB":                    (156, "Est.15 – SAB – Seccionamento Aéreo",                  "DIS-NOR-014"),
    "SDBIM":                  (152, "Est.12 – SDBIM",                                      "DIS-NOR-014"),
    "SDBIT":                  (150, "Est.11 – SDBIT",                                      "DIS-NOR-014"),
    "SDANI":                  (154, "Est.13 – SDANI",                                      "DIS-NOR-014"),
    "SMBI":                   (141, "Est.2 – SMBI",                                        "DIS-NOR-014"),
    "SPBI":                   (155, "Est.14 – SPBI",                                       "DIS-NOR-014"),
    "STBI":                   (140, "Est.1 – STBI",                                        "DIS-NOR-014"),
    # ── DIS-NOR-018 ─────────────────────────────────────────────
    "AT Descida Ext (018)":   (330, "Est.109 – Aterramento Primária Condutor Externo",     "DIS-NOR-018"),
    "AT Descida Int (018)":   (331, "Est.110 – Aterramento Primária Condutor Interno",     "DIS-NOR-018"),
    "B1":                     (189, "Est.17 – B1",                                         "DIS-NOR-018"),
    "B3 (018)":               (190, "Est.18 – B3",                                         "DIS-NOR-018"),
    "B4":                     (191, "Est.19 – B4",                                         "DIS-NOR-018"),
    "CFU 1º NÍVEL":           (192, "Est.20 – CFU 1º Nível",                               "DIS-NOR-018"),
    "ESTAI CONTRAPOSTE":      (195, "Est.23 – Estaiamento de Contraposte",                 "DIS-NOR-018"),
    "ESTAI NORMAL":           (193, "Est.21 – Estai em Terreno Normal",                    "DIS-NOR-018"),
    "ESTAI ROCHA":            (194, "Est.22 – Estai em Rochas e Pântanos",                 "DIS-NOR-018"),
    "HTC":                    (208, "Est.34 – HTC",                                        "DIS-NOR-018"),
    "HTC FIM REDE":           (209, "Est.35 – HTC Fim de Rede",                            "DIS-NOR-018"),
    "HTE":                    (206, "Est.32 – HTE",                                        "DIS-NOR-018"),
    "HTE FIM REDE":           (207, "Est.33 – HTE Fim de Rede",                            "DIS-NOR-018"),
    "HTC-1 Deriv N3":         (320, "Est.103 – Derivação HTC-1 N3",                        "DIS-NOR-018"),
    "HTC-2 Deriv N3":         (322, "Est.104 – Derivação HTC-2 N3",                        "DIS-NOR-018"),
    "HTE-1 Deriv N3":         (316, "Est.101 – Derivação HTE-1 N3",                        "DIS-NOR-018"),
    "HTE-2 Deriv N3":         (318, "Est.102 – Derivação HTE-2 N3",                        "DIS-NOR-018"),
    "HTE-2XN3":               (214, "Est.40 – HTE-2XN3",                                   "DIS-NOR-018"),
    "HTE-N3":                 (212, "Est.38 – HTE-N3",                                     "DIS-NOR-018"),
    "HTC-2XN3":               (215, "Est.41 – HTC-2XN3",                                   "DIS-NOR-018"),
    "HTC-N3":                 (213, "Est.39 – HTC-N3",                                     "DIS-NOR-018"),
    "LDE":                    (210, "Est.36 – LDE",                                        "DIS-NOR-018"),
    "M1-N2 FR Chaves":        (216, "Est.42 – M1-N2 Fim de Rede com Chaves Fusíveis",      "DIS-NOR-018"),
    "M1-N3":                  (211, "Est.37 – M1-N3",                                      "DIS-NOR-018"),
    "M1-N3 FR Chaves":        (217, "Est.43 – M1-N3 Fim de Rede com Chaves Fusíveis",      "DIS-NOR-018"),
    "M-N2BFR":                (355, "Est.125 – Derivação M-N2BFR",                         "DIS-NOR-018"),
    "M-N3B":                  (357, "Est.126 – Derivação M-N3B",                           "DIS-NOR-018"),
    "N1":                     (177, "Est.6 – N1",                                          "DIS-NOR-018"),
    "N1-TT":                  (182, "Est.11 – N1-TT",                                      "DIS-NOR-018"),
    "N3 (018)":               (178, "Est.7 – N3",                                          "DIS-NOR-018"),
    "N3-N3 (018)":            (180, "Est.9 – N3-N3",                                       "DIS-NOR-018"),
    "N3-TT":                  (183, "Est.12 – N3-TT",                                      "DIS-NOR-018"),
    "N3-TT-SOB":              (185, "Est.13 – N3-TT-SOB",                                  "DIS-NOR-018"),
    "N4":                     (179, "Est.8 – N4",                                          "DIS-NOR-018"),
    "N4 COM CRUZETA":         (202, "Est.28 – N4 com Cruzeta de Ferro",                    "DIS-NOR-018"),
    "N4-CFU":                 (186, "Est.14 – N4-CFU",                                     "DIS-NOR-018"),
    "N4-N3 (018)":            (181, "Est.10 – N4-N3",                                      "DIS-NOR-018"),
    "N4-N3-CFU":              (187, "Est.15 – N4-N3-CFU",                                  "DIS-NOR-018"),
    "PARA-RAIOS 2ºNÍV":       (196, "Est.24 – Para-raios em 2º Nível",                     "DIS-NOR-018"),
    "PT Est.M1":              (332, "Est.111 – Posto de Transformação Estrutura M1",        "DIS-NOR-018"),
    "PT Est.N3":              (334, "Est.112 – Posto de Transformação Estrutura N3",        "DIS-NOR-018"),
    "PT Est.N3 FimRede":      (336, "Est.113 – Posto de Transformação N3 Fim de Rede",     "DIS-NOR-018"),
    "PT Est.U1":              (348, "Est.120 – Posto de Transformação Estrutura U1",        "DIS-NOR-018"),
    "PT N3 2+ Clientes":      (279, "Est.79 – PT Ligação 2 ou Mais Clientes",              "DIS-NOR-018"),
    "PT N3 sem Chaves":       (275, "Est.77 – PT N3 sem Chaves",                           "DIS-NOR-018"),
    "PT N3 sem Chaves 2":     (277, "Est.78 – PT N3 sem Chaves (var.2)",                   "DIS-NOR-018"),
    "PT N3 com Chaves":       (273, "Est.76 – PT N3 com Chaves",                           "DIS-NOR-018"),
    "TE":                     (188, "Est.16 – TE",                                         "DIS-NOR-018"),
    "TE FIM REDE":            (205, "Est.31 – TE Fim de Rede",                             "DIS-NOR-018"),
    "U1":                     (172, "Est.1 – U1",                                          "DIS-NOR-018"),
    "U1-U3 c/Chaves":         (340, "Est.116 – U1-U3 Ramal com Chaves",                    "DIS-NOR-018"),
    "U1-U3 s/Chaves":         (339, "Est.115 – U1-U3 Ramal sem Chaves",                    "DIS-NOR-018"),
    "U2":                     (173, "Est.2 – U2",                                          "DIS-NOR-018"),
    "U3":                     (174, "Est.3 – U3",                                          "DIS-NOR-018"),
    "U3-3":                   (175, "Est.4 – U3-3",                                        "DIS-NOR-018"),
    "U4":                     (176, "Est.5 – U4",                                          "DIS-NOR-018"),
}

# ─────────────────────────────────────────────────────────────────
# BANCO DE NOTAS (Exemplos extraídos do novo PDF)
# ─────────────────────────────────────────────────────────────────
NOTAS_ESTRUTURAS = {
    "AT Condutor Ext (013)": [
        "A estrutura tipo AT Condutor Externo é utilizada para aterramento de condutor externo;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "AT Condutor Int (013)": [
        "A estrutura tipo AT Condutor Interno é utilizada para aterramento de condutor interno;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B3.CE3": [
        "A estrutura tipo B3.CE3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B3.CE3 SUI": [
        "A estrutura tipo B3.CE3 SUI é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica CF": [
        "A estrutura tipo Bifásica CF é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica Derivação": [
        "A estrutura tipo Bifásica Derivação é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica Para-raios": [
        "A estrutura tipo Bifásica Para-raios é utilizada para instalação de para-raios;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica TR Fim Rede": [
        "A estrutura tipo Bifásica TR Fim Rede é utilizada para instalação de transformadores em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica TR sem CF": [
        "A estrutura tipo Bifásica TR sem CF é utilizada para instalação de transformadores sem chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica TR sob Rede": [
        "A estrutura tipo Bifásica TR sob Rede é utilizada para instalação de transformadores sob a rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásicas Básicas": [
        "As estruturas tipo Bifásicas Básicas são utilizadas em redes bifásicas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Bifásica Transição": [
        "A estrutura tipo Bifásica Transição é utilizada em transições de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE1": [
        "A estrutura tipo CE1 é utilizada em tangentes e deflexões da rede até 6º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE1A": [
        "A estrutura tipo CE1A é utilizada, a cada 200 m de rede, em longos trechos com várias estruturas tipo CE1;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE1A-PU": [
        "A estrutura tipo CE1A-PU é utilizada, a cada 200 m de rede, em longos trechos com várias estruturas tipo CE1;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE1A-PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE1A."
    ],
    "CE2": [
        "A estrutura tipo CE2 é utilizada nos casos de deflexão da rede de 7º à 60º para cabos de seções 35 mm² e 70 mm² e 7º à 45º para cabos de seções 185 mm² e 240 mm²;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2 DS": [
        "A estrutura tipo CE2 DS é utilizada em derivações subterrâneas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2 PR": [
        "A estrutura tipo CE2 PR é utilizada para instalação de para-raios;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2 TR": [
        "A estrutura tipo CE2 TR é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-CE3": [
        "A estrutura tipo CE2-CE3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-CE3 CF": [
        "A estrutura tipo CE2-CE3 CF é utilizada em derivações de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-CE3 CF LP": [
        "A estrutura tipo CE2-CE3 CF LP é utilizada em derivações de rede com chaves fusíveis e para-raios;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-N3 CF": [
        "A estrutura tipo CE2-N3 CF é utilizada em derivações de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2-PU": [
        "A estrutura tipo CE2-PU é utilizada em tangentes e deflexões da rede até 6º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2.3": [
        "A estrutura tipo CE2.3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE2.CE3": [
        "A estrutura tipo CE2.CE3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3": [
        "A estrutura tipo CE3 é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3 DS": [
        "A estrutura tipo CE3 DS é utilizada em derivações subterrâneas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3 TR": [
        "A estrutura tipo CE3 TR é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3 TRSC": [
        "A estrutura tipo CE3 TRSC é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-CE3": [
        "A estrutura tipo CE3-CE3 é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-I": [
        "A estrutura tipo CE3-I é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-I SUI": [
        "A estrutura tipo CE3-I SUI é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE3-PU": [
        "A estrutura tipo CE3-PU é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE3-PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE3."
    ],
    "CE3PU-CE3PU": [
        "A estrutura tipo CE3PU-CE3PU é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE3PU-CE3PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE3-CE3."
    ],
    "CE4": [
        "A estrutura tipo CE4 é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 CF": [
        "A estrutura tipo CE4 CF é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 CF SAH": [
        "A estrutura tipo CE4 CF SAH é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 SUH": [
        "A estrutura tipo CE4 SUH é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 SUI": [
        "A estrutura tipo CE4 SUI é utilizada para instalação de chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4 TR": [
        "A estrutura tipo CE4 TR é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CE4-PU": [
        "A estrutura tipo CE4-PU é utilizada em fim de rede e em ângulos de deflexão de 60º a 90º;",
        "Esta estrutura deve ser utilizada preferencialmente em postes já instalados onde há necessidade de elevação do nível da rede primária, como por exemplo em circuitos duplos;",
        "Deve ser respeitada as distancias de segurança estabelecidas neste normativo;",
        "Esta estrutura não se aplica em redes de 34,5 kV.",
        "A Estrutura CE4-PU possibilita a elevar a altura da rede em 0,5 m quando comparada com a CE4."
    ],
    "CEJ1": [
        "A estrutura tipo CEJ1 é utilizada com o objetivo de afastar os condutores de edificações;",
        "A estrutura tipo CEJ1 não deve ser utilizada em postes de 200 daN quando a bitola dos condutores forem iguais ou superiores a 185 mm² para classe de tensão de 15 kV e iguais ou superiores a 70 mm² para classe de tensão de 36 kV;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CEJ1 SAH": [
        "A estrutura tipo CEJ1 SAH é utilizada com o objetivo de afastar os condutores de edificações;",
        "A estrutura tipo CEJ1 SAH não deve ser utilizada em postes de 200 daN quando a bitola dos condutores forem iguais ou superiores a 185 mm² para classe de tensão de 15 kV e iguais ou superiores a 70 mm² para classe de tensão de 36 kV;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CEJ2": [
        "A estrutura tipo CEJ2 é utilizada nos casos de deflexão da rede de 7º à 60º para cabos de seções 35 mm² e 70 mm² e 7º à 45º para cabos de seções 185 mm² e 240 mm²;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CEJ2 SAH": [
        "A estrutura tipo CEJ2 SAH é utilizada nos casos de deflexão da rede de 7º à 60º para cabos de seções 35 mm² e 70 mm² e 7º à 45º para cabos de seções 185 mm² e 240 mm²;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Monofásicas Básicas": [
        "As estruturas tipo Monofásicas Básicas são utilizadas em redes monofásicas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "Monofásicas Derivação": [
        "As estruturas tipo Monofásicas de Derivação são utilizadas em derivações de redes monofásicas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3.CE3": [
        "A estrutura tipo N3.CE3 é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3.CE3 SUH": [
        "A estrutura tipo N3.CE3 SUH é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3.CE3 SUI": [
        "A estrutura tipo N3.CE3 SUI é utilizada em transições de rede convencional para rede isolada;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    # ── DIS-NOR-014 ─────────────────────────────────────────────
    "AT Condutor Ext (014)": [
        "A estrutura tipo AT Condutor Externo é utilizada para aterramento de condutor externo;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "AT Condutor Int (014)": [
        "A estrutura tipo AT Condutor Interno é utilizada para aterramento de condutor interno;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CAB": [
        "A estrutura tipo CAB é utilizada para cruzamento aéreo multiplexado;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIT": [
        "A estrutura tipo FLABIT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIDM": [
        "A estrutura tipo FLABIDM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIDT": [
        "A estrutura tipo FLABIDT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLABIM": [
        "A estrutura tipo FLABIM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIM": [
        "A estrutura tipo FLBIM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIM NI": [
        "A estrutura tipo FLBIM NI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIT": [
        "A estrutura tipo FLBIT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "FLBIT NI": [
        "A estrutura tipo FLBIT NI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "IBI": [
        "A estrutura tipo IBI é utilizada para interligação nu/multiplexado;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "IT-R": [
        "A estrutura tipo IT-R é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ITF-R": [
        "A estrutura tipo ITF-R é utilizada para instalação de transformadores;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "LCM": [
        "A estrutura tipo LCM é utilizada para ligação de consumidores multiderivações;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SAB": [
        "A estrutura tipo SAB é utilizada para seccionamento aéreo;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SDBIM": [
        "A estrutura tipo SDBIM é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SDBIT": [
        "A estrutura tipo SDBIT é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SDANI": [
        "A estrutura tipo SDANI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SMBI": [
        "A estrutura tipo SMBI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "SPBI": [
        "A estrutura tipo SPBI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "STBI": [
        "A estrutura tipo STBI é utilizada em redes isoladas;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    # ── DIS-NOR-018 ─────────────────────────────────────────────
    "AT Descida Ext (018)": [
        "A estrutura tipo AT Descida Ext é utilizada para aterramento de descida externa;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "AT Descida Int (018)": [
        "A estrutura tipo AT Descida Int é utilizada para aterramento de descida interna;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B1": [
        "A estrutura tipo B1 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B3 (018)": [
        "A estrutura tipo B3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "B4": [
        "A estrutura tipo B4 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "CFU 1º NÍVEL": [
        "A estrutura tipo CFU 1º Nível é utilizada para chaves fusíveis em 1º nível;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ESTAI CONTRAPOSTE": [
        "A estrutura tipo ESTAI CONTRAPOSTE é utilizada para estaiamento de contraposte;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ESTAI NORMAL": [
        "A estrutura tipo ESTAI NORMAL é utilizada para estai em terreno normal;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "ESTAI ROCHA": [
        "A estrutura tipo ESTAI ROCHA é utilizada para estai em rochas e pântanos;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC": [
        "A estrutura tipo HTC é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC FIM REDE": [
        "A estrutura tipo HTC FIM REDE é utilizada em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE": [
        "A estrutura tipo HTE é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE FIM REDE": [
        "A estrutura tipo HTE FIM REDE é utilizada em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-1 Deriv N3": [
        "A estrutura tipo HTC-1 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-2 Deriv N3": [
        "A estrutura tipo HTC-2 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-1 Deriv N3": [
        "A estrutura tipo HTE-1 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-2 Deriv N3": [
        "A estrutura tipo HTE-2 Deriv N3 é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-2XN3": [
        "A estrutura tipo HTE-2XN3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTE-N3": [
        "A estrutura tipo HTE-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-2XN3": [
        "A estrutura tipo HTC-2XN3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "HTC-N3": [
        "A estrutura tipo HTC-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "LDE": [
        "A estrutura tipo LDE é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M1-N2 FR Chaves": [
        "A estrutura tipo M1-N2 FR Chaves é utilizada em fim de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M1-N3": [
        "A estrutura tipo M1-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M1-N3 FR Chaves": [
        "A estrutura tipo M1-N3 FR Chaves é utilizada em fim de rede com chaves fusíveis;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M-N2BFR": [
        "A estrutura tipo M-N2BFR é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "M-N3B": [
        "A estrutura tipo M-N3B é utilizada em derivações de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N1": [
        "A estrutura tipo N1 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N1-TT": [
        "A estrutura tipo N1-TT é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3 (018)": [
        "A estrutura tipo N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3-N3 (018)": [
        "A estrutura tipo N3-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3-TT": [
        "A estrutura tipo N3-TT é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N3-TT-SOB": [
        "A estrutura tipo N3-TT-SOB é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4": [
        "A estrutura tipo N4 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4 COM CRUZETA": [
        "A estrutura tipo N4 COM CRUZETA é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4-CFU": [
        "A estrutura tipo N4-CFU é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4-N3 (018)": [
        "A estrutura tipo N4-N3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "N4-N3-CFU": [
        "A estrutura tipo N4-N3-CFU é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PARA-RAIOS 2ºNÍV": [
        "A estrutura tipo PARA-RAIOS 2ºNÍV é utilizada para para-raios em 2º nível;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.M1": [
        "A estrutura tipo PT Est.M1 é utilizada para posto de transformação;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.N3": [
        "A estrutura tipo PT Est.N3 é utilizada para posto de transformação;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.N3 FimRede": [
        "A estrutura tipo PT Est.N3 FimRede é utilizada para posto de transformação em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT Est.U1": [
        "A estrutura tipo PT Est.U1 é utilizada para posto de transformação;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 2+ Clientes": [
        "A estrutura tipo PT N3 2+ Clientes é utilizada para ligação de 2 ou mais clientes;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 sem Chaves": [
        "A estrutura tipo PT N3 sem Chaves é utilizada para posto de transformação sem chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 sem Chaves 2": [
        "A estrutura tipo PT N3 sem Chaves 2 é utilizada para posto de transformação sem chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "PT N3 com Chaves": [
        "A estrutura tipo PT N3 com Chaves é utilizada para posto de transformação com chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "TE": [
        "A estrutura tipo TE é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "TE FIM REDE": [
        "A estrutura tipo TE FIM REDE é utilizada em fim de rede;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U1": [
        "A estrutura tipo U1 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U1-U3 c/Chaves": [
        "A estrutura tipo U1-U3 c/Chaves é utilizada em ramal com chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U1-U3 s/Chaves": [
        "A estrutura tipo U1-U3 s/Chaves é utilizada em ramal sem chaves;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U2": [
        "A estrutura tipo U2 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U3": [
        "A estrutura tipo U3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U3-3": [
        "A estrutura tipo U3-3 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
    "U4": [
        "A estrutura tipo U4 é utilizada em redes convencionais;",
        "Os postes DT (ph) e circular (pa) devem ser definidos conforme item 6.11 desta especificação."
    ],
}

CORES_NORMA = {
    "DIS-NOR-013": "#2fbf71",
    "DIS-NOR-014": "#4f8cff",
    "DIS-NOR-018": "#ff8a3d",
}

# ─────────────────────────────────────────────────────────────────
# FUNÇÕES
# ─────────────────────────────────────────────────────────────────

def _resolver_pdf_path(pdf_path: str) -> str:
    if os.path.exists(pdf_path):
        return pdf_path

    base_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    candidates = []

    if pdf_path:
        candidates.append(pdf_path)
        candidates.append(os.path.basename(pdf_path))

    candidates.extend([
        os.path.join(base_dir, "Estruturas_DIS-NOR-013_014_018.pdf"),
        os.path.join(base_dir, "disnors", "Estruturas_DIS-NOR-013_014_018.pdf"),
        os.path.join(base_dir, "..", "disnors", "Estruturas_DIS-NOR-013_014_018.pdf"),
        os.path.join(base_dir, "..", "disnors"),
    ])

    for candidate in candidates:
        if isinstance(candidate, str) and os.path.exists(candidate):
            if os.path.isdir(candidate):
                for root, _, files in os.walk(candidate):
                    for filename in files:
                        if filename.lower().endswith(".pdf"):
                            full_path = os.path.join(root, filename)
                            if "estruturas" in full_path.lower() or "dis-nor" in full_path.lower():
                                return full_path
            else:
                return candidate

    for root, _, files in os.walk(base_dir):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                full_path = os.path.join(root, filename)
                if "estruturas" in full_path.lower() or "dis-nor" in full_path.lower():
                    return full_path

    return pdf_path


@st.cache_data(show_spinner="Carregando desenho...")
def extrair_imagem(pdf_path: str, pagina: int, dpi: int = 150) -> bytes:
    resolved_pdf_path = _resolver_pdf_path(pdf_path)
    if not os.path.exists(resolved_pdf_path):
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    try:
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(resolved_pdf_path)
        try:
            page = pdf[pagina - 1]
            img = page.render(scale=dpi / 72).to_pil()
        finally:
            pdf.close()
    except Exception:
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix = os.path.join(tmpdir, "pag")
            subprocess.run(
                ["pdftoppm", "-jpeg", "-r", str(dpi),
                "-f", str(pagina), "-l", str(pagina),
                resolved_pdf_path, prefix],
                check=True, capture_output=True,
            )
            arquivos = sorted(glob.glob(f"{prefix}-*.jpg"))
            if not arquivos:
                raise FileNotFoundError("pdftoppm não gerou imagem.")
            img = Image.open(arquivos[0])

    w, h = img.size
    # Cortar cabeçalho (13% do topo)
    img = img.crop((0, int(h * 0.13), w, h))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_data
def load_normative_search_index():
    """Carrega o índice de busca dos normativos em cache."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "normatives_text.json"),
        os.path.join(os.getcwd(), "normatives_text.json"),
        "normatives_text.json",
    ]

    for json_path in candidates:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
    return None


def get_page_sequence_for_structure(structure_code: str, base_page: int):
    """Retorna as páginas a exibir para a estrutura selecionada."""
    if structure_code == "CE2.CE3":
        return [
            (49, "Poste tubular"),
            (48, "Poste DT"),
            (50, "Relação de materiais – DT e tubular"),
        ]
    return [
        (base_page, "Estrutura"),
        (base_page + 1, "Variação da estrutura"),
        (base_page + 2, "Relação de materiais"),
    ]

def format_normative_document_name(doc_name: str) -> str:
    """Retorna um rótulo limpo para o documento normativo."""
    name = str(doc_name or "").strip()
    if not name:
        return "Norma"

    match = re.search(r"(DIS-NOR-\d{3})", name, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    name = os.path.splitext(name)[0]
    name = name.replace("_", " ").replace("-", " - ")
    name = re.sub(r"\s+", " ", name).strip()
    return name


def search_keyword_in_normatives(keyword, normative_data, context_lines=2):
    """Busca uma palavra-chave nos textos dos normativos e retorna referências."""
    results = []
    if not keyword or not normative_data:
        return results

    variants = []
    raw = str(keyword).strip()
    if raw:
        variants.append(raw)
        variants.append(raw.replace("-", ""))
        variants.append(raw.replace(".", ""))
        variants.append(raw.replace(" ", ""))
        variants.append(raw.upper())
        variants.append(raw.lower())

    patterns = []
    for variant in dict.fromkeys(variants):
        if variant:
            patterns.append(re.escape(variant))

    if not patterns:
        patterns.append(re.escape(raw))

    for doc_name, pages_data in normative_data.items():
        for page_info in pages_data:
            page_content = page_info.get("content", "")
            page_number = page_info.get("page", "")
            lines = page_content.split('\n')

            for i, line in enumerate(lines):
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns):
                    start_index = max(0, i - context_lines)
                    end_index = min(len(lines), i + context_lines + 1)

                    context_text = []
                    for j in range(start_index, end_index):
                        context_text.append(lines[j].strip())

                    clean_context = " ".join(filter(None, context_text))
                    matched_sentences = []
                    for pattern in patterns:
                        matched_sentences.extend(re.findall(r'[^.!?]*?%s[^.!?]*?[.!?]' % pattern, clean_context, re.IGNORECASE))

                    for sentence in matched_sentences:
                        if sentence.strip():
                            results.append({
                                "document": doc_name,
                                "page": page_number,
                                "text": sentence.strip()
                            })

    unique_results = []
    seen = set()
    for result in results:
        key = (result["document"], result["page"], result["text"])
        if key not in seen:
            seen.add(key)
            unique_results.append(result)

    return unique_results

def extrair_notas_dinamicamente(pdf_path, pagina_inicio):
    """Tenta extrair notas do PDF próximo à página da estrutura."""
    import pdfplumber
    import re
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Procura na página do desenho e nas 3 seguintes
            for p_idx in range(pagina_inicio - 1, min(pagina_inicio + 3, len(pdf.pages))):
                page = pdf.pages[p_idx]
                text = page.extract_text()
                if not text: continue
                if "Notas:" in text or "Nota:" in text:
                    lines = text.split('\n')
                    start_collecting = False
                    found_notes = []
                    for line in lines:
                        if re.search(r'Nota(s)?:', line, re.IGNORECASE):
                            start_collecting = True
                            continue
                        if start_collecting:
                            match = re.match(r'^\s*(\d+)\.\s+(.*)', line)
                            if match:
                                found_notes.append(match.group(2).strip())
                            elif found_notes and line.strip():
                                if any(x in line for x in ["TÍTULO:", "CÓDIGO:", "APROVADOR:", "PÁG.:"]): continue
                                found_notes[-1] = found_notes[-1] + " " + line.strip()
                            elif found_notes and not line.strip():
                                break
                    if found_notes: return found_notes
    except:
        pass
    return None

# ─────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Estruturas Elétricas – Neoenergia Elektro",
    page_icon="⚡",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07131f 0%, #0f2236 45%, #16324d 100%);
        color: #f4f7fb;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stSidebar"] {
        background: rgba(7, 19, 31, 0.95);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .stButton > button {
        background: linear-gradient(90deg, #2fbf71, #4f8cff);
        color: white;
        border: none;
        border-radius: 8px;
    }
    .stButton > button:hover {
        opacity: 0.95;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ Estruturas Elétricas")
    st.caption("Neoenergia Elektro")
    st.divider()

    norma_filtro = st.selectbox(
        "Filtrar por norma",
        ["Todas", "DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"],
        index=0,
    )
    st.divider()

    if "estrutura_ativa" not in st.session_state:
        st.session_state["estrutura_ativa"] = None

    codigos_ordenados = sorted(ESTRUTURAS.keys())
    normas = ["DIS-NOR-013", "DIS-NOR-014", "DIS-NOR-018"]
    for norma in normas:
        if norma_filtro != "Todas" and norma_filtro != norma: continue
        cor = CORES_NORMA[norma]
        st.markdown(f'<div style="color:{cor};font-weight:bold;font-size:12px;margin-top:6px;margin-bottom:4px;">{norma}</div>', unsafe_allow_html=True)
        for codigo in codigos_ordenados:
            pag, titulo, n = ESTRUTURAS[codigo]
            if n != norma: continue
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
    pagina, titulo, norma = ESTRUTURAS[selecionada]
    cor = CORES_NORMA[norma]

    st.markdown(f'<h2 style="color:{cor};margin-bottom:0.2rem;">{titulo}</h2>', unsafe_allow_html=True)
    st.markdown(f'<span style="background:{cor};color:white;padding:3px 10px;border-radius:999px;font-size:13px;">{norma}</span>', unsafe_allow_html=True)
    st.write("")

    st.markdown("### 🧩 Desenhos e relação de materiais")
    st.caption("A instalação atual prioriza o poste tubular; o poste DT é mostrado apenas como referência de manutenção.")

    page_sequence = get_page_sequence_for_structure(selecionada, pagina)
    cols = st.columns(3)

    for col, (page_no, titulo_pagina) in zip(cols, page_sequence):
        with col:
            st.markdown(f"#### {titulo_pagina}")
            try:
                img_bytes = extrair_imagem(PDF_PATH, page_no, DPI)
                st.image(img_bytes, use_container_width=True, output_format="PNG")
            except Exception as e:
                st.info(f"Página {page_no} indisponível no PDF: {e}")

    st.divider()
    st.markdown("### ℹ️ Informações da estrutura")
    st.write(f"Estrutura selecionada: **{selecionada}**")
    st.write(f"Norma: **{norma}**")
    st.write("Sempre consulte as DIS-NORs e verifique as normas.")

    st.divider()
    st.markdown("### 📑 Páginas nas normas correspondentes a essa estrutura")
    normative_data = load_normative_search_index()

    if normative_data:
        references = search_keyword_in_normatives(selecionada, normative_data)
        if references:
            refs_by_doc = {}
            for ref in references:
                refs_by_doc.setdefault(ref["document"], []).append(ref)

            for doc_name in sorted(refs_by_doc.keys()):
                items = refs_by_doc[doc_name]
                seen_items = set()
                unique_items = []
                for item in items:
                    key = (item["page"], item["text"].strip())
                    if key not in seen_items:
                        seen_items.add(key)
                        unique_items.append(item)

                unique_pages = sorted({str(item["page"]) for item in unique_items})
                pages = ", ".join(unique_pages)
                st.markdown(f"- **{format_normative_document_name(doc_name)}** — páginas: {pages}")
                for item in unique_items:
                    snippet = item["text"].strip()
                    if snippet:
                        st.caption(f"• Pág. {item['page']} — {snippet}")
        else:
            st.info("Nenhuma página de referência encontrada para esta estrutura.")
    else:
        st.info("Índice de normativos indisponível.")


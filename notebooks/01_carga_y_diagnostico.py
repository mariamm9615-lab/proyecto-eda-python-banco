"""
01 - Carga y diagnóstico inicial
=================================
Primer paso del análisis exploratorio: cargar los dos conjuntos de datos
originales tal como se han recibido (sin modificar nada todavía) y
diagnosticar qué problemas de calidad tienen antes de decidir cómo
limpiarlos en el siguiente script.

Datasets de partida (carpeta data/raw/):
    - bank-additional.csv   -> datos de la campaña de marketing telefónico.
    - customer-details.xlsx -> datos demográficos de los clientes (3 hojas,
                                una por año de alta: 2012, 2013, 2014).

Este script no escribe ningún archivo nuevo: solo imprime por pantalla el
diagnóstico, que es el que ha guiado las decisiones tomadas en
02_limpieza_transformacion.py.
"""

import pandas as pd

RUTA_BANK = "../data/raw/bank-additional.csv"
RUTA_CUSTOMER = "../data/raw/customer-details.xlsx"


def cargar_bank(ruta: str) -> pd.DataFrame:
    """Carga el CSV de la campaña de marketing.

    El separador real del archivo es la coma (a pesar de la extensión
    y de que varios proyectos similares usan ';'); la primera columna,
    sin nombre, es solo un índice de fila que no aporta información
    (no se usa como índice todavía para poder inspeccionarla).
    """
    return pd.read_csv(ruta, sep=",")


def cargar_customer(ruta: str) -> pd.DataFrame:
    """Carga las 3 hojas del Excel de clientes y las une en un único
    DataFrame, añadiendo de qué hoja (año de alta declarado) procede
    cada fila.
    """
    hojas = pd.read_excel(ruta, sheet_name=None)  # dict {nombre_hoja: df}
    partes = []
    for nombre_hoja, df_hoja in hojas.items():
        df_hoja = df_hoja.copy()
        df_hoja["hoja_origen"] = nombre_hoja
        partes.append(df_hoja)
    return pd.concat(partes, ignore_index=True)


def diagnostico(df: pd.DataFrame, nombre: str) -> None:
    print(f"\n{'=' * 70}\nDIAGNÓSTICO: {nombre}\n{'=' * 70}")
    print(f"Filas x columnas: {df.shape[0]} x {df.shape[1]}")
    print("\nTipos de datos:")
    print(df.dtypes)
    print("\nValores nulos por columna:")
    nulos = df.isnull().sum()
    porcentaje = (nulos / len(df) * 100).round(2)
    resumen_nulos = pd.DataFrame({"nulos": nulos, "% del total": porcentaje})
    print(resumen_nulos[resumen_nulos["nulos"] > 0])
    print(f"\nFilas totalmente duplicadas: {df.duplicated().sum()}")


def main() -> None:
    bank = cargar_bank(RUTA_BANK)
    customer = cargar_customer(RUTA_CUSTOMER)

    diagnostico(bank, "bank-additional.csv (datos de campaña)")
    diagnostico(customer, "customer-details.xlsx (datos demográficos)")

    print(f"\n{'=' * 70}\nOBSERVACIONES CLAVE DEL DIAGNÓSTICO\n{'=' * 70}")
    print(
        "- La primera columna de bank-additional.csv no tiene nombre y es un\n"
        "  simple índice de fila (0..N); se descarta en la limpieza porque ya\n"
        "  existe 'id_' como identificador único real.\n"
        "- 'cons.price.idx', 'cons.conf.idx', 'euribor3m' y 'nr.employed' se\n"
        "  leen como texto porque usan la coma como separador decimal\n"
        "  (ej. '93,994'); hay que convertirlas a número.\n"
        "- 'marital' y 'poutcome' están en MAYÚSCULAS mientras que 'job',\n"
        "  'education', 'contact' e 'y' están en minúsculas: falta de\n"
        "  consistencia de formato que se corrige en la limpieza.\n"
        "- 'date' es un texto con el mes en español ('2-agosto-2019'); se\n"
        "  convierte a fecha real y de ahí se derivan 'contact_month' y\n"
        "  'contact_year', tal como pide el enunciado.\n"
        "- 'default', 'housing' y 'loan' son indicadores 0/1 con bastantes\n"
        "  nulos (sobre todo 'default', ~21%); se recodifican como\n"
        "  'si'/'no'/'desconocido' en vez de imputar un valor inventado.\n"
        "- 'pdays' usa el valor centinela 999 para \"nunca contactado antes\";\n"
        "  se mantiene el valor original y se añade una columna booleana\n"
        "  'contactado_previamente' para no tener que recordar ese código.\n"
        "- El identificador 'id_' de bank-additional.csv coincide al 100%\n"
        "  con la columna 'ID' de customer-details.xlsx (43.000 valores en\n"
        "  común); customer-details.xlsx tiene 170 clientes de más que no\n"
        "  participaron en esta campaña, así que no aparecerán en el\n"
        "  dataset final combinado (se documenta en el README).\n"
        "- Las columnas 'latitude'/'longitude' tienen coordenadas propias de\n"
        "  Estados Unidos, no de Portugal (el enunciado dice que el banco es\n"
        "  portugués); es un indicio de que el dataset ha sido anonimizado /\n"
        "  aleatorizado con fines didácticos, así que no se usan para sacar\n"
        "  conclusiones geográficas reales, solo se conservan como vienen."
    )


if __name__ == "__main__":
    main()

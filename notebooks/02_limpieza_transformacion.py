"""
02 - Limpieza y transformación
================================
A partir del diagnóstico de 01_carga_y_diagnostico.py, este script limpia
y transforma los dos datasets originales y los combina en un único
dataset final, listo para el análisis descriptivo y la visualización.

Genera tres archivos en data/processed/:
    - bank_marketing_limpio.csv   -> campaña de marketing, limpia.
    - customer_details_limpio.csv -> datos demográficos, limpios.
    - dataset_final.csv           -> combinación de los dos anteriores
                                      por cliente (id_ / ID).
"""

import numpy as np
import pandas as pd

RUTA_BANK = "../data/raw/bank-additional.csv"
RUTA_CUSTOMER = "../data/raw/customer-details.xlsx"

SALIDA_BANK = "../data/processed/bank_marketing_limpio.csv"
SALIDA_CUSTOMER = "../data/processed/customer_details_limpio.csv"
SALIDA_FINAL = "../data/processed/dataset_final.csv"

MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

# Columnas que llegan como texto por usar la coma como separador decimal.
COLUMNAS_DECIMAL_COMA = ["cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]

# Columnas 0/1 (con nulos) que en realidad son indicadores sí/no/desconocido.
COLUMNAS_SI_NO = ["default", "housing", "loan"]


def parsear_fecha_es(texto: str):
    """Convierte 'D-mes_en_español-AAAA' en un Timestamp real.

    Devuelve NaT si el texto es nulo o no tiene el formato esperado, en
    vez de lanzar una excepción, para no interrumpir la limpieza por
    unas pocas fechas mal formadas.
    """
    if pd.isna(texto):
        return pd.NaT
    try:
        dia, mes_texto, anio = texto.strip().split("-")
        mes = MESES_ES[mes_texto.lower()]
        return pd.Timestamp(year=int(anio), month=mes, day=int(dia))
    except (ValueError, KeyError):
        return pd.NaT


def limpiar_bank(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta, sep=",")

    # La primera columna (sin nombre) es un índice de fila redundante:
    # ya existe 'id_' como identificador único real.
    columnas_sin_nombre = [c for c in df.columns if c.startswith("Unnamed")]
    df = df.drop(columns=columnas_sin_nombre)

    # --- Tipos numéricos con coma decimal -> punto decimal -----------------
    for col in COLUMNAS_DECIMAL_COMA:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ".", regex=False),
            errors="coerce",
        )

    # --- Consistencia de mayúsculas/minúsculas en texto categórico --------
    columnas_categoricas = ["job", "marital", "education", "contact", "poutcome", "y"]
    for col in columnas_categoricas:
        df[col] = df[col].str.strip().str.lower()

    # --- Fechas: texto en español -> fecha real + columnas derivadas ------
    df["date"] = df["date"].apply(parsear_fecha_es)
    df["contact_month"] = df["date"].dt.month
    df["contact_year"] = df["date"].dt.year

    # --- Indicadores 0/1 con muchos nulos -> categoría explícita ----------
    # No se imputa un 0 o un 1 "inventado": se deja constancia de que el
    # dato no se conoce, en vez de sesgar el análisis.
    for col in COLUMNAS_SI_NO:
        df[col] = df[col].map({1.0: "si", 0.0: "no"}).fillna("desconocido")

    # --- Categorías de texto con nulos -> 'desconocido' --------------------
    for col in ["job", "marital", "education"]:
        df[col] = df[col].fillna("desconocido")

    # --- pdays: además del valor original (centinela 999 = "nunca
    # contactado antes"), se añade una columna booleana legible ------------
    df["contactado_previamente"] = df["pdays"] != 999

    # --- Edad: imputación por mediana agrupada por profesión ---------------
    # Se documenta con una columna booleana qué filas llevan una edad
    # estimada, en vez de mezclarla sin más con los datos reales.
    df["edad_imputada"] = df["age"].isna()
    mediana_por_job = df.groupby("job")["age"].transform("median")
    df["age"] = df["age"].fillna(mediana_por_job)
    df["age"] = df["age"].fillna(df["age"].median())  # red de seguridad si algún job no tuviera ninguna edad conocida
    df["age"] = df["age"].round().astype(int)

    # --- Indicadores macroeconómicos: pocos nulos, se imputan con la
    # mediana general de cada indicador ------------------------------------
    for col in COLUMNAS_DECIMAL_COMA:
        df[col] = df[col].fillna(df[col].median())

    # --- Sin duplicados exactos ni duplicados por identificador ------------
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="id_", keep="first")

    # --- Renombrar id_ a un nombre más cómodo para el merge -----------------
    df = df.rename(columns={"id_": "id_cliente"})

    return df


def limpiar_customer(ruta: str) -> pd.DataFrame:
    hojas = pd.read_excel(ruta, sheet_name=None)
    partes = []
    for nombre_hoja, df_hoja in hojas.items():
        df_hoja = df_hoja.copy()
        df_hoja["anio_hoja_origen"] = int(nombre_hoja)
        partes.append(df_hoja)
    df = pd.concat(partes, ignore_index=True)

    columnas_sin_nombre = [c for c in df.columns if c.startswith("Unnamed")]
    df = df.drop(columns=columnas_sin_nombre)

    df = df.rename(columns={
        "ID": "id_cliente",
        "Income": "ingresos_anuales",
        "Kidhome": "ninos_en_hogar",
        "Teenhome": "adolescentes_en_hogar",
        "Dt_Customer": "fecha_alta_cliente",
        "NumWebVisitsMonth": "visitas_web_mensuales",
    })

    # Comprobación de calidad: el año de la hoja debe coincidir con el año
    # real de la fecha de alta. Si no coincidiera en algún caso, se avisa
    # por pantalla en vez de fallar silenciosamente.
    discrepancias = (df["fecha_alta_cliente"].dt.year != df["anio_hoja_origen"]).sum()
    if discrepancias:
        print(f"Aviso: {discrepancias} filas con año de hoja distinto al de fecha_alta_cliente.")
    df = df.drop(columns="anio_hoja_origen")

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="id_cliente", keep="first")

    return df


def combinar(bank: pd.DataFrame, customer: pd.DataFrame) -> pd.DataFrame:
    """Combina los dos datasets por cliente.

    Se usa 'left' con bank como tabla base porque cada fila de bank es un
    contacto real de la campaña (que es el objeto de este análisis); los
    170 clientes de customer-details.xlsx que no aparecen en ninguna
    campaña quedan fuera a propósito (se documentan en el README).
    """
    return bank.merge(customer, on="id_cliente", how="left", validate="one_to_one")


def main() -> None:
    bank = limpiar_bank(RUTA_BANK)
    customer = limpiar_customer(RUTA_CUSTOMER)
    final = combinar(bank, customer)

    bank.to_csv(SALIDA_BANK, index=False)
    customer.to_csv(SALIDA_CUSTOMER, index=False)
    final.to_csv(SALIDA_FINAL, index=False)

    print("Limpieza completada.")
    print(f"  bank_marketing_limpio.csv   -> {bank.shape}")
    print(f"  customer_details_limpio.csv -> {customer.shape}")
    print(f"  dataset_final.csv           -> {final.shape}")
    print("\nNulos restantes en dataset_final.csv:")
    print(final.isnull().sum()[final.isnull().sum() > 0])


if __name__ == "__main__":
    main()

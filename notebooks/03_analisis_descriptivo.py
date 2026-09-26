"""
03 - Análisis descriptivo
==========================
Estadística descriptiva sobre el dataset ya limpio (dataset_final.csv):
medidas de tendencia central y dispersión, correlaciones y agregaciones
por grupo (tasa de suscripción según distintas variables).

Genera un resumen en texto (resumen_estadistico.txt) y una tabla de
correlaciones (correlaciones.csv) dentro de data/processed/, que se
reutilizan después en el informe del README y en la visualización.
"""

import pandas as pd

RUTA_FINAL = "../data/processed/dataset_final.csv"
SALIDA_RESUMEN = "../data/processed/resumen_estadistico.txt"
SALIDA_CORRELACIONES = "../data/processed/correlaciones.csv"

COLUMNAS_NUMERICAS = [
    "age", "duration", "campaign", "pdays", "previous",
    "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
    "ingresos_anuales", "ninos_en_hogar", "adolescentes_en_hogar", "visitas_web_mensuales",
]


def tasa_suscripcion_por(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Nº de clientes, suscripciones y % de éxito agrupado por 'columna'.

    Función reutilizable para no repetir la misma agregación groupby +
    mean/count una vez por cada variable categórica que se quiera mirar.
    """
    resumen = (
        df.groupby(columna)["y_binaria"]
        .agg(clientes="count", suscripciones="sum")
        .assign(tasa_suscripcion_pct=lambda d: (d["suscripciones"] / d["clientes"] * 100).round(2))
        .sort_values("tasa_suscripcion_pct", ascending=False)
    )
    return resumen


def bloque(texto: str, ancho: int = 70) -> str:
    return f"\n{'=' * ancho}\n{texto}\n{'=' * ancho}"


def main() -> None:
    df = pd.read_csv(RUTA_FINAL)
    df["y_binaria"] = (df["y"] == "yes").astype(int)

    lineas = []

    lineas.append(bloque("ESTADÍSTICA DESCRIPTIVA — VARIABLES NUMÉRICAS"))
    lineas.append(df[COLUMNAS_NUMERICAS].describe().T.round(2).to_string())

    lineas.append(bloque("VARIABLE OBJETIVO (y): ¿SUSCRIBIÓ EL DEPÓSITO?"))
    conteo_y = df["y"].value_counts()
    porcentaje_y = (df["y"].value_counts(normalize=True) * 100).round(2)
    lineas.append(pd.DataFrame({"clientes": conteo_y, "% del total": porcentaje_y}).to_string())
    lineas.append(
        "\nEl dataset está desbalanceado: solo "
        f"{porcentaje_y['yes']}% de los clientes contactados suscribió el depósito."
    )

    for columna in ["job", "marital", "education", "contact", "poutcome", "housing", "loan", "default"]:
        lineas.append(bloque(f"TASA DE SUSCRIPCIÓN POR '{columna.upper()}'"))
        lineas.append(tasa_suscripcion_por(df, columna).to_string())

    lineas.append(bloque("TASA DE SUSCRIPCIÓN POR TRAMO DE EDAD"))
    tramos_edad = pd.cut(
        df["age"],
        bins=[0, 25, 35, 45, 55, 65, 100],
        labels=["<=25", "26-35", "36-45", "46-55", "56-65", "66+"],
    )
    lineas.append(tasa_suscripcion_por(df.assign(tramo_edad=tramos_edad), "tramo_edad").to_string())

    lineas.append(bloque("TASA DE SUSCRIPCIÓN POR MES DE CONTACTO"))
    lineas.append(tasa_suscripcion_por(df.dropna(subset=["contact_month"]), "contact_month").to_string())

    lineas.append(bloque("TASA DE SUSCRIPCIÓN POR NÚMERO DE HIJOS EN EL HOGAR"))
    lineas.append(tasa_suscripcion_por(df, "ninos_en_hogar").to_string())

    lineas.append(bloque("MATRIZ DE CORRELACIÓN (variables numéricas + objetivo)"))
    correlaciones = df[COLUMNAS_NUMERICAS + ["y_binaria"]].corr().round(3)
    lineas.append(correlaciones.to_string())
    correlaciones.to_csv(SALIDA_CORRELACIONES)

    lineas.append(bloque("CORRELACIONES MÁS FUERTES CON LA VARIABLE OBJETIVO (y_binaria)"))
    correlacion_con_objetivo = (
        correlaciones["y_binaria"]
        .drop("y_binaria")
        .sort_values(key=abs, ascending=False)
    )
    lineas.append(correlacion_con_objetivo.to_string())

    texto_final = "\n".join(lineas)
    with open(SALIDA_RESUMEN, "w", encoding="utf-8") as f:
        f.write(texto_final)

    print(texto_final)
    print(f"\n\nResumen guardado en {SALIDA_RESUMEN}")
    print(f"Correlaciones guardadas en {SALIDA_CORRELACIONES}")


if __name__ == "__main__":
    main()

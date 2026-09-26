"""
04 - Visualización
====================
Genera los gráficos del análisis exploratorio a partir del dataset ya
limpio (dataset_final.csv) y los guarda como imágenes PNG en la carpeta
graficos/, para poder incluirlos en el README sin depender de que
alguien vuelva a ejecutar el código.
"""

import matplotlib
matplotlib.use("Agg")  # backend sin interfaz gráfica, para poder ejecutarlo en cualquier entorno
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

RUTA_FINAL = "../data/processed/dataset_final.csv"
CARPETA_GRAFICOS = "../graficos"

sns.set_theme(style="whitegrid")
PALETA = "viridis"


def guardar(fig, nombre_archivo: str) -> None:
    ruta = f"{CARPETA_GRAFICOS}/{nombre_archivo}"
    fig.tight_layout()
    fig.savefig(ruta, dpi=130)
    plt.close(fig)
    print(f"Guardado: {ruta}")


def grafico_distribucion_objetivo(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    conteo = df["y"].value_counts()
    ax.bar(conteo.index, conteo.values, color=["#4C72B0", "#DD8452"])
    for i, valor in enumerate(conteo.values):
        ax.text(i, valor + 400, f"{valor:,}\n({valor / len(df):.1%})", ha="center")
    ax.set_title("¿El cliente suscribió el depósito a plazo? (variable objetivo)")
    ax.set_xlabel("y")
    ax.set_ylabel("Número de clientes")
    guardar(fig, "01_distribucion_objetivo.png")


def grafico_distribucion_edad(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=df, x="age", hue="y", multiple="stack", bins=30, palette=PALETA, ax=ax)
    ax.set_title("Distribución de la edad, por resultado de la campaña")
    ax.set_xlabel("Edad")
    ax.set_ylabel("Número de clientes")
    guardar(fig, "02_distribucion_edad.png")


def grafico_tasa_por_job(df: pd.DataFrame) -> None:
    resumen = (
        df.groupby("job")["y_binaria"].mean().mul(100).sort_values(ascending=False)
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=resumen.values, y=resumen.index, hue=resumen.index, palette=PALETA, legend=False, ax=ax)
    ax.set_title("Tasa de suscripción por profesión")
    ax.set_xlabel("Tasa de suscripción (%)")
    ax.set_ylabel("Profesión")
    guardar(fig, "03_tasa_suscripcion_por_job.png")


def grafico_duracion_por_objetivo(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.boxplot(data=df, x="y", y="duration", hue="y", palette=PALETA, legend=False, ax=ax)
    ax.set_title("Duración de la llamada según si suscribió o no")
    ax.set_xlabel("y")
    ax.set_ylabel("Duración de la llamada (segundos)")
    ax.set_ylim(0, df["duration"].quantile(0.99))  # recorta el eje para que se vea bien (hay valores extremos)
    guardar(fig, "04_duracion_por_objetivo.png")


def grafico_correlaciones(df: pd.DataFrame) -> None:
    columnas = [
        "age", "duration", "campaign", "pdays", "previous",
        "emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed",
        "ingresos_anuales", "visitas_web_mensuales", "y_binaria",
    ]
    correlaciones = df[columnas].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlaciones, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Matriz de correlación entre variables numéricas")
    guardar(fig, "05_matriz_correlacion.png")


def grafico_tasa_por_contacto_previo(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    resumen = df.groupby("poutcome")["y_binaria"].mean().mul(100).sort_values(ascending=False)
    sns.barplot(x=resumen.index, y=resumen.values, hue=resumen.index, palette=PALETA, legend=False, ax=ax)
    ax.set_title("Tasa de suscripción según el resultado de la campaña anterior")
    ax.set_xlabel("Resultado de la campaña anterior (poutcome)")
    ax.set_ylabel("Tasa de suscripción (%)")
    guardar(fig, "06_tasa_por_poutcome.png")


def grafico_ingresos_por_objetivo(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.kdeplot(data=df, x="ingresos_anuales", hue="y", fill=True, common_norm=False, palette=PALETA, ax=ax)
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_title("Distribución de ingresos anuales, por resultado de la campaña")
    ax.set_xlabel("Ingresos anuales")
    guardar(fig, "07_ingresos_por_objetivo.png")


def grafico_tasa_por_mes(df: pd.DataFrame) -> None:
    resumen = (
        df.dropna(subset=["contact_month"])
        .groupby("contact_month")["y_binaria"].mean().mul(100)
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(resumen.index, resumen.values, marker="o", color="#4C72B0")
    ax.set_xticks(range(1, 13))
    ax.set_title("Tasa de suscripción por mes de contacto")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Tasa de suscripción (%)")
    guardar(fig, "08_tasa_por_mes.png")


def main() -> None:
    df = pd.read_csv(RUTA_FINAL)
    df["y_binaria"] = (df["y"] == "yes").astype(int)

    grafico_distribucion_objetivo(df)
    grafico_distribucion_edad(df)
    grafico_tasa_por_job(df)
    grafico_duracion_por_objetivo(df)
    grafico_correlaciones(df)
    grafico_tasa_por_contacto_previo(df)
    grafico_ingresos_por_objetivo(df)
    grafico_tasa_por_mes(df)

    print("\nTodos los gráficos se han generado correctamente.")


if __name__ == "__main__":
    main()

# 🏦 Análisis Exploratorio de Datos — Campaña de Marketing de un Banco Portugués

Análisis exploratorio (EDA) en **Python** de una campaña de marketing telefónico de un banco, combinando los datos de la campaña con datos demográficos de los clientes: limpieza y transformación, análisis descriptivo, visualización e informe de hallazgos.

> Proyecto del Bootcamp de Data & Analytics — Módulo *Python for Data*.

---

## 📝 Descripción del proyecto

El objetivo es realizar un análisis exploratorio completo sobre los datos de una campaña de marketing directo (llamadas telefónicas) de un banco, cuyo producto era un depósito a plazo fijo, cubriendo los cuatro puntos exigidos por el enunciado:

1. **Transformación y limpieza de los datos.**
2. **Análisis descriptivo de los datos.**
3. **Visualización de los datos.**
4. **Informe explicativo del análisis** (más abajo, en "Resultados y conclusiones").

Todo el proceso se ha resuelto en **Python**, usando **Pandas** para la manipulación de datos y **Matplotlib/Seaborn** para las visualizaciones.

### Datasets de partida

- **`bank-additional.csv`** (43.000 filas): un registro por cada llamada de la campaña, con datos del cliente (edad, profesión, estado civil, educación...), datos de la propia llamada (duración, número de contactos...), indicadores macroeconómicos del momento (`emp.var.rate`, `euribor3m`...) y la variable objetivo `y` (si el cliente suscribió el depósito o no).
- **`customer-details.xlsx`** (43.170 filas, en 3 hojas — una por año de alta del cliente: 2012/2013/2014): datos demográficos y de comportamiento de compra de los clientes (ingresos anuales, hijos/adolescentes en el hogar, visitas mensuales a la web, fecha de alta).

Ambos datasets comparten un identificador de cliente (`id_` / `ID`) que permite combinarlos en un único dataset para el análisis.

---

## 🗂️ Estructura del proyecto

```
├── README.md
├── data/
│   ├── raw/                          <- datos originales, sin ninguna modificación
│   │   ├── bank-additional.csv
│   │   └── customer-details.xlsx
│   └── processed/                    <- datos ya limpios/transformados
│       ├── bank_marketing_limpio.csv
│       ├── customer_details_limpio.csv
│       ├── dataset_final.csv         <- dataset combinado, usado en el análisis
│       ├── correlaciones.csv
│       └── resumen_estadistico.txt
├── notebooks/                        <- todo el código del análisis, paso a paso
│   ├── 01_carga_y_diagnostico.py
│   ├── 02_limpieza_transformacion.py
│   ├── 03_analisis_descriptivo.py
│   └── 04_visualizacion.py
└── graficos/                         <- gráficos generados por 04_visualizacion.py
    ├── 01_distribucion_objetivo.png
    ├── 02_distribucion_edad.png
    ├── 03_tasa_suscripcion_por_job.png
    ├── 04_duracion_por_objetivo.png
    ├── 05_matriz_correlacion.png
    ├── 06_tasa_por_poutcome.png
    ├── 07_ingresos_por_objetivo.png
    └── 08_tasa_por_mes.png
```

---

## ⚙️ Instalación y requisitos

Se necesita **Python 3.9 o superior** con las siguientes librerías: `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl` (esta última solo para leer el Excel).

```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

Los scripts de `notebooks/` están numerados y pensados para ejecutarse en orden, **desde dentro de la propia carpeta `notebooks/`** (usan rutas relativas del tipo `../data/...`):

```bash
cd notebooks
python3 01_carga_y_diagnostico.py       # diagnóstico inicial (no genera archivos, solo lo imprime)
python3 02_limpieza_transformacion.py   # limpia y combina los datos -> data/processed/
python3 03_analisis_descriptivo.py      # estadística descriptiva  -> data/processed/resumen_estadistico.txt
python3 04_visualizacion.py             # genera los gráficos      -> graficos/
```

Cada script se ha ejecutado y verificado de principio a fin sin errores antes de entregar el proyecto; `data/processed/` y `graficos/` ya se entregan generados, así que no es obligatorio volver a ejecutar nada para revisar los resultados.

---

## 📈 Resultados y conclusiones (informe del análisis)

### 1. Transformación y limpieza de los datos

Antes de analizar nada se diagnosticaron y corrigieron los siguientes problemas (detalle completo, con las cifras exactas, en `notebooks/01_carga_y_diagnostico.py` y `02_limpieza_transformacion.py`):

- **Formato numérico inconsistente:** `cons.price.idx`, `cons.conf.idx`, `euribor3m` y `nr.employed` llegaban como texto porque usaban la coma como separador decimal (`"93,994"`); se convirtieron a número.
- **Mayúsculas/minúsculas inconsistentes:** `marital` y `poutcome` venían en MAYÚSCULAS mientras el resto de columnas de texto estaban en minúsculas; se normalizó todo a minúsculas.
- **Fechas en español como texto:** la columna `date` (p. ej. `"2-agosto-2019"`) se convirtió a una fecha real, de la que se derivaron `contact_month` y `contact_year`, tal como pedía el enunciado.
- **Valores faltantes:**
  - `age` (11,9% de nulos) se imputó con la mediana de edad **de cada profesión** (más preciso que una mediana global), dejando constancia en una columna booleana `edad_imputada` de qué filas llevan una edad estimada.
  - `job`, `marital` y `education` (entre 0,2% y 4,2% de nulos) se recodificaron como categoría `"desconocido"` en vez de eliminarse, para no perder esas filas.
  - `default`, `housing` y `loan` eran indicadores 0/1 con bastantes huecos (`default` tenía un 21% de nulos); se recodificaron como `"si"` / `"no"` / `"desconocido"`, sin inventar un valor donde no se conocía.
  - Los cuatro indicadores macroeconómicos (entre 0% y 21,5% de nulos) se imputaron con la mediana de cada indicador.
  - `date` (0,6% de nulos) se dejó sin fecha (no se pudo derivar `contact_month`/`contact_year` en esas filas); es un porcentaje pequeño y no afecta al resto del análisis.
- **Columna sobrante:** la primera columna de `bank-additional.csv`, sin nombre, era solo un índice de fila; se eliminó porque ya existe `id_` como identificador único real.
- **Sin filas duplicadas** en ninguno de los dos datasets (se comprobó explícitamente).
- **Transformación derivada:** se añadió `contactado_previamente` (booleano) a partir de `pdays`, ya que ese campo usa el valor "centinela" `999` para indicar "nunca contactado antes" — una forma más legible de trabajar con ese dato.
- **Combinación de datasets:** se unieron `bank-additional.csv` y `customer-details.xlsx` por el identificador de cliente. El 100% de los clientes de la campaña (43.000) tienen su ficha demográfica; `customer-details.xlsx` tiene 170 clientes de más que nunca fueron contactados en esta campaña, así que quedan fuera del dataset combinado (no aportan nada a un análisis de la campaña).
- **Dato curioso detectado:** las columnas `latitude`/`longitude` del CSV tienen coordenadas propias de Estados Unidos, no de Portugal (el enunciado dice que el banco es portugués), y los indicadores macroeconómicos no son coherentes día a día. Es un indicio de que el dataset ha sido aleatorizado con fines didácticos; por eso no se han usado para sacar ninguna conclusión geográfica real, solo se han conservado tal cual venían.

### 2 y 3. Análisis descriptivo y visualización — hallazgos principales

*(detalle numérico completo en `data/processed/resumen_estadistico.txt`; gráficos completos en `graficos/`)*

- **La campaña tiene una tasa de éxito baja y el dataset está desbalanceado:** solo el **11,3%** de los 43.000 clientes contactados suscribió el depósito (`graficos/01_distribucion_objetivo.png`).
- **La duración de la llamada es, con diferencia, la variable más relacionada con el éxito** (correlación de 0,40 con la variable objetivo): las llamadas que terminan en suscripción duran claramente más de media (`graficos/04_duracion_por_objetivo.png`). Es un resultado esperable — una llamada larga implica que el cliente sigue interesado — pero también un aviso importante: la duración solo se conoce **después** de hacer la llamada, así que no sirve para decidir a quién llamar de antemano.
- **La profesión importa mucho:** los **jubilados** (25,2%) y **estudiantes** (31,3%) suscriben muchas más veces que la media, frente a `blue-collar` (6,9%) o `services` (8,1%) (`graficos/03_tasa_suscripcion_por_job.png`). Tiene sentido: ambos colectivos suelen tener más tiempo disponible y perfiles de ahorro distintos a los de alguien con un empleo a tiempo completo.
- **El resultado de la campaña anterior es un fortísimo predictor:** si la campaña anterior tuvo éxito con ese cliente (`poutcome = success`), la tasa de suscripción sube al **65,3%**, frente al 8,8% de los clientes nunca contactados antes (`graficos/06_tasa_por_poutcome.png`). El histórico de relación con el cliente pesa mucho más que sus datos demográficos.
- **El canal de contacto importa:** contactar por móvil (`cellular`) triplica la tasa de éxito (14,7%) frente al teléfono fijo (5,2%).
- **La edad tiene una relación en forma de "U":** los mayores de 66 años suscriben en el **46%** de los casos y los menores de 25 en el **21,7%**, muy por encima del resto de tramos (8,7%-11,6%) (`graficos/02_distribucion_edad.png`). Son perfiles con menos compromisos de crédito y más orientados al ahorro.
- **El contexto macroeconómico también influye:** `nr.employed` (número de empleados en la economía) y `euribor3m` correlacionan negativamente con la suscripción (-0,36 y -0,27): en periodos de peor contexto laboral/financiero, curiosamente, más clientes suscriben el depósito, probablemente porque buscan productos más seguros.
- **Los datos demográficos del segundo dataset (ingresos, hijos en el hogar, visitas a la web) casi no influyen:** ninguno de ellos supera una correlación de 0,01 con la variable objetivo (`graficos/07_ingresos_por_objetivo.png`), y la tasa de suscripción por número de hijos apenas varía entre el 11,1% y el 11,4%. Es un hallazgo relevante en sí mismo: para esta campaña, el histórico de contacto y el perfil laboral/etario del cliente predicen mucho mejor que su poder adquisitivo o su comportamiento online.
- **El mes de contacto influye poco:** la tasa de suscripción oscila en una banda relativamente estrecha (10,3%-12,4%) a lo largo del año, sin una estacionalidad marcada (`graficos/08_tasa_por_mes.png`).

**Valor práctico:** de cara a una futura campaña, el banco debería priorizar a clientes con una campaña anterior exitosa, jubilados/estudiantes y mayores de 65 o menores de 25 años, contactando preferiblemente por móvil — y no basar la decisión de a quién llamar en los datos demográficos del segundo dataset, que apenas aportan señal.

---

## 🔭 Próximos pasos

- Entrenar un modelo predictivo (p. ej. regresión logística o árbol de decisión) que estime la probabilidad de suscripción **sin usar `duration`** (al no conocerse antes de la llamada, no es una variable válida para decidir a quién contactar).
- Analizar si existe estacionalidad multianual real, separando por año además de por mes.
- Investigar por qué las coordenadas geográficas no son coherentes con un banco portugués, si se llegara a tener acceso a la fuente original de los datos.

---

## 🤝 Contribuciones

Proyecto académico individual, no abierto a contribuciones externas.

---

## 👤 Autoría

- **Autora:** María — Bootcamp Data & Analytics.
- **Datos:** campaña de marketing de un banco portugués (datos de tipo "Bank Marketing", aportados por el bootcamp) + datos demográficos de clientes, aportados por el bootcamp.

# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# dependencies = [
#   "plotly==7.2.0",
# ]
# ///
# MAGIC %md
# MAGIC # Estadística básica de montos por canal
# MAGIC TI2006B · Matrícula: A01234560 · Edición hecha en GitHub para probar el Pull.
# MAGIC
# MAGIC **Pregunta:** ¿Cómo varían los montos de transacción entre canales?
# MAGIC
# MAGIC **Fuente:** datos sintéticos generados en este notebook (semilla 42), según el ejemplo de la actividad.
# MAGIC
# MAGIC **Unidades:** `amount` en unidades sintéticas; `channel` es Online o Store.
# MAGIC
# MAGIC **Valores faltantes:** se excluyen las filas sin `amount` o sin `channel`. No se imputan.

# COMMAND ----------

# MAGIC %pip install plotly==7.2.0

# COMMAND ----------

import numpy as np
import pandas as pd
import plotly
import plotly.express as px

rng = np.random.default_rng(42)
df = pd.DataFrame({
    "channel": ["Online"] * 100 + ["Store"] * 100,
    "amount": np.round(rng.lognormal(3.5, 0.6, 200), 2),
})
df.loc[0, "amount"] = np.nan

print("Versions:", np.__version__, pd.__version__, plotly.__version__)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Calidad de datos

# COMMAND ----------

print("Rows:", len(df))
print("Missing values:", df[["amount", "channel"]].isna().sum(), sep="\n")

clean = df.dropna(subset=["amount", "channel"]).copy()
if len(clean) < 2 or not np.isfinite(clean["amount"]).all():
    raise ValueError("Need at least two finite amounts")

print("Analyzed rows:", len(clean))
print("Excluded rows:", len(df) - len(clean))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Estadística descriptiva
# MAGIC `std` es la desviación estándar muestral; 25%, 50% y 75% son los cuartiles.

# COMMAND ----------

print(clean["amount"].describe().round(2))
print("Median:", round(clean["amount"].median(), 2))

by_channel = clean.groupby("channel")["amount"].agg(["count", "mean", "median"])
print(by_channel.round(2))

assert by_channel["count"].sum() == len(clean), "Los conteos por canal no cuadran"
print("Conteo conciliado:", by_channel["count"].sum(), "=", len(clean))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gráficas

# COMMAND ----------

histogram = px.histogram(
    clean, x="amount", nbins=20, title="Transaction amount distribution",
    labels={"amount": "Amount (synthetic units)"},
)
histogram.show()

# COMMAND ----------

box = px.box(
    clean, x="channel", y="amount", title="Amounts by channel",
    labels={"amount": "Amount (synthetic units)", "channel": "Channel"},
)
box.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusiones
# MAGIC _Borrador redactado con Claude a partir de los resultados; pendiente de revisión del estudiante._
# MAGIC
# MAGIC - **Histograma (forma, dispersión, media contra mediana):** distribución asimétrica a la derecha, concentrada entre 10 y 60, con desviación estándar de 23.12. La media (37.61) supera a la mediana (32.06), consistente con la cola de montos altos (máximo 190.25).
# MAGIC - **Boxplot (comparación entre canales):** las cajas y medianas son parecidas (Online 32.78, Store 30.64). Store muestra más valores atípicos altos, incluido el máximo.
# MAGIC - **Una observación basada en las estadísticas:** Store tiene mayor media (39.55 contra 35.65) pero menor mediana, así que su media más alta no implica un monto típico más alto.
# MAGIC - **Tamaño de los grupos:** 99 filas Online y 100 Store, casi iguales.
# MAGIC - **Efecto de la fila excluida:** se excluyó 1 de 200 filas (0.5%), de Online, cuyo monto se marcó como faltante a propósito. No se imputó.
# MAGIC - **Limitación:** ambos canales se generan con la misma distribución, así que las diferencias observadas no tienen un efecto de canal incorporado.

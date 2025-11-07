import pandas as pd
from pathlib import Path

# Ciclos y sus letras
cycles = {
    "2007-2008": "E",
    "2009-2010": "F",
    "2011-2012": "G",
    "2013-2014": "H",
    "2015-2016": "I",
    "2017-2018": "J"
}

data_path = Path("/Users/jorgegalvez/Desktop/hackaton_duoc_2025/data")

for cycle, letter in cycles.items():
    print(f"\n📁 Procesando ciclo {cycle} ({letter})")

    # Leer cada módulo (si existe)
    def read_xpt(prefix):
        f = data_path / f"{prefix}_{letter}.xpt"
        if f.exists():
            try:
                df = pd.read_sas(f)
                df.columns = df.columns.str.upper()  # Normaliza nombres
                return df
            except Exception as e:
                print(f"  ⚠️ Error leyendo {f.name}: {e}")
        return pd.DataFrame()

    slq = read_xpt("SLQ")
    smq = read_xpt("SMQ")
    paq = read_xpt("PAQ")
    pad = read_xpt("PAD")
    bmx = read_xpt("BMX")# Algunos ciclos tienen PAD, otros no

    # Combinar módulos (solo si tienen SEQN)
    dfs = [d for d in [slq, smq, paq, pad, bmx] if not d.empty and "SEQN" in d.columns]
    if not dfs:
        print("  ⚠️ Ningún módulo encontrado, saltando...")
        continue

    quest = dfs[0]
    for d in dfs[1:]:
        quest = quest.merge(d, on="SEQN", how="outer")

    out_file = data_path / f"QUEST_{cycle.replace('-', '_')}.csv"
    quest.to_csv(out_file, index=False)
    print(f"  ✅ Archivo creado: {out_file.name} ({len(quest)} filas, {len(quest.columns)} columnas)")

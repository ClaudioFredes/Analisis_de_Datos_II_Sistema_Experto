import json
from pathlib import Path

data = json.loads(Path("data/preguntas.json").read_text(encoding="utf-8"))
f3 = data["fase3_por_dominio"]

errores = []
for dom, pathways in f3.items():
    for p in pathways:
        for q in p["preguntas"]:
            required = ["id", "pregunta", "polo_a", "polo_b", "boosts_polo_a", "boosts_polo_b"]
            missing = [k for k in required if k not in q]
            old_keys = [k for k in ["opt1", "opt2", "opt3", "boosts_1", "boosts_3"] if k in q]
            if missing:
                errores.append(f"{q['id']}: falta {missing}")
            if old_keys:
                errores.append(f"{q['id']}: aun tiene claves viejas {old_keys}")

if errores:
    print("ERRORES:")
    for e in errores:
        print(" ", e)
else:
    print("JSON valido. Estructura bipolar correcta en los 90 preguntas.")
    sample = f3["tecnologia"][0]["preguntas"][0]
    print("Muestra:", sample["pregunta"])
    print("  polo_a:", sample["polo_a"])
    print("  polo_b:", sample["polo_b"])
    print("  boosts_polo_a:", sample["boosts_polo_a"])
    print("  boosts_polo_b:", sample["boosts_polo_b"])

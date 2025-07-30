from themachine_pycontrol import Medusa, MedusaDesigner
from pathlib import Path
import json

# with open(Path(r"C:\Users\aag\Downloads\medusa_design.json"), "r") as f:
#     design = json.load(f)

medusa = Medusa(Path(r"C:\Users\aag\Downloads\medusa_design.json"))

# medusa.transfer_volumetric("Vial1", "Waste Vessel", "Pump", 0.1, "liquid", flush=1)
medusa.heat_stir("Vial1", 20, 500)
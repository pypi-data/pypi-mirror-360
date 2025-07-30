import logging
from pathlib import Path
from themachine_pycontrol import Medusa
import logging
import time

logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

medusa = Medusa(
    graph_layout=Path(r"C:\Users\aag\Aspuru-Guzik Lab Dropbox\Lab Manager Aspuru-Guzik\PythonScript\Han\Medusa\examples\monitor_1.json"),
    logger=logger
)

def rxn_2_vial(vial_name: str):
    # rinse tubing and pump head
    for i in range (0, 3):
        print("transfer from reaction to waste")
        medusa.transfer_volumetric(
            source="Reaction",
            destination="Waste Vessel",
            pump_id="Pump",
            volume=0.067,
            flush = 0,
            transfer_type="liquid"
        )
    medusa.transfer_volumetric(
        source="Reaction",
        destination=vial_name,
        pump_id="Pump",
        volume=0.05,
        flush=0,
        transfer_type="liquid"
    )
    medusa.transfer_volumetric(
        source="ACN",
        destination=vial_name,
        pump_id="Pump",
        volume=1,
        transfer_type="liquid",
        flush=1
    )
medusa.heat_stir(
    "Reaction",
    temperature=60,
    # temperature=20,
    rpm=500
)
time.sleep(60*6)
t0 = time.time()
time_stamps = [t0]
for i in range(0,10):
    while time.time() - t0 < 720:
        logger.info(f"waiting for inj, left over {720+t0-time.time()} sec")
        time.sleep(1)
    t0 = time.time()
    logger.info(f"new t0 is {t0}")
    time_stamps.append(t0)
    rxn_2_vial(f"Vial{i+1}")

medusa.heat_stir(
    "Reaction",
    temperature=20,
    rpm=0
)

# medusa.transfer_volumetric("ACN", "Reaction", "Pump", 1, "liquid")


import logging
from pathlib import Path
from medusa import Medusa, MedusaDesigner
import logging
import time

logger = logging.getLogger("test")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# designer = MedusaDesigner()
# designer.new_design()
# exit()
# input()

base_path = Path(r"D:\Aspuru-Guzik Lab Dropbox\Lab Manager Aspuru-Guzik\PythonScript\Han\Medusa\examples")
# layout = input("New design name\n") + ".json"
layout = "poly_test.json"
medusa = Medusa(
    graph_layout=base_path/layout,
    logger=logger     )

medusa.transfer_volumetric(source="Gas Reservoir Vessel", 
                           destination="Waste_Vessel_1", 
                           pump_id="Whatever_Pump", 
                           volume= 1, transfer_type="liquid")
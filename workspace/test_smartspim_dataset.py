import coloredlogs

from utoolbox.io.dataset import SmartSpimDataset

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

ds = SmartSpimDataset("/scratch/20191217_16_50_20_cerebellum_tile/")
print(ds.inventory)

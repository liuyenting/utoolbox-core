import logging
import os

from utoolbox.io.dataset import LatticeScopeTiledDataset, ZarrDataset

logger = logging.getLogger("test_zarr")


def main():
    pwd = os.path.abspath(__file__)
    cwd = os.path.dirname(pwd)
    parent = os.path.dirname(cwd)

    logger.info("loading source dataset")
    ds_src_dir = os.path.join(parent, "data", "demo_3D_2x2x2_CMTKG-V3")
    ds_src = LatticeScopeTiledDataset.load(ds_src_dir)

    logger.info("loading destination dataset")
    ds_dst_dir = os.path.join(parent, "data", "demo_3D_2x2x2_CMTKG-V3.zarr")
    ds_dst = ZarrDataset.load(ds_dst_dir)


if __name__ == "__main__":
    import coloredlogs

    logging.getLogger("tifffile").setLevel(logging.ERROR)
    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )
    main()

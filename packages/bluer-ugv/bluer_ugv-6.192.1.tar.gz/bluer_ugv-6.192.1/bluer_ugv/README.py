import os

from bluer_objects import file, README


from bluer_ugv import NAME, VERSION, ICON, REPO_NAME
from bluer_ugv.swallow.README import items as swallow_items


items = README.Items(
    [
        {
            "name": "bluer-beast",
            "marquee": "https://github.com/waveshareteam/ugv_rpi/raw/main/media/UGV-Rover-details-23.jpg",
            "description": "based on [UGV Beast PI ROS2](https://www.waveshare.com/wiki/UGV_Beast_PI_ROS2).",
            "url": "./bluer_ugv/docs/bluer-beast.md",
        },
        {
            "name": "bluer-fire",
            "marquee": "https://github.com/kamangir/assets/blob/main/bluer-ugv/bluer-fire.png?raw=true",
            "description": "based on a used car.",
            "url": "./bluer_ugv/docs/bluer-fire.md",
        },
        {
            "name": "bluer-swallow",
            "marquee": "https://github.com/kamangir/assets2/blob/main/bluer-swallow/20250618_102816~2_1.gif?raw=true",
            "description": "based on power wheels.",
            "url": "./bluer_ugv/docs/bluer-swallow.md",
        },
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
        )
        for readme in [
            {
                "items": items,
                "path": "..",
            },
            {"path": "docs/bluer-beast.md"},
            {"path": "docs/bluer-fire.md"},
            {
                "items": swallow_items,
                "path": "docs/bluer-swallow.md",
            },
            {"path": "docs/bluer-swallow-analog.md"},
            {"path": "docs/bluer-swallow-digital.md"},
            {"path": "docs/bluer-swallow-digital-parts.md"},
            {"path": "docs/bluer-swallow-digital-terraform.md"},
            {"path": "docs/bluer_swallow-steering-over-current-detection.md"},
            {"path": "docs/bluer-swallow-digital-rpi-pinout.md"},
            {"path": "docs/bluer-swallow-digital-operation.md"},
        ]
    )

from blueness.pypi import setup

from bluer_ugv import NAME, VERSION, DESCRIPTION, REPO_NAME

setup(
    filename=__file__,
    repo_name=REPO_NAME,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    packages=[
        NAME,
        f"{NAME}.help",
        f"{NAME}.swallow",
        f"{NAME}.swallow.session",
        f"{NAME}.swallow.session.classical",
        f"{NAME}.swallow.session.classical.motor",
    ],
    include_package_data=True,
    package_data={
        NAME: [
            "config.env",
            "sample.env",
            ".abcli/**/*.sh",
        ],
    },
)

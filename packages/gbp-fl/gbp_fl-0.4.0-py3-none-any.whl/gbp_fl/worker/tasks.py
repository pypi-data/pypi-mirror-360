"""Async tasks for gbp-fl"""

# pylint: disable=import-outside-toplevel


def index_build(machine: str, build_id: str) -> None:
    """Index packages for the given build"""
    import logging

    from gbp_fl import package_utils
    from gbp_fl.gateway import gateway
    from gbp_fl.types import Build

    logger = logging.getLogger(__package__)
    build = Build(machine=machine, build_id=build_id)

    logger.info("Saving packages for %s.%s", machine, build_id)
    gateway.set_process(build, "index")
    package_utils.index_build(build)
    gateway.set_process(build, "clean")


def deindex_build(machine: str, build_id: str) -> None:
    """Delete all the files from the given build"""
    from gbp_fl.gateway import gateway
    from gbp_fl.records import repo
    from gbp_fl.types import Build

    files = repo.files
    build = Build(machine=machine, build_id=build_id)

    gateway.set_process(build, "deindex")
    files.deindex_build(machine, build_id)
    gateway.set_process(build, "clean")

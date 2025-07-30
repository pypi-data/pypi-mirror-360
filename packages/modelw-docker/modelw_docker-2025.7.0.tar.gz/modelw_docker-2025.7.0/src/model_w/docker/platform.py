from psutil import disk_partitions

__all__ = ["in_docker"]


def _has_dns_mounts():
    """
    Docker will mount the DNS-related files from the host into the container.
    If we detect this pattern, we consider that we're inside a Docker
    container.
    """

    expected_mount_points = {"/etc/resolv.conf", "/etc/hosts", "/etc/hostname"}
    found_mount_points = set(x.mountpoint for x in disk_partitions(all=True))

    return expected_mount_points.issubset(found_mount_points)


def _has_overlay_root():
    """
    In most cases, Docker will mount the root filesystem as an overlayfs. We go
    through the list of mounts and check if the root is an overlayfs.
    """

    for part in disk_partitions(all=True):
        if part.mountpoint == "/":
            return part.fstype == "overlay"

    return False


def _docker_in_cgroup():
    """
    We're looking for the word "docker" in the cgroup file of the first process
    as this could be an indication of being in a Docker container.
    """

    try:
        with open("/proc/1/cgroup") as f:
            return "docker" in f.read()
    except FileNotFoundError:
        return False


def in_docker() -> bool:
    """
    Checks if we are running in a Docker container (well, not 100% sure but
    let's say it's a good enough guess).

    Notes
    -----
    There is no official way to check if we are running in a Docker container.
    This is a best-effort approach that should work in most cases. We use the
    different methods listed above.
    """

    for test in [_has_dns_mounts, _has_overlay_root, _docker_in_cgroup]:
        if test():
            return True

    return False

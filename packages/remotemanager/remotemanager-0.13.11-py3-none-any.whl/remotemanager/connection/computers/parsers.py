from remotemanager.connection.computers import Resources


def slurm(resources: Resources) -> list:
    """
    Example parser for a slurm based computer

    Args:
        resources:
            resources dictionary, provided by BaseComputer
    Returns:
        list of resource request lines
    """
    from remotemanager.connection.computers import format_time

    output = []
    for resource in resources:
        if resource.name == "time":
            formatted = format_time(resource.value)
            output.append(f"#SBATCH --{resource.flag}={formatted}")

        elif resource:
            output.append(f"#SBATCH {resource.flag} {resource.value}")

    return output


def torque(resources: Resources) -> list:
    """
    Example parser for a torque based computer

    Args:
        resources:
            resources dictionary, provided by BaseComputer
    Returns:
        list of resource request lines
    """
    from remotemanager.connection.computers import format_time

    output = []
    for resource in resources:
        if resource.name in ["mpi", "omp", "nodes", "time"]:
            continue
        elif resource:
            output.append(f"#PBS -{resource.flag} {resource.value}")
    # this sort is unnecessary in a real parser, it's just here to help the CI tests
    output = sorted(output)

    output.append(
        f"#PBS -l nodes={resources['nodes'].value}:"
        f"ppn={resources['mpi'].value},"
        f"walltime={format_time(resources['time'].value)}"
    )

    output.append("\ncd $PBS_O_WORKDIR")
    output.append(f"export OMP_NUM_THREADS={resources['omp']}")

    return output

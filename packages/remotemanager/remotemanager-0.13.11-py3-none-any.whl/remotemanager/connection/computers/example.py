from remotemanager.connection.computers.base import BaseComputer
from remotemanager.connection.computers.resource import Resource


class ExampleTorque(BaseComputer):
    """
    example class for connecting to a remote computer using a torque scheduler
    """

    def __init__(self, **kwargs):
        if "host" not in kwargs:
            kwargs["host"] = "remote.address.for.connection"

        super().__init__(**kwargs)

        self.submitter = "qsub"
        self.shebang = "#!/bin/bash"
        self.pragma = "#PBS"

        self.mpi = Resource(flag="ppn", name="mpi")
        self.omp = Resource(flag="omp", name="omp")
        self.nodes = Resource(flag="nodes", name="nodes")
        self.queue = Resource(flag="q", name="queue")
        self.time = Resource(flag="walltime", name="time", format="time")
        self.account = Resource(flag="a", name="account", optional=True)
        self.jobname = Resource(flag="N", name="jobname", optional=True)
        self.outfile = Resource(flag="o", name="outfile", optional=True)
        self.errfile = Resource(flag="e", name="errfile", optional=True)

        self._internal_extra = ""

    def parser(self, resources) -> list:
        """
        Example parser for a torque based computer

        Args:
            resources:
                resources dictionary, provided by BaseComputer
        Returns:
            list of resource request lines
        """
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
            f"walltime={resources['time'].value}"
        )

        output.append("\ncd $PBS_O_WORKDIR")
        output.append(f"export OMP_NUM_THREADS={resources['omp']}")

        return output


class ExampleSlurm(BaseComputer):
    """
    example class for connecting to a remote computer using a slurm scheduler
    """

    def __init__(self, **kwargs):
        if "host" not in kwargs:
            kwargs["host"] = "remote.address.for.connection"

        super().__init__(**kwargs)

        self.submitter = "sbatch"
        self.shebang = "#!/bin/bash"
        self.pragma = "#SBATCH"

        self.mpi = Resource(flag="ntasks", name="mpi")
        self.omp = Resource(flag="cpus-per-task", name="omp")
        self.nodes = Resource(flag="nodes", name="nodes")
        self.queue = Resource(flag="queue", name="queue")
        self.account = Resource(flag="account", name="account", optional=True)
        self.time = Resource(flag="walltime", name="time", format="time")
        self.jobname = Resource(flag="job-name", name="jobname", optional=True)
        self.outfile = Resource(flag="output", name="outfile", optional=True)
        self.errfile = Resource(flag="error", name="errfile", optional=True)

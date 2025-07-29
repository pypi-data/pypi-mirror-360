"""
jupyter_slurm_provisioner

This package registers slurm_ssh_provisioner endpoint.

    pip install jupyter_slurm_ssh_provisioner
    # check endpoints
    jupyter kernelspec provisioners
"""
from .provisioner import SlurmSSHProvisioner

VERSION = "0.2.0"

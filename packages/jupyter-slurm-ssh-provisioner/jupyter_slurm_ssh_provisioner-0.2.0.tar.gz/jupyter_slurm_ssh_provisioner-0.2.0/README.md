# Slurm SSH Provisioner

## What is this package

This package is a Jupyter Kernel Provisioner.

It uses ssh tunnels to launch a remote kernel in a slurm job and connect to it.

Once configured, on the Jupyter Notebook / Lab interface, you can just select a kernel using this provisioner and it will set up everything accordingly.

## Setup

### 1 - Build a remote wrapper script

This remote wrapper will be called when we want to launch the kernel.
Thus, it should:

- Start a slurm job that will start a kernel (the connection file should be named .../kernel-{slurm_job_id}.json, thus the command inside a batch script could be `python -m ipykernel_launcher -f=/tmp/kernel-${SLURM_JOB_ID}.json`)
- Wait for the job to start
- Return the slurm job id

### 2 - Setup a kernel

This is the kernel that will use the slurm-ssh-provisioner. It will be displayed in the Notebook / Lab interface.

```
#~/.local/share/jupyter/kernels/slurm-ssh/kernel.json
{
  "display_name": "Python 3 (Slurm SSH)",
  "language": "python",
  "metadata": {
    "kernel_provisioner": {
      "provisioner_name": "slurm-ssh-provisioner",
      "config": {
        "host": "xxx.xxx.xxx.xxx",
        "username": "debian",
        "first_local_port": 9000,
        "wrapper_cmd": "bash wrapper.sh"
      }
    }
  }
}
```

### 3 - Voilà

You should now be able to use this new kernel.

Use `jupyter kernelspec list` to check your kernel is detected.
Use `jupyter kernelspec provisioners` to check that slurm-ssh-provisioner is installed.

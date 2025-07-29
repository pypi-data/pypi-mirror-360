"""Kernel Provisioner for Jupyter that uses Slurm and SSH to launch kernels on remote machines."""
import logging
import json
from dataclasses import dataclass
from jupyter_client import KernelProvisionerBase # pylint: disable=import-error
import asyncssh # pylint: disable=import-error

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

@dataclass
class SSHConfig:
    """Configuration for SSH connection."""
    hostname: str
    username: str

@dataclass
class SSHTunnelConfig:
    """Configuration for SSH tunnels."""
    # 5 consecutive ports starting with first_local_port will be used
    # to establish the connection with the remote kernel
    first_local_port: int
    ssh_tunnels: list
    ports_map: dict
    ssh_conn: asyncssh.SSHClientConnection

class SlurmSSHProvisioner(KernelProvisionerBase):
    """
    A Kernel Provisioner that creates a kernel in a Slurm job and connects to it.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        config = kwargs.get('config', {})

        # If no config is provided, try to get it from the kernel_spec metadata
        if not config:
            kernel_spec = kwargs.get('kernel_spec', {})
            metadata = getattr(kernel_spec,'metadata', {})
            kp = metadata.get('kernel_provisioner', {})
            config = kp.get('config', {})

        self.ssh_config = SSHConfig(
            hostname=config.get('host', ''),
            username=config.get('username', 'debian')
        )

        self._ssh_tunnel_config = SSHTunnelConfig(
            first_local_port=config.get('first_local_port', 9000),
            ssh_tunnels = [],
            ports_map = {},
            ssh_conn = None
        )

        _log.debug("using config %s",config)

        self._wrapper_cmd = config.get('wrapper_cmd', 'bash ~/wrapper.sh')
        self._slurm_job_id = None # Slurm job ID for the Jupyter kernel
        self._connection_info = {} # Dictionary to hold connection info for the Jupyter kernel
        _log.info("SlurmSSHProvisioner initialized")


    async def launch_kernel(self, cmd, **kwargs): # pylint: disable=unused-argument
        """ Launches a Jupyter kernel on a remote machine using Slurm and SSH."""
        try:
            # ----- STARTING THE REMOTE KERNEL -----
            # Connects to the remote machine via SSH and checks if the connection is successful
            _log.info("Establishing SSH connection to the remote machine...")
            await self._run_ssh_command("cat /etc/hostname")
            _log.info("SSH connection established.")


            # Starts a Slurm job to run the Jupyter kernel
            _log.info("Submitting Slurm job to start the Jupyter kernel...")
            await self._submit_slurm_job()
            _log.info("Slurm job is now running.")


            # ----- CONNECTING TO THE REMOTE KERNEL -----
            # Getting the connection file for the Jupyter kernel
            _log.info("Getting the connection file for the Jupyter kernel...")
            await self._get_remote_connection_file()
            _log.info("Connection file retrieved successfully.")

            # Establishing ssh tunnels to the remote kernel
            _log.info("Establishing SSH tunnels to the remote kernel...")
            try:
                await self._establish_ssh_tunnels()
            except Exception as e:
                _log.error("Failed to establish SSH tunnels: %s", e)
                raise RuntimeError(f"SSH tunnel setup failed: {e}") from e

            # Log the mapping of remote to local ports for debugging
            for remote_port, local_port in self._ssh_tunnel_config.ports_map.items():
                _log.info("Remote port %s is forwarded to local port %s", remote_port, local_port)
            _log.info("SSH tunnels established successfully.")

            # jupyter_client expects the value of "key" to be bytes.
            self._connection_info["key"] = self._connection_info["key"].encode()
            return self._connection_info

        except Exception as e:
            _log.error("Failed to launch kernel: %s", e)
            await self.cleanup(False)
            raise e

    async def pre_launch(self, **kwargs): # pylint: disable=missing-function-docstring
        kwargs = await super().pre_launch(**kwargs)
        kwargs.setdefault('cmd', None)
        return kwargs

    async def _run_ssh_command(self, command):
        try:
            async with asyncssh.connect(self.ssh_config.hostname,
                                        username=self.ssh_config.username) as conn:
                result = await conn.run(command)
                if result.exit_status != 0:
                    raise RuntimeError(
                    f"SSH command failed with status {result.exit_status}: {result.stderr.strip()}"
                    )
                return result.stdout.strip()
        except (asyncssh.Error, OSError) as e:
            raise RuntimeError(f"SSH connection or command failed: {e}") from e

    async def _submit_slurm_job(self):
        _log.info("Submitting Slurm job with command: %s", self._wrapper_cmd)

        output = await self._run_ssh_command(self._wrapper_cmd)

        # Sanity check for sbatch output: usually just the job ID like "123456"
        if not output.strip().isdigit():
            raise RuntimeError(f"Invalid Slurm job ID returned: '{output}'")

        self._slurm_job_id = output.strip()
        _log.info("Slurm job submitted with ID: %s", self._slurm_job_id)

        return self._slurm_job_id

    async def _get_remote_connection_file(self):
        # Define the path to the Jupyter connection file on the remote machine
        remote_connection_file = f"/tmp/kernel-{self._slurm_job_id}.json"

        # Run a command to retrieve the connection file content
        command = f"cat {remote_connection_file}"
        try:
            content = await self._run_ssh_command(command)

            connection_info = json.loads(content)
            if not isinstance(connection_info, dict):
                raise RuntimeError(f"Invalid connection file format: {content}")
            _log.debug("Remote connection file content: %s", connection_info)

            # Extract ports and set up SSH tunnels
            for i,(k, value) in enumerate(connection_info.items()):
                if k in set(["shell_port", "iopub_port", "stdin_port", "control_port", "hb_port"]):
                    local_port = self._ssh_tunnel_config.first_local_port + i
                    self._ssh_tunnel_config.ports_map[value] = local_port

            # Update connection_info to use local ports for tunneling
            for k,value in connection_info.items():
                if k in set(["shell_port", "iopub_port", "stdin_port", "control_port", "hb_port"]):
                    connection_info[k] = self._ssh_tunnel_config.ports_map[value]

            # Save the remote connection file content locally for use by Jupyter
            local_connection_file = f"/tmp/kernel-remote-{self._slurm_job_id}.json"
            with open(local_connection_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(connection_info, indent=2))

            self._connection_info = connection_info

        except RuntimeError as e:
            _log.error("Failed to retrieve remote connection file: %s", e)
            raise e

    async def _establish_ssh_tunnels(self):
        if not self._connection_info:
            raise RuntimeError("Connection info is not set. Cannot establish SSH tunnels.")

        self._ssh_tunnel_config.ssh_conn = await asyncssh.connect(
            self.ssh_config.hostname, username=self.ssh_config.username)

        for remote_port, local_port in self._ssh_tunnel_config.ports_map.items():
            self._ssh_tunnel_config.ssh_tunnels.append(
                await self._ssh_tunnel_config.ssh_conn.forward_local_port(
                    listen_port=local_port,
                    dest_port=remote_port,
                    listen_host='',
                    dest_host='127.0.0.1',
                )
            )

    async def _cancel_slurm_job(self):
        job_id = self._slurm_job_id
        _log.info("Cancelling Slurm job %s...", job_id)
        try:
            await self._run_ssh_command(f"scancel {job_id}")
            _log.info("Slurm job %s cancelled successfully.", job_id)
        except RuntimeError as e:
            _log.error("Failed to cancel Slurm job %s: %s", job_id, e)

    @property
    def has_process(self) -> bool: # pylint: disable=missing-function-docstring
        return True

    async def poll(self): # pylint: disable=missing-function-docstring
        pass

    async def wait(self): # pylint: disable=missing-function-docstring
        pass

    async def send_signal(self, signum: int): # pylint: disable=missing-function-docstring
        _log.warning("Cannot send signal: %s.", signum)

    async def kill(self, restart=False): # pylint: disable=missing-function-docstring
        if restart:
            _log.warning("Cannot restart existing kernel.")
        await self.cleanup(restart)

    async def terminate(self, restart=False): # pylint: disable=missing-function-docstring
        if restart:
            _log.warning("Cannot terminate existing kernel.")
        await self.cleanup(restart)

    async def cleanup(self, restart=False): # pylint: disable=missing-function-docstring, unused-argument
        if self._slurm_job_id:
            _log.info("Cancelling Slurm job %s...", self._slurm_job_id)
            await self._cancel_slurm_job()

        if self._ssh_tunnel_config.ssh_conn:
            _log.info("Closing SSH tunnels...")
            try:
                self._ssh_tunnel_config.ssh_conn.close()
            except (asyncssh.Error, OSError) as e:
                _log.error("Error closing SSH connection: %s", e)

        _log.info("Cleanup completed.")

import os
import pyworkflow.utils as pwutils
import pwem
import subprocess

__version__ = "1.0.0"  # plugin version
_logo = "icon.png"
_references = ['cryoten2025']

# Define V1 before using it
V1 = "1.0.0"

class Plugin(pwem.Plugin):
    _url = "https://github.com/scipion-em/scipion-em-cryoten"
    _supportedVersions = [V1]  # binary version

    @classmethod
    def getEnvActivation(cls):
        return f"conda activate cryoten_env"

    @classmethod
    def getEnviron(cls, gpuID=None):
        """ Setup the environment variables needed to launch the program. """
        environ = pwutils.Environ(os.environ)

        if gpuID is not None:
            environ["CUDA_VISIBLE_DEVICES"] = gpuID

        return environ

    @classmethod
    def getCryotenProgram(cls, program):
        cmd = '%s %s && python %s' % (cls.getCondaActivationCmd(), cls.getEnvActivation(), program)
        return cmd

    @classmethod
    def getCommand(cls, program, args):
        return cls.getCryotenProgram(program) + args

    @classmethod
    def defineBinaries(cls, env):
        def getCryotenInstallationCommands():
            commands = cls.getCondaActivationCmd() + " "
            # Remove existing cryoten directory if it exists
            commands += "if [ -d cryoten ]; then rm -rf cryoten; fi && "
            # Clone the cryoten repository
            commands += "git clone https://github.com/jianlin-cheng/cryoten && "
            # Change directory to cryoten
            commands += "cd cryoten && "
            # Download cryoten_v2.ckpt and rename it to cryoten.ckpt
            commands += "if [ ! -f cryoten_v2.ckpt ]; then wget https://zenodo.org/records/14736781/files/cryoten_v2.ckpt; fi && "
            commands += "mv cryoten_v2.ckpt cryoten.ckpt && "
            # Remove existing conda environment if it exists
            commands += "conda remove -n cryoten_env --all -y && "
            # Create the conda environment
            commands += "conda env create -f environment.yaml && "
            # Activate the conda environment
            commands += "conda activate cryoten_env && "
            # Create a file to indicate that cryoten has been installed
            commands += "touch ../cryoten_installed"
            return commands

        installCmds = [(getCryotenInstallationCommands(), "cryoten_installed")]
        env.addPackage('cryoten', version=V1, tar='void.tgz', commands=installCmds, default=True)
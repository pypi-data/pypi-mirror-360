__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__ = "jianfeng.sunmt@gmail.com"
__maintainer__ = "Jianfeng Sun"

import os

from aerialer.Commander import Commander
from aerialer.cluster.Slurm import Slurm
from aerialer.Generator import Generator
from aerialer.BashCLI import BashCLI


class Transmitter:

    def __init__(
            self,
            config,
            job_fp,
            job_fn,
            scheduler,
            commander,
            cluster='slurm',
            method='slurm_to_many',
            job_suffix='.job',
            **kwargs,
    ):
        self.config = config
        self.job_fp = job_fp
        self.job_fn = job_fn
        self.job_suffix = job_suffix
        self.kwargs = kwargs
        self.method = method
        self.cluster = cluster
        self.scheduler = scheduler
        self.commander = commander

        self.kwargs['config'] = self.config
        self.kwargs['job_fn'] = self.job_fn
        self.kwargs['job_fp'] = self.job_fp
        self.kwargs['job_suffix'] = self.job_suffix

        self.kwargs['cmd_line'] = []

        ### /*** set cluster ***/
        if self.cluster == 'slurm':
            ### /*** generate headlines ***/
            self.Slurm = Slurm(**self.kwargs)
            self.scheduler_menu = {
                "sbatch": self.Slurm.sbatch,
                "sbatch_customised": self.Slurm.sbatch_customised,
            }
            self.scheduler_menu[self.scheduler]()

        ### /*** generate commands ***/
        self.Commander = Commander(**self.kwargs)
        self.command_tool_menu = {
            "dict": self.Commander.tool_py_dict,
        }
        self.Commander.pre()
        self.command = self.command_tool_menu[self.commander]()
        print("======>The CMD (software): {}".format(self.command))
        self.Commander.post()

        ### /*** generate job files ***/
        self.generator = Generator(**self.kwargs)
        self.generator.transcribe()

        self.bashcli = BashCLI(**self.kwargs)
        self.command_shell_menu = {
            "slurm_to_many": self.bashcli.shell_slurm_to_many,
        }
        self.cmd_in_shell = self.command_shell_menu[self.method]()
        print("======>The CMD (shell): {}".format(self.cmd_in_shell))

    def run(self, ):
        os.system(self.cmd_in_shell)
        return 'Job {} submitted!'.format(self.job_fn)


if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv(
        'D:\Document\Programming\Python\minverse\minverse\data\deepisite/cplx.txt',
        sep='\t',
        header=None,
    )
    print(df)
    prots = df[0].unique()[:2]
    print(prots)

    config = {
        "slurm": [
            "#!/usr/bin/env bash",
            "#SBATCH --job-name=myjob",
            "#SBATCH --nodes=1",
            "#SBATCH --time=23:00:00",
            "#SBATCH --ntasks=1",
            "#SBATCH --cpus-per-task=2",
            "#SBATCH --mem=8G",
            "#SBATCH --partition=short",
        ],
        "pre": [
            "source ~/.bashrc",
            "conda activate pbmc",
        ],
        "cmd" : {
            'pypropel_struct_check_cplx': '',
            '-fp': '/project/cribbslab/shared/proj048/sun/pdbtm/',
            '-fn': '',
            '-o': '/project/cribbslab/shared/proj048/sun/check/',
            '-t': 5.5,
            '-vb': False,
        }
    }


    for key, prot in enumerate(prots):
        config['cmd']['-fn'] = prot
        p = Transmitter(
            config=config,
            job_fp='./data/',
            job_fn=str(key),
            cluster='slurm',
            scheduler='sbatch_customised',
            commander='dict',
        )
        # p.run()
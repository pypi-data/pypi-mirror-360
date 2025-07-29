__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__ = "jianfeng.sunmt@gmail.com"
__maintainer__ = "Jianfeng Sun"


class Slurm:

    def __init__(
            self,
            **kwargs,
    ):
        self.kwargs = kwargs
        # print('Slurm: ', self.kwargs)
        if 'node' in self.kwargs.keys():
            self.node = self.kwargs['node']
        else:
            self.node = "1"
        if 'time' in self.kwargs.keys():
            self.time = self.kwargs['time']
        else:
            self.time="23:00:00"
        if 'num_tasks' in self.kwargs.keys():
            self.num_tasks = self.kwargs['num_tasks']
        else:
            self.num_tasks = "1"
        if 'cpu' in self.kwargs.keys():
            self.cpu = self.kwargs['cpu']
        else:
            self.cpu = "2"
        if 'memory' in self.kwargs.keys():
            self.memory = self.kwargs['memory']
        else:
            self.memory = "8"
        if 'partition' in self.kwargs.keys():
            self.partition = self.kwargs['partition']
        else:
            self.partition = 'short'
        if 'job_fn' in self.kwargs.keys():
            self.job_fn = self.kwargs['job_fn']
        if 'job_fpn' in self.kwargs.keys():
            self.job_fpn = self.kwargs['job_fpn']
        if 'command' in self.kwargs.keys():
            self.command = self.kwargs['command']
        if 'slurm' in self.kwargs.keys():
            self.slurm = self.kwargs['slurm']

    def sbatch(self, ):
        with open(self.job_fpn, 'w') as job:
            # job.writelines("#!/bin/bash\n")
            job.writelines("#!/usr/bin/env bash\n")
            job.writelines("#SBATCH --job-name={}\n".format(self.job_fn))
            job.writelines("#SBATCH --nodes={}\n".format(self.node))
            job.writelines("#SBATCH --time={}\n".format(self.time))
            job.writelines("#SBATCH --ntasks={}\n".format(self.num_tasks))
            job.writelines("#SBATCH --cpus-per-task={}\n".format(str(self.cpu)))
            job.writelines("#SBATCH --mem={}G\n".format(str(self.memory)))
            job.writelines("#SBATCH --partition={}\n".format(str(self.partition)))
            job.writelines("\n")
            job.writelines(self.command+"\n")
        return "sbatch {}".format(self.job_fpn)

    def sbatch_customised(self, ):
        lines = self.kwargs['config'].get("slurm", [])

        self.kwargs['cmd_line'].extend(lines)

        # Blank line between this and the rest
        if self.kwargs['cmd_line']:
            self.kwargs['cmd_line'].append("")

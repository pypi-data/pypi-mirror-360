__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__ = "jianfeng.sunmt@gmail.com"
__maintainer__ = "Jianfeng Sun"


class BashCLI:

    def __init__(
            self,
            **kwargs,
    ):
        self.kwargs = kwargs
        self.job_fpn = self.kwargs['job_fp'] + self.kwargs['job_fn'] + '.job'

    def shell_slurm_to_many(self, ):
        return "sbatch {}".format(self.job_fpn)
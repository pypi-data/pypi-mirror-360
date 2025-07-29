__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__ = "jianfeng.sunmt@gmail.com"
__maintainer__ = "Jianfeng Sun"

import os


class Generator:

    def __init__(
            self,
            **kwargs,
    ):
        self.kwargs = kwargs
        if not os.path.exists(self.kwargs['job_fp']):
            os.makedirs(self.kwargs['job_fp'])
        self.job_fpn = self.kwargs['job_fp'] + self.kwargs['job_fn'] + '.job'

    def transcribe(self, ):
        with open(self.job_fpn, 'w') as job:
            job.write("\n".join(self.kwargs['cmd_line']) + "\n")
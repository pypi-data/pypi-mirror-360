__author__ = "Jianfeng Sun"
__version__ = "v1.0"
__copyright__ = "Copyright 2025"
__license__ = "GPL v3.0"
__email__ = "jianfeng.sunmt@gmail.com"
__maintainer__ = "Jianfeng Sun"

from aerialer.Transmitter import Transmitter


def submit(
        config,
        job_fp,
        job_fn,
        scheduler,
        commander,
        cluster='slurm',
        method='slurm_to_many',
        job_suffix='.job',
) -> str:
    return Transmitter(
        config=config,
        job_fp=job_fp,
        job_fn=job_fn,
        scheduler=scheduler,
        commander=commander,
        cluster=cluster,
        method=method,
        job_suffix=job_suffix,
    ).run()


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
        "cmd": {
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
        submit(
            config=config,
            job_fp='./data/',
            job_fn=str(prot),
            cluster='slurm',
            scheduler='sbatch_customised',
            commander='dict',
            method='slurm_to_many',
        )
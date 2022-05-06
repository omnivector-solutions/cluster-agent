from argparse import ArgumentParser
from collections import namedtuple
from itertools import chain
from typing import Iterator, List

from bidict import bidict

_IDENTIFICATION_FLAG = "#SBATCH"
_INLINE_COMMENT_MARK = "#"


def _flagged_line(line: str) -> bool:
    """
    Identify if a provided line starts with the
    identification flag
    """
    return line.startswith(_IDENTIFICATION_FLAG)


def _clean_line(line: str) -> str:
    """
    Clean the provided line by removing the
    identification flag at the beguining of the line,
    then remove the inline comment mark and anything
    after it, and finally strip white spaces at both sides
    """
    return line.lstrip(_IDENTIFICATION_FLAG).split(_INLINE_COMMENT_MARK)[0].strip()


def _split_line(line: str) -> List[str]:
    if "=" in line:
        return line.split("=")
    return line.split()


def _clean_jobscript(jobscript: str) -> Iterator[str]:
    """
    Transform a job script string by filtering only the lines that start with
    the identification flag and mapping a cleaning procedure to them, in order
    to remove the identification flag, remove inline comments, and strip extra
    white spaces. Finally, split each pair of parameter/value and chain them
    in a single iterator.
    """
    jobscript_filtered = filter(_flagged_line, jobscript.splitlines())
    jobscript_cleaned = map(_clean_line, jobscript_filtered)
    jobscript_splitted = map(_split_line, jobscript_cleaned)
    return chain.from_iterable(jobscript_splitted)


SbatchToSlurm = namedtuple("info", "slurm_api sbatch sbatch_short argparser_param")

sbatch_to_slurm = [
    SbatchToSlurm("", "--account", "-A", {}),
    SbatchToSlurm("", "--acctg-freq", "", {}),
    SbatchToSlurm("", "--array", "-a", {}),
    SbatchToSlurm("", "--batch", "", {}),
    SbatchToSlurm("", "--bb", "", {}),
    SbatchToSlurm("", "--bbf", "", {}),
    SbatchToSlurm("", "--begin", "-b", {}),
    SbatchToSlurm("", "--chdir", "-D", {}),
    SbatchToSlurm("", "--cluster-constraint", "", {}),
    SbatchToSlurm("", "--clusters", "-M", {}),
    SbatchToSlurm("", "--comment", "", {}),
    SbatchToSlurm("", "--constraint", "-C", {}),
    SbatchToSlurm("", "--container", "", {}),
    SbatchToSlurm("", "--contiguous", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--core-spec", "-S", {}),
    SbatchToSlurm("", "--cores-per-socket", "", {}),
    SbatchToSlurm("", "--cpu-freq", "", {}),
    SbatchToSlurm("", "--cpus-per-gpu", "", {}),
    SbatchToSlurm("", "--cpus-per-task", "-c", {}),
    SbatchToSlurm("", "--deadline", "", {}),
    SbatchToSlurm("", "--delay-boot", "", {}),
    SbatchToSlurm("", "--dependency", "-d", {}),
    SbatchToSlurm("", "--distribution", "-m", {}),
    SbatchToSlurm("", "--error", "-e", {}),
    SbatchToSlurm("", "--exclude", "-x", {}),
    SbatchToSlurm("", "--exclusive", "", {}),
    SbatchToSlurm("", "--export", "", {}),
    SbatchToSlurm("", "--export-file", "", {}),
    SbatchToSlurm("", "--extra-node-info", "-B", {}),
    SbatchToSlurm("", "--get-user-env", "", {}),
    SbatchToSlurm("", "--gid", "", {}),
    SbatchToSlurm("", "--gpu-bind", "", {}),
    SbatchToSlurm("", "--gpu-freq", "", {}),
    SbatchToSlurm("", "--gpus", "-G", {}),
    SbatchToSlurm("", "--gpus-per-node", "", {}),
    SbatchToSlurm("", "--gpus-per-socket", "", {}),
    SbatchToSlurm("", "--gpus-per-task", "", {}),
    SbatchToSlurm("", "--gres", "", {}),
    SbatchToSlurm("", "--gres-flags", "", {}),
    SbatchToSlurm("", "--hint", "", {}),
    SbatchToSlurm("", "--hold", "-H", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--ignore-pbs", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--input", "-i", {}),
    SbatchToSlurm("", "--job-name", "-J", {}),
    SbatchToSlurm("", "--kill-on-invalid-dep", "", {}),
    SbatchToSlurm("", "--licenses", "-L", {}),
    SbatchToSlurm("", "--mail-type", "", {}),
    SbatchToSlurm("", "--mail-user", "", {}),
    SbatchToSlurm("", "--mcs-label", "", {}),
    SbatchToSlurm("", "--mem", "", {}),
    SbatchToSlurm("", "--mem-bind", "", {}),
    SbatchToSlurm("", "--mem-per-cpu", "", {}),
    SbatchToSlurm("", "--mem-per-gpu", "", {}),
    SbatchToSlurm("", "--mincpus", "", {}),
    SbatchToSlurm("", "--network", "", {}),
    SbatchToSlurm("", "--nice", "", {}),
    SbatchToSlurm("", "--no-kill", "-k", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--no-requeue", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--nodefile", "-F", {}),
    SbatchToSlurm("", "--nodelist", "-w", {}),
    SbatchToSlurm("", "--nodes", "-N", {}),
    SbatchToSlurm("", "--ntasks", "-n", {}),
    SbatchToSlurm("", "--ntasks-per-core", "", {}),
    SbatchToSlurm("", "--ntasks-per-gpu", "", {}),
    SbatchToSlurm("", "--ntasks-per-node", "", {}),
    SbatchToSlurm("", "--ntasks-per-socket", "", {}),
    SbatchToSlurm("", "--open-mode", "", {}),
    SbatchToSlurm("", "--output", "-o", {}),
    SbatchToSlurm("", "--overcommit", "-O", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--oversubscribe", "-s", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--parsable", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--partition", "-p", {}),
    SbatchToSlurm("", "--power", "", {}),
    SbatchToSlurm("", "--priority", "", {}),
    SbatchToSlurm("", "--profile", "", {}),
    SbatchToSlurm("", "--propagate", "", {}),
    SbatchToSlurm("", "--qos", "-q", {}),
    SbatchToSlurm("", "--quiet", "-Q", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--reboot", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--requeue", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--reservation", "", {}),
    SbatchToSlurm("", "--signal", "", {}),
    SbatchToSlurm("", "--sockets-per-node", "", {}),
    SbatchToSlurm("", "--spread-job", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--switches", "", {}),
    SbatchToSlurm("", "--test-only", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--thread-spec", "", {}),
    SbatchToSlurm("", "--threads-per-core", "", {}),
    SbatchToSlurm("", "--time", "-t", {}),
    SbatchToSlurm("", "--time-min", "", {}),
    SbatchToSlurm("", "--tmp", "", {}),
    SbatchToSlurm("", "--uid", "", {}),
    SbatchToSlurm("", "--usage", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--use-min-nodes", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--verbose", "-v", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--version", "-V", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--wait", "-W", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--wait-all-nodes", "", {}),
    SbatchToSlurm("", "--wckey", "", {}),
    SbatchToSlurm("", "--wrap", "", {}),
]


def build_parser():
    parser = ArgumentParser()
    for item in sbatch_to_slurm:
        args = (i for i in (item.sbatch_short, item.sbatch) if i)
        parser.add_argument(*args, **item.argparser_param)
    return parser


def build_mapping_sbatch_to_slurm():
    mapping = bidict()

    for item in sbatch_to_slurm:
        if item.slurm_api:
            mapping[item.sbatch.lstrip("-")] = item.slurm_api

    return mapping


parser = build_parser()
mapping_sbatch_to_slurm = build_mapping_sbatch_to_slurm()

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
    SbatchToSlurm("account", "--account", "-A", {}),
    SbatchToSlurm("account_gather_freqency", "--acctg-freq", "", {}),
    SbatchToSlurm("array", "--array", "-a", {}),
    SbatchToSlurm("batch_features", "--batch", "", {}),
    SbatchToSlurm("burst_buffer", "--bb", "", {}),
    SbatchToSlurm("", "--bbf", "", {}),
    SbatchToSlurm("begin_time", "--begin", "-b", {}),
    SbatchToSlurm("current_working_directory", "--chdir", "-D", {}),
    SbatchToSlurm("cluster_constraints", "--cluster-constraint", "", {}),
    SbatchToSlurm("", "--clusters", "-M", {}),
    SbatchToSlurm("comment", "--comment", "", {}),
    SbatchToSlurm("constraints", "--constraint", "-C", {}),
    SbatchToSlurm("", "--container", "", {}),
    SbatchToSlurm("", "--contiguous", "", dict(action="store_const", const=True)),
    SbatchToSlurm("core_specification", "--core-spec", "-S", {}),
    SbatchToSlurm("cores_per_socket", "--cores-per-socket", "", {}),
    SbatchToSlurm("cpu_frequency", "--cpu-freq", "", {}),
    SbatchToSlurm("cpus_per_gpu", "--cpus-per-gpu", "", {}),
    SbatchToSlurm("cpus_per_task", "--cpus-per-task", "-c", {}),
    SbatchToSlurm("deadline", "--deadline", "", {}),
    SbatchToSlurm("delay_boot", "--delay-boot", "", {}),
    SbatchToSlurm("dependency", "--dependency", "-d", {}),
    SbatchToSlurm("distribution", "--distribution", "-m", {}),
    SbatchToSlurm("standard_error", "--error", "-e", {}),
    SbatchToSlurm("", "--exclude", "-x", {}),
    SbatchToSlurm("exclusive", "--exclusive", "", {}),
    SbatchToSlurm("", "--export", "", {}),
    SbatchToSlurm("", "--export-file", "", {}),
    SbatchToSlurm("", "--extra-node-info", "-B", {}),
    SbatchToSlurm("get_user_environment", "--get-user-env", "", {}),
    SbatchToSlurm("", "--gid", "", {}),
    SbatchToSlurm("gpu_binding", "--gpu-bind", "", {}),
    SbatchToSlurm("gpu_frequency", "--gpu-freq", "", {}),
    SbatchToSlurm("gpus", "--gpus", "-G", {}),
    SbatchToSlurm("gpus_per_node", "--gpus-per-node", "", {}),
    SbatchToSlurm("gpus_per_socket", "--gpus-per-socket", "", {}),
    SbatchToSlurm("gpus_per_task", "--gpus-per-task", "", {}),
    SbatchToSlurm("gres", "--gres", "", {}),
    SbatchToSlurm("gres_flags", "--gres-flags", "", {}),
    SbatchToSlurm("", "--hint", "", {}),
    SbatchToSlurm("hold", "--hold", "-H", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--ignore-pbs", "", dict(action="store_const", const=True)),
    SbatchToSlurm("standard_input", "--input", "-i", {}),
    SbatchToSlurm("name", "--job-name", "-J", {}),
    SbatchToSlurm("kill_on_invalid_dependency", "--kill-on-invalid-dep", "", {}),
    SbatchToSlurm("licenses", "--licenses", "-L", {}),
    SbatchToSlurm("mail_type", "--mail-type", "", {}),
    SbatchToSlurm("mail_user", "--mail-user", "", {}),
    SbatchToSlurm("mcs_label", "--mcs-label", "", {}),
    SbatchToSlurm("memory_per_node", "--mem", "", {}),
    SbatchToSlurm("memory_binding", "--mem-bind", "", {}),
    SbatchToSlurm("memory_per_cpu", "--mem-per-cpu", "", {}),
    SbatchToSlurm("memory_per_gpu", "--mem-per-gpu", "", {}),
    SbatchToSlurm("minimum_cpus_per_node", "--mincpus", "", {}),
    SbatchToSlurm("", "--network", "", {}),
    SbatchToSlurm("nice", "--nice", "", {}),
    SbatchToSlurm("no_kill", "--no-kill", "-k", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--no-requeue", "", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--nodefile", "-F", {}),
    SbatchToSlurm("", "--nodelist", "-w", {}),
    SbatchToSlurm("nodes", "--nodes", "-N", {}),
    SbatchToSlurm("tasks", "-n", {}),
    SbatchToSlurm("tasks_per_core", "--ntasks-per-core", "", {}),
    SbatchToSlurm("", "--ntasks-per-gpu", "", {}),
    SbatchToSlurm("tasks_per_node", "--ntasks-per-node", "", {}),
    SbatchToSlurm("tasks_per_socket", "--ntasks-per-socket", "", {}),
    SbatchToSlurm("open_mode", "--open-mode", "", {}),
    SbatchToSlurm("standard_output", "--output", "-o", {}),
    SbatchToSlurm("", "--overcommit", "-O", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--oversubscribe", "-s", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--parsable", "", dict(action="store_const", const=True)),
    SbatchToSlurm("partition", "--partition", "-p", {}),
    SbatchToSlurm("", "--power", "", {}),
    SbatchToSlurm("priority", "--priority", "", {}),
    SbatchToSlurm("", "--profile", "", {}),
    SbatchToSlurm("", "--propagate", "", {}),
    SbatchToSlurm("qos", "--qos", "-q", {}),
    SbatchToSlurm("", "--quiet", "-Q", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--reboot", "", dict(action="store_const", const=True)),
    SbatchToSlurm("requeue", "--requeue", "", dict(action="store_const", const=True)),
    SbatchToSlurm("reservation", "--reservation", "", {}),
    SbatchToSlurm("signal", "--signal", "", {}),
    SbatchToSlurm("sockets_per_node", "--sockets-per-node", "", {}),
    SbatchToSlurm(
        "spread_job", "--spread-job", "", dict(action="store_const", const=True)
    ),
    SbatchToSlurm("", "--switches", "", {}),
    SbatchToSlurm("", "--test-only", "", dict(action="store_const", const=True)),
    SbatchToSlurm("thread_specification", "--thread-spec", "", {}),
    SbatchToSlurm("threads_per_core", "--threads-per-core", "", {}),
    SbatchToSlurm("time_limit", "--time", "-t", {}),
    SbatchToSlurm("time_minimum", "--time-min", "", {}),
    SbatchToSlurm("", "--tmp", "", {}),
    SbatchToSlurm("", "--uid", "", {}),
    SbatchToSlurm("", "--usage", "", dict(action="store_const", const=True)),
    SbatchToSlurm(
        "minimum_nodes", "--use-min-nodes", "", dict(action="store_const", const=True)
    ),
    SbatchToSlurm("", "--verbose", "-v", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--version", "-V", dict(action="store_const", const=True)),
    SbatchToSlurm("", "--wait", "-W", dict(action="store_const", const=True)),
    SbatchToSlurm("wait_all_nodes", "--wait-all-nodes", "", {}),
    SbatchToSlurm("wckey", "--wckey", "", {}),
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

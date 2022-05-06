from argparse import ArgumentParser
from typing import List, Iterator
from itertools import chain

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


parser = ArgumentParser()

parser.add_argument("-A", "--account")
parser.add_argument("--acctg-freq")
parser.add_argument("-a", "--array")
parser.add_argument("--batch")
parser.add_argument("--bb")
parser.add_argument("--bbf")
parser.add_argument("-b", "--begin")
parser.add_argument("-D", "--chdir")
parser.add_argument("--cluster-constraint")
parser.add_argument("-M", "--clusters")
parser.add_argument("--comment")
parser.add_argument("-C", "--constraint")
parser.add_argument("--container")
parser.add_argument("--contiguous", action="store_const", const=True)
parser.add_argument("-S", "--core-spec")
parser.add_argument("--cores-per-socket")
parser.add_argument("--cpu-freq")
parser.add_argument("--cpus-per-gpu")
parser.add_argument("-c", "--cpus-per-task")
parser.add_argument("--deadline")
parser.add_argument("--delay-boot")
parser.add_argument("-d", "--dependency")
parser.add_argument("-m", "--distribution")
parser.add_argument("-e", "--error")
parser.add_argument("-x", "--exclude")
parser.add_argument("--exclusive")
parser.add_argument("--export")
parser.add_argument("--export-file")
parser.add_argument("-B", "--extra-node-info")
parser.add_argument("--get-user-env")
parser.add_argument("--gid")
parser.add_argument("--gpu-bind")
parser.add_argument("--gpu-freq")
parser.add_argument("-G", "--gpus")
parser.add_argument("--gpus-per-node")
parser.add_argument("--gpus-per-socket")
parser.add_argument("--gpus-per-task")
parser.add_argument("--gres")
parser.add_argument("--gres-flags")
parser.add_argument("--hint")
parser.add_argument("-H", "--hold", action="store_const", const=True)
parser.add_argument("--ignore-pbs", action="store_const", const=True)
parser.add_argument("-i", "--input")
parser.add_argument("-J", "--job-name")
parser.add_argument("--kill-on-invalid-dep")
parser.add_argument("-L", "--licenses")
parser.add_argument("--mail-type")
parser.add_argument("--mail-user")
parser.add_argument("--mcs-label")
parser.add_argument("--mem")
parser.add_argument("--mem-bind")
parser.add_argument("--mem-per-cpu")
parser.add_argument("--mem-per-gpu")
parser.add_argument("--mincpus")
parser.add_argument("--network")
parser.add_argument("--nice")
parser.add_argument("-k", "--no-kill", action="store_const", const=True)
parser.add_argument("--no-requeue", action="store_const", const=True)
parser.add_argument("-F", "--nodefile")
parser.add_argument("-w", "--nodelist")
parser.add_argument("-N", "--nodes")
parser.add_argument("-n", "--ntasks")
parser.add_argument("--ntasks-per-core")
parser.add_argument("--ntasks-per-gpu")
parser.add_argument("--ntasks-per-node")
parser.add_argument("--ntasks-per-socket")
parser.add_argument("--open-mode")
parser.add_argument("-o", "--output")
parser.add_argument("-O", "--overcommit", action="store_const", const=True)
parser.add_argument("-s", "--oversubscribe", action="store_const", const=True)
parser.add_argument("--parsable", action="store_const", const=True)
parser.add_argument("-p", "--partition")
parser.add_argument("--power")
parser.add_argument("--priority")
parser.add_argument("--profile")
parser.add_argument("--propagate")
parser.add_argument("-q", "--qos")
parser.add_argument("-Q", "--quiet", action="store_const", const=True)
parser.add_argument("--reboot", action="store_const", const=True)
# TODO: link it with --no-requeue
parser.add_argument("--requeue", action="store_const", const=True)
parser.add_argument("--reservation")
parser.add_argument("--signal")
parser.add_argument("--sockets-per-node")
parser.add_argument("--spread-job", action="store_const", const=True)
parser.add_argument("--switches")
parser.add_argument("--test-only", action="store_const", const=True)
parser.add_argument("--thread-spec")
parser.add_argument("--threads-per-core")
parser.add_argument("-t", "--time")
parser.add_argument("--time-min")
parser.add_argument("--tmp")
parser.add_argument("--uid")
parser.add_argument("--usage", action="store_const", const=True)
parser.add_argument("--use-min-nodes", action="store_const", const=True)
parser.add_argument("-v", "--verbose", action="store_const", const=True)
parser.add_argument("-V", "--version", action="store_const", const=True)
parser.add_argument("-W", "--wait", action="store_const", const=True)
parser.add_argument("--wait-all-nodes")
parser.add_argument("--wckey")
parser.add_argument("--wrap")

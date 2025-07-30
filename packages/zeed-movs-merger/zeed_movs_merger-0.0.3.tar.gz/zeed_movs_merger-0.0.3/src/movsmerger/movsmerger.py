from difflib import SequenceMatcher
from logging import INFO
from logging import basicConfig
from logging import getLogger
from pathlib import Path
from shlex import join
from shutil import copy
from sys import argv
from typing import TYPE_CHECKING

from movslib.movs import write_txt
from movslib.reader import read

if TYPE_CHECKING:
    from collections.abc import Iterator

    from movslib.model import KV
    from movslib.model import Row

logger = getLogger(__name__)


def _merge_rows_helper(acc: 'list[Row]', new: 'list[Row]') -> 'Iterator[Row]':
    sequence_matcher = SequenceMatcher(None, acc, new, autojunk=False)
    for tag, i1, i2, j1, j2 in sequence_matcher.get_opcodes():
        if tag == 'insert':
            yield from new[j1:j2]
        elif tag in {'equal', 'delete'}:
            yield from acc[i1:i2]
        elif tag == 'replace':  # take from both
            i = i1
            j = j1
            while i < i2 and j < j2:
                a = acc[i]
                n = new[j]
                if a.date > n.date:
                    yield a
                    i += 1
                else:
                    yield n
                    j += 1
            yield from new[j:j2]
            yield from acc[i:i2]


def merge_rows(acc: 'list[Row]', new: 'list[Row]') -> 'list[Row]':
    return list(_merge_rows_helper(acc, new))


def merge_files(acc_fn: str, *mov_fns: str) -> 'tuple[KV, list[Row]]':
    kv, csv = read(acc_fn)
    for mov_fn in mov_fns:
        kv, mov_csv = read(mov_fn)
        csv = merge_rows(csv, mov_csv)
    return kv, csv


def copy_to_txt(bin_fn: str) -> str:
    txt_fn = str(Path(bin_fn).with_suffix('.txt'))
    kv_orig, csv_orig = merge_files(bin_fn)
    write_txt(txt_fn, kv_orig, csv_orig)
    return txt_fn


def _main_txt(accumulator: str, movimentis: list[str]) -> None:
    pqtdiff3_suggestion = ['pqtdiff3']

    backup_accumulator = f'{accumulator}~'
    copy(accumulator, backup_accumulator)
    logger.info('backupd at %s', backup_accumulator)

    pqtdiff3_suggestion.append(backup_accumulator)

    kv, csv = merge_files(accumulator, *movimentis)
    write_txt(accumulator, kv, csv)
    logger.info('overridden %s', accumulator)

    pqtdiff3_suggestion.append(accumulator)

    for movimenti in movimentis:
        logger.info('and merged %s', movimenti)
        if not movimenti.endswith('.txt'):
            text_movimenti = copy_to_txt(movimenti)
            logger.info(' copied as %s', text_movimenti)

            pqtdiff3_suggestion.append(text_movimenti)
        else:
            pqtdiff3_suggestion.append(movimenti)

    logger.info('%s', join(pqtdiff3_suggestion))


def _main_binary(binary_accumulator: str, movimentis: list[str]) -> None:
    logger.info('kept %s', binary_accumulator)
    text_accumulator = copy_to_txt(binary_accumulator)
    logger.info('backupd at %s', text_accumulator)

    accumulator = str(Path(binary_accumulator).with_suffix('.txt'))
    kv, csv = merge_files(binary_accumulator, *movimentis)
    write_txt(accumulator, kv, csv)
    logger.info('merged at %s', accumulator)

    for movimenti in movimentis:
        logger.info('and merged %s', movimenti)
        if not movimenti.endswith('.txt'):
            text_movimenti = copy_to_txt(movimenti)
            logger.info(' copied as %s', text_movimenti)


def main() -> None:
    basicConfig(level=INFO, format='%(message)s')

    if not argv[1:] or '-h' in argv[1:] or '--help' in argv[1:]:
        logger.error('uso: %s ACCUMULATOR [MOVIMENTI...]', argv[0])
        raise SystemExit

    accumulator, *movimentis = argv[1:]

    if accumulator.endswith('.txt'):
        _main_txt(accumulator, movimentis)
    else:
        _main_binary(accumulator, movimentis)

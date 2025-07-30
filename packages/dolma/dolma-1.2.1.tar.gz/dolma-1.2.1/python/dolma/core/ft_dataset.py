"""

Builds a dataset for training a FastText model from 2 or more pretraining datasets.

@rauthur

"""

import argparse
import gzip
import json
import os
import random
from dataclasses import dataclass
from functools import partial
from multiprocessing import Manager, Pool, Process, Queue
from threading import Event
from typing import Generator, List, Optional

import smart_open

from .data_types import TextSlice
from .ft_tagger import BaseFastTextTagger
from .paths import glob_path
from .utils import split_paragraphs, split_sentences

_WRITER_EXIT_MSG = "__WRITE__EXIT__"


@dataclass
class Config:
    target_path: str
    sample_paths: List[str]
    out_path: str
    mode: str
    newlines: str
    n_proc: int
    n_segments: Optional[int]
    pos_label: str
    neg_label: str


def gzip_open(file, mode, **open_kwargs):
    return gzip.open(filename=file, mode=mode, **open_kwargs)


def _split(text: str, config: Config) -> Generator[TextSlice, None, None]:
    if config.mode == BaseFastTextTagger.SENTENCE_LEVEL_TAGGER:
        for sentence in split_sentences(text):
            yield sentence

    elif config.mode == BaseFastTextTagger.PARAGRAPH_LEVEL_TAGGER:
        for paragraph in split_paragraphs(text):
            yield paragraph

    elif config.mode == BaseFastTextTagger.DOCUMENT_LEVEL_TAGGER:
        yield TextSlice(doc=text, start=0, end=len(text))

    else:
        raise RuntimeError(f"Unknown data split mode: {config.mode}")


@dataclass
class ReadResult:
    examples: List[str]


def process_file(config: Config, q: "Queue[str]", flag: Event, label: str, fn):
    # Check a global exit flag and stop processing file
    if flag.is_set():
        return

    print(f"Processing {fn}")

    with smart_open.open(fn, "rt") as f:
        for line in f:
            # Abort part way through processing this file is flag set
            if flag.is_set():
                return

            # Expected JSONL format following OLMo data spec
            data = json.loads(line)
            line_text = data["text"]

            if len(line_text) == 0:
                continue

            for slice in _split(line_text, config):
                final_text = slice.text

                if "\n" in final_text:
                    if config.newlines == "replace":
                        final_text = final_text.replace("\n", " ")
                    elif config.newlines == "skip":
                        continue

                q.put(f"__label__{label} {final_text}")


def write_results(config: Config, q: "Queue[str]", flag: Event):
    written = 0

    with smart_open.open(config.out_path, "wb") as o:
        while True:
            msg = q.get()

            if msg == _WRITER_EXIT_MSG:
                break

            if not flag.is_set():
                o.write(q.get())
                o.write("\n")
                written += 1

            if config.n_segments is not None and written >= config.n_segments:
                flag.set()
                written = 0


def process_paths(paths: List[str], config: Config, q: "Queue[str]", flag: Event, label: str):
    fns = [fn for p in paths for fn in glob_path(p)]
    random.shuffle(fns)

    work_fn = partial(process_file, config, q, flag, label)

    with Pool(processes=max(1, config.n_proc - 1)) as pool:
        pool.map(work_fn, fns)
        pool.close()
        pool.join()


def main(config: Config):
    random.seed(117)

    with Manager() as manager:
        q: "Queue[str]" = manager.Queue()  # type: ignore
        flag = manager.Event()

        writer = Process(target=write_results, args=(config, q, flag))
        writer.start()

        # Generate expected number of positive examples
        process_paths([config.target_path], config, q, flag, config.pos_label)

        # Reset early exit flag as all positive examples processed
        flag.clear()

        # Generate expected number of negative examples
        process_paths(config.sample_paths, config, q, flag, config.neg_label)

        q.put(_WRITER_EXIT_MSG)
        writer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        type=str,
        help="Local or remote path including OLMo formatted TARGET dataset",
    )
    parser.add_argument(
        "-s",
        "--sample",
        required=True,
        type=str,
        nargs="+",
        help="Sample these paths to create negative examples",
    )
    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        required=False,
        default=os.cpu_count(),
        help="Number of processes to launch",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        required=True,
        choices=[
            BaseFastTextTagger.SENTENCE_LEVEL_TAGGER,
            BaseFastTextTagger.PARAGRAPH_LEVEL_TAGGER,
            BaseFastTextTagger.DOCUMENT_LEVEL_TAGGER,
        ],
        help="Output examples at this level",
    )
    parser.add_argument(
        "-o",
        "--output-filename",
        type=str,
        required=True,
        help="Path to write the processed result (can be on S3)",
    )
    parser.add_argument(
        "--n-segments",
        type=int,
        required=False,
        help="Stop after generating this many segments (e.g., sentences)",
    )
    parser.add_argument(
        "--newlines",
        type=str,
        required=False,
        choices=["skip", "keep", "replace"],
        default="skip",
        help="Skip, keep or replace with ' ' examples with newlines after splitting",
    )
    parser.add_argument(
        "--pos-label",
        type=str,
        required=False,
        default="pos",
        help="Use this class label for positive instances",
    )
    parser.add_argument(
        "--neg-label",
        type=str,
        required=False,
        default="neg",
        help="Use this class label for negative instances",
    )

    args = parser.parse_args()
    config = Config(
        target_path=args.target,
        sample_paths=args.sample,
        out_path=args.output_filename,
        mode=args.mode,
        newlines=args.newlines,
        n_proc=args.processes,
        n_segments=args.n_segments,
        pos_label=args.pos_label,
        neg_label=args.neg_label,
    )

    main(config)

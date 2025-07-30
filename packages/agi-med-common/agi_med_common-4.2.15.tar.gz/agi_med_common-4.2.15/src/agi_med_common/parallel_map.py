from typing import Any, Callable, TypeVar, Iterable
import concurrent.futures
from tqdm import tqdm


X = TypeVar("X")


def parallel_map(
    func: Callable[..., X],
    items: Iterable[Any],
    process: bool = False,
    multiple_args: bool = False,
    max_workers: int = 2,
    show_tqdm: bool = False,
    desc: str = ""
) -> list[X]:
    pool = (
        concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        if process
        else concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    )
    with pool as executor:
        futures = []
        for item in items:
            if multiple_args:
                futures.append(executor.submit(func, *item))
            else:
                futures.append(executor.submit(func, item))
        results: list[X] = [
            future.result() for future in tqdm(futures, disable=(not show_tqdm), desc=desc)
        ]
    return results

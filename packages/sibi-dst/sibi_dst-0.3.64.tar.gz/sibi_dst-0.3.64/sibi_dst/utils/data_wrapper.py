import datetime
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Type, Any, Dict, Optional, Union, List

import fsspec
import pandas as pd
from tqdm import tqdm

from .log_utils import Logger
from .parquet_saver import ParquetSaver


class DataWrapper:
    DEFAULT_PRIORITY_MAP = {
        "overwrite": 1,
        "missing_in_history": 2,
        "existing_but_stale": 3,
        "missing_outside_history": 4,
        "file_is_recent": 0
    }
    DEFAULT_MAX_AGE_MINUTES = 1440
    DEFAULT_HISTORY_DAYS_THRESHOLD = 30

    def __init__(
            self,
            dataclass: Type,
            date_field: str,
            data_path: str,
            parquet_filename: str,
            fs: Optional[fsspec.AbstractFileSystem] = None,
            debug: bool = False,
            verbose: bool = False,
            class_params: Optional[Dict] = None,
            load_params: Optional[Dict] = None,
            logger: Logger = None,
            show_progress: bool = False,
            timeout: float = 30,
            max_threads: int = 1,
            **kwargs: Any,
    ):
        self.dataclass = dataclass
        self.date_field = date_field
        self.data_path = self._ensure_forward_slash(data_path)
        self.parquet_filename = parquet_filename
        self.fs = fs or None
        self.debug = debug
        self.verbose = verbose
        self.logger = logger or Logger.default_logger(logger_name=self.dataclass.__name__)
        self.logger.set_level(logging.DEBUG if debug else logging.INFO)
        self.show_progress = show_progress
        self.timeout = timeout
        self.max_threads = max_threads
        self.class_params = class_params or {
            'debug': self.debug,
            'logger': self.logger,
            'fs': self.fs,
            'verbose': self.verbose,
        }
        self.load_params = load_params or {}

        self._lock = threading.Lock()
        self.processed_dates: List[datetime.date] = []
        self.benchmarks: Dict[datetime.date, Dict[str, float]] = {}
        self.mmanifest = kwargs.get("mmanifest", None)
        self.update_planner=kwargs.get("update_planner", None)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.mmanifest and self.mmanifest._new_records:
            self.mmanifest.save()
            self.mmanifest.cleanup_temp_manifests()
        if exc_type is not None:
            self.logger.error(f"Exception occurred: {exc_val}")
        return False

    def _init_filesystem(self) -> fsspec.AbstractFileSystem:
        with self._lock:
            return fsspec.filesystem(self.filesystem_type, **self.filesystem_options)

    @staticmethod
    def _convert_to_date(date: Union[datetime.date, str]) -> datetime.date:
        if isinstance(date, datetime.date):
            return date
        try:
            return pd.to_datetime(date).date()
        except ValueError as e:
            raise ValueError(f"Error converting {date} to datetime: {e}")

    @staticmethod
    def _ensure_forward_slash(path: str) -> str:
        return path.rstrip('/') + '/'

    def process(self, max_retries: int = 3):
        """Process updates with priority-based execution, retries, benchmarking and progress updates"""
        overall_start = time.perf_counter()
        plan = self.update_planner.plan
        # Use len(plan.index) instead of plan.empty for Dask compatibility
        plan_count = len(plan.index)
        if plan_count == 0:
            self.logger.info("No updates required")
            return
        self.logger.info(f"Update plan for {self.dataclass.__name__} includes {plan_count} items for update")

        if self.verbose:
            self.update_planner.show_update_plan()

        for priority in sorted(plan["update_priority"].unique()):
            self._process_priority_group(plan, priority, max_retries)

        total_time = time.perf_counter() - overall_start
        processed = len(self.processed_dates)
        if processed:
            self.logger.info(
                f"Processed {processed} dates in {total_time:.1f}s "
                f"(avg {total_time / processed:.1f}s per date)"
            )
            if self.show_progress or self.verbose:
                self.show_benchmark_summary()

    def _process_priority_group(
            self,
            plan: pd.DataFrame,
            priority: int,
            max_retries: int
    ):
        """Process a single priority group with parallel execution and timing"""
        dates = plan[plan["update_priority"] == priority]["date"].tolist()
        if not dates:
            return
        desc = f"Processing {self.dataclass.__name__}, priority: {priority}"
        self.logger.debug(f"Starting {desc.lower()}")
        group_start = time.perf_counter()
        max_thr = min(len(dates), self.max_threads)
        self.logger.debug(f"Max threads for priority {priority}: {max_thr}")
        with ThreadPoolExecutor(max_workers=max_thr) as executor:
            futures = {executor.submit(self._process_date_with_retry, date, max_retries): date for date in dates}
            for future in tqdm(as_completed(futures), total=len(futures), desc=desc, disable=not self.show_progress):
                date = futures[future]
                try:
                    future.result(timeout=self.timeout)
                except Exception as e:
                    self.logger.error(f"Permanent failure processing {date}: {e}")
        group_time = time.perf_counter() - group_start
        self.logger.info(f"Priority {priority} group processed {len(dates)} dates in {group_time:.1f}s")

    def _process_date_with_retry(self, date: datetime.date, max_retries: int):
        for attempt in range(1, max_retries + 1):
            try:
                self._process_single_date(date)
                return
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"Retry {attempt}/{max_retries} for {date}: {e}")
                else:
                    raise RuntimeError(f"Failed processing {date} after {max_retries} attempts") from e

    def _process_single_date(self, date: datetime.date):
        """Core date processing logic with load/save timing and thread reporting"""
        path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
        self.logger.info(f"Processing date {date.isoformat()} for {path}")
        # self.logger.info(f"Path {path} in {self.skipped}: {path in self.skipped}")
        if path in self.update_planner.skipped and self.update_planner.ignore_missing:
            self.logger.info(f"Skipping {date} as it exists in the skipped list")
            return
        full_path = f"{path}{self.parquet_filename}"

        thread_name = threading.current_thread().name
        self.logger.info(f"[{thread_name}] Executing date: {date} -> saving to: {full_path}")

        overall_start = time.perf_counter()
        try:
            load_start = time.perf_counter()
            with self.dataclass(**self.class_params) as data:
                df = data.load_period(
                    dt_field=self.date_field,
                    start=date,
                    end=date,
                    **self.load_params
                )
            load_time = time.perf_counter() - load_start

            if df.head(1, compute=True).empty:
                if self.mmanifest:
                    schema = df._meta.dtypes.astype(str).to_dict()
                    self.mmanifest.record(
                        full_path=path
                    )
                self.logger.info(f"No data found for {date}. Logged to missing manifest.")
                return
            # Dask-compatible empty check
            # if len(df.index) == 0:
            #    self.logger.warning(f"No data found for {date}")
            #    return

            save_start = time.perf_counter()
            with self._lock:
                ParquetSaver(
                    df_result=df,
                    parquet_storage_path=path,
                    fs=self.fs,
                    logger=self.logger
                ).save_to_parquet(self.parquet_filename)
            save_time = time.perf_counter() - save_start

            total_time = time.perf_counter() - overall_start
            self.benchmarks[date] = {
                "load_duration": load_time,
                "save_duration": save_time,
                "total_duration": total_time
            }
            self._log_success(date, total_time, full_path)
        except Exception as e:
            self._log_failure(date, e)
            raise

    def _log_success(self, date: datetime.date, duration: float, path: str):
        msg = f"Completed {date} in {duration:.1f}s | Saved to {path}"
        self.logger.info(msg)
        self.processed_dates.append(date)

    def _log_failure(self, date: datetime.date, error: Exception):
        msg = f"Failed processing {date}: {error}"
        self.logger.error(msg)

    def show_benchmark_summary(self):
        """Display a summary of load/save timings per date"""
        if not self.benchmarks:
            self.logger.info("No benchmarking data to show")
            return
        df_bench = pd.DataFrame.from_records([{"date": d, **m} for d, m in self.benchmarks.items()])
        df_bench = df_bench.set_index("date").sort_index(ascending=not self.update_planner.reverse_order)
        self.logger.info("Benchmark Summary:\n" + df_bench.to_string())

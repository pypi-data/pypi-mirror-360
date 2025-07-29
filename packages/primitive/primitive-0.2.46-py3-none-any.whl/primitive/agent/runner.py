import asyncio
import os
import re
import shutil
import typing
from enum import Enum, IntEnum
from pathlib import Path, PurePath
from typing import Dict, List, TypedDict

import yaml
from loguru import logger

from primitive.utils.cache import get_artifacts_cache, get_logs_cache, get_sources_cache
from primitive.utils.logging import fmt, log_context
from primitive.utils.psutil import kill_process_and_children
from primitive.utils.shell import env_to_dict

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

if typing.TYPE_CHECKING:
    import primitive.client

CHUNK_SIZE = 64 * 1024
ENV_VAR_LOOKUP_START = "_ENV_VAR_LOOKUP_START"
START_DELIMITER_SIZE = len(bytes(ENV_VAR_LOOKUP_START, encoding="utf-8"))
ENV_VAR_LOOKUP_END = "_ENV_VAR_LOOKUP_END"
END_DELIMITER_SIZE = len(bytes(ENV_VAR_LOOKUP_END, encoding="utf-8"))

assert CHUNK_SIZE > START_DELIMITER_SIZE + END_DELIMITER_SIZE


class Task(TypedDict):
    label: str
    workdir: str
    tags: Dict
    cmd: str


class JobConfig(TypedDict):
    requires: List[str]
    executes: List[Task]
    stores: List[str]


# NOTE This must match FailureLevel subclass in JobSettings model
class FailureLevel(IntEnum):
    ERROR = 1
    WARNING = 2


class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"


class Runner:
    def __init__(
        self,
        primitive: "primitive.client.Primitive",
        job_run: Dict,
        max_log_size: int = 10 * 1024 * 1024,  # 10MB
    ) -> None:
        self.primitive = primitive
        self.job = job_run["job"]
        self.job_run = job_run
        self.job_settings = job_run["jobSettings"]
        self.config = None
        self.source_dir: Path | None = None
        self.initial_env = {}
        self.modified_env = {}
        self.file_logger = None

        # If max_log_size set to <= 0, disable file logging
        if max_log_size > 0:
            log_name = f"{self.job['slug']}_{self.job_run['jobRunNumber']}_{{time}}.primitive.log"

            self.file_logger = logger.add(
                Path(get_logs_cache(self.job_run["id"]) / log_name),
                rotation=max_log_size,
                format=fmt,
                backtrace=True,
            )

    @log_context(label="setup")
    def setup(self) -> None:
        # Attempt to download the job source code
        git_repo_full_name = self.job_run["gitCommit"]["repoFullName"]
        git_ref = self.job_run["gitCommit"]["sha"]
        logger.info(f"Downloading repository {git_repo_full_name} at ref {git_ref}")

        github_access_token = self.primitive.jobs.github_access_token_for_job_run(
            self.job_run["id"]
        )

        downloaded_git_repository_dir = (
            self.primitive.git.download_git_repository_at_ref(
                git_repo_full_name=git_repo_full_name,
                git_ref=git_ref,
                github_access_token=github_access_token,
                destination=get_sources_cache(),
            )
        )

        self.source_dir = downloaded_git_repository_dir.joinpath(
            self.job_settings["rootDirectory"]
        )

        job_filename = self.job_settings["repositoryFilename"]
        logger.info(f"Scanning directory for job file {job_filename}")

        job_config_file = Path(self.source_dir / ".primitive" / job_filename)

        if job_config_file.exists():
            logger.info(
                f"Found job description for {self.job['slug']} at {job_config_file}"
            )
            self.config = yaml.load(open(job_config_file, "r"), Loader=Loader)
        else:
            logger.error(
                f"No job description with matching filename '{job_filename}' found"
            )
            raise FileNotFoundError

        # Setup initial process environment
        self.initial_env = os.environ
        self.initial_env = {
            **self.initial_env,
            **self.primitive.jobs.get_job_secrets_for_job_run(self.job_run["id"]),
        }
        self.initial_env["PRIMITIVE_SOURCE_DIR"] = str(self.source_dir)
        self.initial_env["PRIMITIVE_GIT_SHA"] = str(self.job_run["gitCommit"]["sha"])
        self.initial_env["PRIMITIVE_GIT_BRANCH"] = str(
            self.job_run["gitCommit"]["branch"]
        )
        self.initial_env["PRIMITIVE_GIT_REPO"] = str(
            self.job_run["gitCommit"]["repoFullName"]
        )

    @log_context(label="execute")
    def execute_job_run(self) -> None:
        self.modified_env = {**self.initial_env}
        task_failed = False
        cancelled = False
        timed_out = False

        for task in self.config["executes"]:
            # Everything inside this loop should be contextualized with the task label
            # this way we aren't jumping back and forth between the task label and "execute"
            with logger.contextualize(label=task["label"]):
                # the get status check here is to ensure that if cancel is called
                # while one task is running, we do not run any OTHER labeled tasks
                # THIS is required for MULTI STEP JOBS
                status = self.primitive.jobs.get_job_status(self.job_run["id"])
                status_value = status.data["jobRun"]["status"]
                conclusion_value = status.data["jobRun"]["conclusion"]

                if status_value == "completed" and conclusion_value == "cancelled":
                    cancelled = True
                    break
                if status_value == "completed" and conclusion_value == "timed_out":
                    timed_out = True
                    break

                # Everything within this block should be contextualized as user logs
                with logger.contextualize(type="user"):
                    with asyncio.Runner() as async_runner:
                        if task_failed := async_runner.run(self.run_task(task)):
                            break

        # FOR NONE MULTI STEP JOBS
        # we still have to check that the job was cancelled here as well
        with logger.contextualize(label="conclusion"):
            status = self.primitive.jobs.get_job_status(self.job_run["id"])
            status_value = status.data["jobRun"]["status"]
            conclusion_value = status.data["jobRun"]["conclusion"]
            if status_value == "completed" and conclusion_value == "cancelled":
                cancelled = True
            if status_value == "completed" and conclusion_value == "timed_out":
                timed_out = True

            if cancelled:
                logger.warning("Job cancelled by user")
                return

            if timed_out:
                logger.error("Job timed out")
                return

            conclusion = "success"
            if task_failed:
                conclusion = "failure"
            else:
                logger.success(f"Completed {self.job['slug']} job")

            self.primitive.jobs.job_run_update(
                self.job_run["id"],
                status="request_completed",
                conclusion=conclusion,
            )

    def get_number_of_files_produced(self) -> int:
        """Returns the number of files produced by the job."""
        number_of_files_produced = 0

        # Logs can be produced even if no artifact stores are created for the job run.
        job_run_logs_cache = get_logs_cache(self.job_run["id"])
        has_walk = getattr(job_run_logs_cache, "walk", None)
        if has_walk:
            log_files = [
                file
                for _, _, current_path_files in job_run_logs_cache.walk()
                for file in current_path_files
            ]
        else:
            log_files = [
                file
                for _, _, current_path_files in os.walk(job_run_logs_cache)
                for file in current_path_files
            ]

        number_of_files_produced += len(log_files)

        if "stores" not in self.config:
            return number_of_files_produced

        job_run_artifacts_cache = get_artifacts_cache(self.job_run["id"])
        has_walk = getattr(job_run_artifacts_cache, "walk", None)
        if has_walk:
            artifact_files = [
                file
                for _, _, current_path_files in job_run_artifacts_cache.walk()
                for file in current_path_files
            ]
        else:
            artifact_files = [
                file
                for _, _, current_path_files in os.walk(job_run_artifacts_cache)
                for file in current_path_files
            ]

        number_of_files_produced += len(artifact_files)

        return number_of_files_produced

    async def run_task(self, task: Task) -> bool:
        logger.info(f"Running step '{task['label']}'")
        commands = task["cmd"].strip().split("\n")
        for i, cmd in enumerate(commands):
            # Adding an additional echo and utilizing stdbuf to force line buffering
            # This ensures that the environment variables and starting delimiter are
            # always in a new chunk, vastly simplifying our parsing logic
            args = [
                "/bin/bash",
                "-c",
                f"{cmd} && echo -n '{ENV_VAR_LOOKUP_START}' && env && echo -n '{ENV_VAR_LOOKUP_END}'",
            ]

            logger.info(f"Executing command {i + 1}/{len(commands)}: {cmd}")

            process = await asyncio.create_subprocess_exec(
                *args,
                env=self.modified_env,
                cwd=str(Path(self.source_dir / task.get("workdir", ""))),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                await self.primitive.jobs.ajob_run_update(
                    self.job_run["id"],
                    parent_pid=process.pid,
                )
            except ValueError:
                logger.error(
                    f"Failed to update job run {self.job_run['id']} with process PID {process.pid}"
                )
                kill_process_and_children(pid=process.pid)
                return False

            stdout_failed, stderr_failed = await asyncio.gather(
                self.log_cmd(
                    process=process, stream=process.stdout, tags=task.get("tags", {})
                ),
                self.log_cmd(
                    process=process, stream=process.stderr, tags=task.get("tags", {})
                ),
            )

            returncode = await process.wait()

            logger.info(
                f"Finished executing command {i + 1}/{len(commands)}: {cmd} with return code {returncode}"
            )

            if returncode > 0:
                logger.error(
                    f"Task {task['label']} failed on '{cmd}' with return code {returncode}"
                )
                return True
            elif stdout_failed or stderr_failed:
                logger.error(f"Task {task['label']} failed on '{cmd}'")
                return True

        logger.success(f"Completed {task['label']} task")
        return False

    async def log_cmd(self, process, stream, tags: Dict = {}) -> bool:
        failure_detected = False
        parse_environment = False
        last_chunk_buffer = b""
        environment_buffer = b""
        while chunk := await stream.read(CHUNK_SIZE):
            if parse_environment:
                environment_buffer += chunk
                continue

            # First, look for start delimiter in chunk
            full_chunk = last_chunk_buffer + chunk
            last_chunk_buffer = b""
            start_index = full_chunk.find(bytes(ENV_VAR_LOOKUP_START, encoding="utf-8"))

            if start_index != -1:
                environment_buffer = full_chunk[start_index + START_DELIMITER_SIZE :]
                processed_lines = await self.read_chunk(full_chunk[:start_index])
                parse_environment = True
            else:
                processed_lines = await self.read_chunk(full_chunk)

                while (
                    len(last_chunk_buffer) < START_DELIMITER_SIZE
                    and len(processed_lines) > 0
                ):
                    last_chunk_buffer += bytes(
                        processed_lines.pop() + "\n", encoding="utf-8"
                    )

            # Handle logging
            parse_logs = self.job_settings["parseLogs"]
            parse_stderr = self.job_settings["parseStderr"]

            for line in processed_lines:
                level = LogLevel.INFO
                tag = None
                if (parse_logs and "error" in line.lower()) or (
                    parse_stderr and stream is process.stderr
                ):
                    level = LogLevel.ERROR
                elif parse_logs and "warning" in line.lower():
                    level = LogLevel.WARNING

                # If we already detected a failure, skip checking
                if not failure_detected:
                    failure_detected = (
                        level == LogLevel.ERROR
                        and self.job_settings["failureLevel"] >= FailureLevel.ERROR
                    ) or (
                        level == LogLevel.WARNING
                        and self.job_settings["failureLevel"] >= FailureLevel.WARNING
                    )

                # Tag on the first matching regex in the list
                for tag_key, regex in tags.items():
                    pattern = re.compile(regex)
                    if pattern.match(line):
                        tag = tag_key
                        break

                logger.bind(tag=tag).log(level.value, line)

        start_index = environment_buffer.find(
            bytes(ENV_VAR_LOOKUP_END, encoding="utf-8")
        )
        if parse_environment and start_index == -1:
            logger.error("Environment variable buffer did not contain end delimiter")
            failure_detected = True
            return failure_detected

        environment_buffer = environment_buffer[:start_index]
        new_env_vars = env_to_dict(environment_buffer)
        if len(new_env_vars.keys()) > 0:
            self.modified_env = {**self.modified_env, **new_env_vars}
        return failure_detected

    async def read_chunk(self, chunk: bytes) -> List[str]:
        """Converts a chunk of bytes into proper lines."""
        lines = []
        current_line = ""
        for char in chunk.decode():
            if char in ("\n", "\r"):
                lines.append(current_line)
                current_line = ""
            else:
                current_line += char

        # Handle extra characters in the buffer
        if len(current_line) > 0:
            lines.append(current_line)

        return [line for line in lines if len(line) > 0]

    @log_context(label="cleanup")
    def cleanup(self) -> None:
        for glob in self.config.get("stores", []):
            # Glob relative to the source directory
            matches = self.source_dir.rglob(glob)

            for match in matches:
                relative_path = PurePath(match).relative_to(self.source_dir)
                dest = Path(get_artifacts_cache(self.job_run["id"]) / relative_path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                Path(match).replace(dest)

        shutil.rmtree(path=self.source_dir)

        number_of_files_produced = self.get_number_of_files_produced()
        logger.info(
            f"Produced {number_of_files_produced} files for {self.job['slug']} job"
        )
        self.primitive.jobs.job_run_update(
            self.job_run["id"],
            number_of_files_produced=number_of_files_produced,
        )

        logger.remove(self.file_logger)

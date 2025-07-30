from typing import Callable, Optional, Any
import math
import multiprocessing as mp
import gymnasium as gym
import numpy as np
import time
import platform

from rich.live import Live

from sai_rl.model import ModelManager
from sai_rl.sai_console import SAIConsole, SAIStatus
from sai_rl.benchmark.types import BenchmarkResults
from sai_rl.benchmark.utils import generate_batch_panel
from sai_rl.benchmark.seed import get_match_seed


# TODO: make this simpler and cleaner
def run_benchmark(
    env_creator: Callable[[], gym.Env],
    num_envs: int = 1,
    seed: Optional[int] = None,
    model: Optional[ModelManager] = None,
    timeout: int = 600,
    console: Optional[SAIConsole] = None,
    status: Optional[SAIStatus] = None,
    show_progress: bool = False,
    save_actions: bool = False,
) -> tuple[BenchmarkResults, list[Any], Optional[list[int]]]:
    """
    Run a benchmark on the given environment and model in CPU‐sized batches,
    reusing a single Live display for the entire run.
    Always returns (results, actions, seeds), even on error.
    """
    start_time = time.time()

    if status:
        status.update("Starting benchmark...")
        status.stop()

    results: BenchmarkResults = {
        "status": "error",
        "score": None,
        "duration": 0,
        "matches": [],
        "logs": None,
        "error": None,
    }

    all_actions: list[list[Any]] = [] if save_actions else []
    all_seeds: list[int] = []

    try:
        is_windows = platform.system() == "Windows"
        if is_windows:
            mp.set_start_method("spawn", force=True)
        else:
            mp.set_start_method("fork", force=True)

        # Calculate Batch Size for Parallel Processing
        cpu_count = mp.cpu_count()
        batch_size = min(num_envs, cpu_count)
        num_batches = math.ceil(num_envs / batch_size)

        # Using the Competition Seed or a Random One
        # -> this lets us reproduce the environment for when we want to replay the benchmark
        #    for recording specific episodes after the benchmark is done.
        master_seed = seed if seed is not None else np.random.randint(0, 2**31 - 1)

        # Aggregate Results Across Batches
        agg_scores: list[float] = []
        agg_durations: list[float] = []
        agg_timesteps: list[int] = []

        reached_timeout = False

        # Create the Benchmark Tracker
        batch_live: Optional[Live] = None
        if show_progress and console:
            batch_live = Live(
                generate_batch_panel(console),
                console=console.console,
                refresh_per_second=15,
            )
            batch_live.start()

        for batch_idx in range(num_batches):
            batch_start_time = time.time()
            current_batch_size = min(batch_size, num_envs - batch_idx * batch_size)

            if console and not show_progress:
                console.info(
                    f"→ Batch {batch_idx + 1}/{num_batches}: {current_batch_size} envs"
                )

            # Append Current Batch Seeds
            batch_seeds = [
                get_match_seed(master_seed, batch_idx * batch_size + i)
                for i in range(current_batch_size)
            ]
            all_seeds.extend(batch_seeds)

            # Create the Environments
            # -> We found issues with the AsyncVectorEnv on Windows, so we use SyncVectorEnv instead
            #    for now. We should revisit this later to improve performance.
            envs: Optional[gym.vector.VectorEnv] = None
            if is_windows:
                envs = gym.vector.SyncVectorEnv(
                    [env_creator for _ in range(current_batch_size)],
                    copy=False,
                )
            else:
                envs = gym.vector.AsyncVectorEnv(
                    [env_creator for _ in range(current_batch_size)],
                    shared_memory=True,
                    copy=False,
                )

            if envs is None:
                raise RuntimeError("Failed to create environment")

            # Figure out the Environment Timeout
            # -> this is to make sure the timeout is the timeout of the time inside the environment
            #    and not the time it takes to run the benchmark. On slower machines, this can lead to
            #    early timeouts if the environment is slow.
            fps: int = envs.metadata.get("render_fps", 30)
            timeout_timestep = timeout * fps

            # Create the State to Track the Environment
            alive = np.ones(current_batch_size, bool)
            terminated = np.zeros(current_batch_size, bool)
            truncated = np.zeros(current_batch_size, bool)
            scores = np.zeros(current_batch_size, float)
            timesteps = np.zeros(current_batch_size, int)
            batch_actions = (
                [[] for _ in range(current_batch_size)] if save_actions else None
            )

            def update_status(is_final: bool = False) -> None:
                if batch_live and console:
                    batch_live.update(
                        generate_batch_panel(
                            console,
                            batch_active_count=int(alive.sum()),
                            batch_size=current_batch_size,
                            batch_idx=batch_idx,
                            batch_start_time=batch_start_time,
                            batch_score=float(scores.mean()),
                            batch_timesteps=timesteps.sum(),
                            batch_timeout=timeout,
                            num_envs=num_envs,
                            num_batches=num_batches,
                            is_final=is_final,
                        )
                    )

            # Reset the Environments
            timestep = 0
            obs, _ = envs.reset(seed=batch_seeds)
            update_status()

            # Batch Environment Loop
            while not np.all(terminated | truncated):
                if timestep > timeout_timestep:
                    if console:
                        console.warning(
                            f"Hit timeout at {timestep / fps:.1f}s; stopping current batch."
                        )
                    reached_timeout = True
                    break

                actions = model.get_action(obs) if model else envs.action_space.sample()
                obs, rewards, terms, truns, _ = envs.step(actions)

                terminated |= terms
                truncated |= truns
                alive = ~(terminated | truncated)
                scores += rewards * alive
                timesteps += alive.astype(int)
                timestep += 1

                if save_actions:
                    for i in range(current_batch_size):
                        if alive[i]:
                            batch_actions[i].append(actions[i])  # type: ignore

                update_status()

            update_status(True)

            # Save the Batch Results
            if save_actions and batch_actions is not None:
                all_actions.extend(batch_actions)

            agg_scores.extend(scores.tolist())
            agg_durations.extend((timesteps / fps).tolist())
            agg_timesteps.extend(timesteps.tolist())

            try:
                envs.close()
            except:  # noqa: E722
                pass

        # Calculate the Final Results
        duration = time.time() - start_time
        avg_score = float(np.mean(agg_scores)) if agg_scores else 0.0

        results["status"] = "success" if not reached_timeout else "timeout"
        results["score"] = avg_score  # type: ignore
        results["duration"] = duration
        results["matches"] = [
            {
                "score": agg_scores[i],
                "duration": agg_durations[i],
            }
            for i in range(num_envs)
        ]
        results["logs"] = None
        results["error"] = None

        if batch_live:
            batch_live.stop()

        if console:
            console.info(
                f"\n\nBenchmark of {num_envs} episodes completed in {results['duration']:.2f} seconds"
            )
            console.info(f"Average Episode Score: {results['score']:.2f}")
            console.info(
                f"Average Duration per Batch: {np.mean(agg_durations):.2f} seconds"
            )
            console.info(
                f"Average FPS Across All Batches: {np.sum(agg_timesteps) / results['duration']:.2f}"
            )
            console.info(f"Total Timesteps: {np.sum(agg_timesteps)}\n")

    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        if console:
            console.error(f"Error during benchmark: {e!r}")

    finally:
        if batch_live:
            batch_live.stop()
        if status:
            status.update("Cleaning up...")

    return results, all_actions, all_seeds

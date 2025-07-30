from typing import Literal, Optional, Callable
from io import StringIO
from types import SimpleNamespace
import json

import os
import gymnasium as gym
import random
import string
import sys
import shutil
import numpy as np

from rich.align import Align
from rich.text import Text

from sai_rl.api.routes.competition import CompetitionType
from sai_rl.api.routes.environment import EnvironmentType

from sai_rl.api.routes.package import PackageType
from sai_rl.package_control import PackageControl
from sai_rl.sai_console import SAIConsole, SAIStatus
from sai_rl.utils import TeeIO, config
from sai_rl.error import (
    BenchmarkError,
    CompetitionError,
    SubmissionError,
    SetupError,
    EnvironmentError,
    AuthenticationError
)

from sai_rl.api import APIClient
from sai_rl.model import ModelManager
from sai_rl.types import ModelType, ModelLibraryType
from sai_rl.benchmark import (
    run_benchmark,
    record_episode,
    BenchmarkResults,
)


class SAIClient(object):
    """
    Main client for interacting with the SAI platform.

    The SAIClient provides methods for:
    - Managing competitions and submissions
    - Loading and evaluating models
    - Working with action functions
    - Managing environment packages
    - Running benchmarks and watching agents

    Args:
        env_id (Optional[str]): ID of environment to load
        api_key (Optional[str]): API key for authentication
        competition_id (Optional[str]): ID of competition to load
        action_function_id (Optional[str]): ID of action function to use
        api_base (Optional[str]): Custom API endpoint
        max_network_retries (Optional[int]): Max API retry attempts
        console (Optional[SAIConsole]): Custom console for output

    Examples:
        Basic usage:
        >>> client = SAIClient(api_key="your-api-key")
        >>> client.load_competition("comp-123456")
        >>> client.watch()  # Watch random agent

        Using a model:
        >>> model = torch.load("my_model.pt")
        >>> client.benchmark(model=model, model_type="pytorch")

        Working with action functions:
        >>> client.load_action_fn("./my_action.py")
        >>> client.submit_action_fn()
    """

    def __init__(
        self,
        env_id: Optional[str] = None,
        api_key: Optional[str] = None,
        *,
        comp_id: Optional[str] = None,
        api_base: Optional[str] = None,
        is_server: bool = False,
    ):
        self.is_server = is_server
        if is_server:
            self._log_capture = StringIO()
            self._original_stdout = sys.stdout
            sys.stdout = TeeIO(self._log_capture, sys.__stdout__)
        else:
            self._log_capture = None
            self._original_stdout = None
        self._console = SAIConsole()

        with self._console.status("Loading SAI CLI...") as status:
            # Setup API client
            self._api = APIClient(
                console=self._console, api_key=api_key, api_base=api_base
            )

            # Setup package control
            self._package_control = PackageControl(
                api=self._api,
                console=self._console,
                is_disabled=is_server,
            )

            self._console.display_title(
                self._package_control._get_package_version("sai_rl") or "unknown",
                self._package_control._is_editable_install("sai_rl"),
            )

            self._package_control.setup(status)

            self._package: Optional[PackageType] = None
            self._environment: Optional[EnvironmentType] = None
            self._competition: Optional[CompetitionType] = None

            self._env = None

            if comp_id is not None:
                self._console.print()
                self._load_competition(comp_id, status)

            elif env_id is not None:
                self._console.print()
                self._load_environment(env_id, status)

            self._console.print()

    # ---- Internal Utility Methods ----
    def _check_setup(self) -> bool:
        if not self._package_control.setup_complete:
            raise SetupError("Setup not complete")
        assert self._package_control.setup_complete
        return True

    def _get_logs(self) -> str:
        if self._log_capture:
            return self._log_capture.getvalue()
        return ""

    # ---- Print Methods ----
    def _print_environment(self):
        if not self._environment:
            raise EnvironmentError("Environment not loaded")

        id = self._environment.get("gymId")
        name = self._environment.get("name")
        package = self._environment.get("package").get("name")
        gym_id = self._environment.get("gymId")
        gym_type = self._environment.get("type")
        gym_vars = {}

        link = f"{config.platform_url}/environments/{id}"
        if self._competition:
            id = self._competition.get("slug")
            link = f"{config.platform_url}/competitions/{self._competition.get('id')}"
            gym_vars = self._competition.get("environmentVariables")

        title = f'"{name}" ({id})'

        info_group = f"""[bold cyan]
Env:[/bold cyan]    {gym_id}
[bold cyan]Env Standard:[/bold cyan] {gym_type}
[bold cyan]Env Vars:[/bold cyan] {json.dumps(gym_vars, indent=2)}
[bold cyan]Package:[/bold cyan] {package}"""

        link_group = f"[link={link}]View in Platform →[/link]"

        env_info = self._console.group(
            Align.left(Text.from_markup(info_group)),
            Align.right(Text.from_markup(link_group)),
        )

        panel = self._console.panel(env_info, title=title, padding=(0, 2))
        self._console.print(panel)

    def _print_submission_details(
        self,
        name: str,
        model_manager: ModelManager,
    ):
        if not self._competition:
            raise CompetitionError("Competition not loaded")

        title = f'"{name}" Submission Details'

        info_group = f"""[bold cyan]
Competition ID:[/bold cyan]      {self._competition.get("id")}
[bold cyan]Competition Name:[/bold cyan]    {self._competition.get("name")}
[bold cyan]Model Type:[/bold cyan]          {model_manager.model_type}
[bold cyan]Preprocess Function:[/bold cyan]  {"Custom" if model_manager._preprocess_manager else f"Default (environment state)"}
[bold cyan]Action Function:[/bold cyan]  {"Custom" if model_manager._action_manager else f"Default ({'sample' if model_manager._handler.is_continuous else 'argmax'})"}"""

        submission_info = self._console.group(Align.left(Text.from_markup(info_group)))

        panel = self._console.panel(submission_info, title=title, padding=(0, 2))
        self._console.print(panel)

    # ---- Load Methods ----
    def _load_competition_from_json(
        self, competition_json: str, status: Optional[SAIStatus] = None
    ):
        if status:
            status.update("Loading competition...")

        self._package = None
        self._environment = None
        self._competition = None

        try:
            comp_env = json.loads(
                competition_json, object_hook=lambda d: SimpleNamespace(**d)
            )
            competition: CompetitionType = {
                "id": comp_env.id,
                "slug": comp_env.slug,
                "name": comp_env.name,
                "opensource": comp_env.opensource
                if hasattr(comp_env, "opensource")
                else False,
                "environment": {
                    "id": comp_env.environment.id,
                    "name": comp_env.environment.name,
                    "gymId": comp_env.environment.gymId,
                    "type": comp_env.environment.type,
                    "actionType": comp_env.environment.actionType,
                    "package": {
                        "id": comp_env.environment.package.id,
                        "name": comp_env.environment.package.name,
                        "version": comp_env.environment.package.version,
                    },
                },
                "environmentVariables": vars(comp_env.environmentVariables)
                if hasattr(comp_env, "environmentVariables")
                and not isinstance(comp_env.environmentVariables, dict)
                else (
                    comp_env.environmentVariables
                    if hasattr(comp_env, "environmentVariables")
                    else {}
                ),
                "numberOfBenchmarks": comp_env.numberOfBenchmarks
                if hasattr(comp_env, "numberOfBenchmarks")
                else None,
                "seed": comp_env.seed if hasattr(comp_env, "seed") else None,
                "evaluation_fn": comp_env.evaluationFn if hasattr(comp_env, "evaluationFn") else None
            }

            self._competition = competition
            self._environment = self._competition.get("environment")
            self._package = self._environment.get("package")

            self._print_environment()

            package_name = self._package.get("name")
            if package_name:
                self._package_control.load(package_name, status=status)

            self._console.success("Successfully loaded competition.")
            return self._competition
        except json.JSONDecodeError as e:
            raise CompetitionError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise CompetitionError(f"Failed to load competition: {e}")

    def _load_competition(
        self, competition_id: str, status: Optional[SAIStatus] = None
    ):
        if status:
            status.update(f"Loading competition {competition_id}...")

        self._package = None
        self._environment = None
        self._competition = None

        self._competition = self._api.competition.get(competition_id)
        if not self._competition:
            raise CompetitionError("Competition not found")

        self._environment = self._competition.get("environment")
        self._package = self._environment.get("package")

        self._print_environment()

        package_name = self._package.get("name")
        if package_name:
            self._package_control.load(package_name, status=status)

        self._console.success("Successfully loaded competition.")
        return self._competition

    def _load_environment(
        self, environment_id: str, status: Optional[SAIStatus] = None
    ):
        if status:
            status.update(f"Loading environment {environment_id}...")

        self._package = None
        self._environment = None
        self._competition = None

        self._environment = self._api.environment.get(environment_id)
        if not self._environment:
            raise EnvironmentError("Environment not found")

        self._print_environment()

        self._package = self._environment.get("package")

        package_name = self._package.get("name")
        if package_name:
            self._package_control.load(package_name, status=status)

        self._console.success("Successfully loaded environment.")
        return self._environment

    # ---- Make Methods ----
    def _custom_evaluation_wrapper(self, env, use_custom_eval: bool = False):
        if not use_custom_eval and not self.is_server:
            return env

        evaluation_fn = self._competition.get("evaluation_fn") if self._competition else None
        if evaluation_fn is not None and isinstance(evaluation_fn, str):
            global_ns = {"np": np}
            exec(evaluation_fn, global_ns)
            evaluation_fn = global_ns.get("evaluation_fn")

            if callable(evaluation_fn):
                if isinstance(env, gym.Env):
                    class CustomEvaluationWrapper(gym.Wrapper):
                        def __init__(self, env):
                            super().__init__(env)
                            self.evaluation_fn = evaluation_fn
                            self.unwrapped_env = self.unwrap_env()

                        def unwrap_env(self):
                            env = self.env
                            while hasattr(env, "env"):
                                env = env.env
                            return env                            

                        def step(self, action):
                            obs, reward, terminated, truncated, info = self.unwrapped_env.step(action)
                            reward = self.evaluation_fn(self.unwrapped_env)
                            return obs, reward, terminated, truncated, info

                    env = CustomEvaluationWrapper(env)
        return env

    def _create_env_factory(self, use_custom_eval: bool = False):
        if self._environment is None:
            raise EnvironmentError("Environment not loaded")

        env_id = self._environment.get("gymId")
        env_type = self._environment.get("type")
        competition_vars = (
            self._competition.get("environmentVariables") if self._competition else {}
        )

        def env_factory(**kwargs):
            env_vars = {
                **(competition_vars or {}),
                "render_mode": "rgb_array",
                **kwargs,
            }

            env = None
            if env_type == "gymnasium":
                env = gym.make(env_id, **env_vars)
            elif env_type == "gym-v26":
                env = gym.make("GymV26Environment-v0", env_id=env_id, **env_vars)
            elif env_type == "gym-v21":
                env = gym.make("GymV21Environment-v0", env_id=env_id, **env_vars)
            elif env_type == "pufferlib":
                try:
                    from pufferlib.emulation import GymnasiumPufferEnv
                    from pufferlib.ocean import env_creator

                    env = GymnasiumPufferEnv(
                        env_creator=env_creator(env_id),
                        env_kwargs=env_vars,
                    )
                except ImportError:
                    raise ImportError(
                        "Pufferlib is not installed. "
                        "Please install it using \"pip install 'sai_rl[pufferlib]'\"."
                    )
            else:
                raise EnvironmentError(f"Unsupported environment type: {env_type}")

            return self._custom_evaluation_wrapper(env, use_custom_eval)

        return env_factory

    def _make_new_env(
        self,
        *,
        render_mode: Literal["human", "rgb_array"] = None,
        **kwargs,
    ):
        if self._environment is None:
            raise EnvironmentError("Environment not loaded")

        if self._env is not None:
            self._env.close()
            self._env = None

        env_id = self._environment.get("gymId")
        competition_vars = (
            self._competition.get("environmentVariables") if self._competition else {}
        )
        env_vars = {**(competition_vars or {}), "render_mode": render_mode, **kwargs}

        if self._competition and kwargs:
            self._console.warning(
                "Additional environment arguments will override competitions settings."
                "Your local environment may not match the competition configuration."
            )

        env_type = self._environment.get("type")

        if env_type == "gymnasium":
            env = gym.make(env_id, **env_vars)
        elif env_type == "gym-v26":
            env = gym.make("GymV26Environment-v0", env_id=env_id, **env_vars)
        elif env_type == "gym-v21":
            env = gym.make("GymV21Environment-v0", env_id=env_id, **env_vars)
        elif env_type == "pettingzoo":
            raise NotImplementedError(
                "PettingZoo environments are not supported yet. "
                "Please use the competition environment."
            )
        elif env_type == "pufferlib":
            try:
                from pufferlib.emulation import GymnasiumPufferEnv
                from pufferlib.ocean import env_creator

                return GymnasiumPufferEnv(
                    env_creator=env_creator(env_id),
                    env_kwargs=env_vars,
                )
            except ImportError:
                raise ImportError(
                    "Pufferlib is not installed. "
                    "Please install it using \"pip install 'sai_rl[pufferlib]'\"."
                )
        else:
            raise EnvironmentError(
                f"Unsupported environment type: {env_type}. "
                "Please use a supported environment."
            )

        self._env = env
        return env

    ############################################################
    # Public Methods
    ############################################################

    # ---- Competition Methods ----
    def get_competition(self):
        """
        Gets information about the currently loaded competition.

        Returns:
            dict: Competition information including:
                - id: Competition ID
                - name: Competition name
                - env_name: Environment name
                - env_lib: Environment library
                - env_vars: Environment variables
            None: If no competition is loaded

        Examples:
            >>> comp = client.get_competition()
            >>> if comp:
            ...     print(f"Using {comp['env_name']}")
        """
        self._check_setup()
        return self._competition

    def load_competition(self, competition_id: str):
        """
        Loads a competition by its ID.

        Args:
            competition_id (str): Platform ID of the competition to load

        Returns:
            dict: Loaded competition information

        Raises:
            CompetitionError: If competition cannot be loaded

        Examples:
            >>> client.load_competition("comp-123456")
            >>> client.watch()  # Watch random agent
        """
        self._check_setup()

        with self._console.status(f"Loading competition {competition_id}...") as status:
            return self._load_competition(competition_id, status=status)

    def list_competitions(self, show_table: bool = True):
        """
        Lists all available competitions.

        Args:
            show_table (bool): Whether to display a formatted table of competitions

        Returns:
            list[dict]: List of competition information including:
                - id: Competition ID
                - name: Competition name
                - description: Competition description
                - environment_name: Name of the environment
                - link: URL to view in platform

        Examples:
            >>> # Show table and get data
            >>> competitions = client.list_competitions()
            >>>
            >>> # Get data only
            >>> competitions = client.list_competitions(show_table=False)
        """
        self._check_setup()
        self._console.print()

        with self._console.status("Loading competitions...") as status:
            competitions = self._api.competition.list()
            if competitions is None:
                self._console.warning("No competitions found.")
                return []

            if show_table:
                status.update("Displaying competitions...")
                table = self._console.table("Available Competitions")

                table.add_column("ID", style="yellow")
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Description", style="magenta")
                table.add_column("Environment", style="green")
                table.add_column("View in Platform", style="green", justify="center")

                for comp in competitions:
                    table.add_row(
                        comp.get("slug"),
                        comp.get("name"),
                        comp.get("description"),
                        comp.get("environment").get("name"),
                        f"[link={comp.get('link')}]View →[/link]",
                    )

                self._console.print(table)
                self._console.print()

            return competitions

    # ---- Submission Methods ----
    def list_submissions(self, show_table: bool = True):
        """
        Lists all your submissions across competitions.

        Args:
            show_table (bool): Whether to display a formatted table of submissions
                If True, shows a rich table with clickable platform links
                If False, returns data only

        Returns:
            list[dict]: List of submission information including:
                - id: Submission ID
                - name: Submission name
                - status: Current status ("pending", "running", "completed", "failed")
                - last_score: Most recent evaluation score
                - competition: Name of the competition
                - link: URL to view submission in platform

        Note: Returns empty list if no submissions are found

        Examples:
            >>> # Show table and get data
            >>> submissions = client.list_submissions()
            >>>
            >>> # Get data only
            >>> submissions = client.list_submissions(show_table=False)
            >>> for sub in submissions:
            ...     print(f"{sub['name']}: {sub['last_score']}")
            >>>
            >>> # Filter completed submissions
            >>> completed = [s for s in submissions
            ...             if s['status'] == 'completed']
            >>> print(f"Found {len(completed)} completed submissions")
        """
        self._check_setup()
        self._console.print()

        with self._console.status("Loading submissions...") as status:
            submissions = self._api.submission.list()
            if submissions is None:
                self._console.warning("No submissions found.")
                return []

            if show_table:
                status.update("Displaying submissions...")
                table = self._console.table("Your Submissions")
                table.add_column("ID", style="yellow")
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Model Type", style="magenta")
                table.add_column("Competition", style="cyan")
                table.add_column("Environment", style="green")
                table.add_column("Last Score", style="bright_green", justify="right")
                table.add_column("SAIStatus", style="bright_yellow")
                table.add_column(
                    "View in Platform", style="bright_blue", justify="center"
                )

                for submission in submissions:
                    table.add_row(
                        submission.get("id"),
                        submission.get("name"),
                        submission.get("model_type"),
                        submission.get("competition_name"),
                        submission.get("environment_name"),
                        submission.get("last_score"),
                        submission.get("status"),
                        f"[link={submission.get('link')}]View →[/link]"
                        if submission.get("link")
                        else "",
                    )

                self._console.print(table)
                self._console.print()

            return submissions

    # ---- Environment Methods ----
    def get_environment(self):
        """
        Gets information about the currently loaded environment.

        Returns:
            dict: Environment information including:
                - id: Environment ID
                - slug: Environment slug
                - name: Environment name
                - env_name: Environment name in the registry
                - env_library: Environment library
            None: If no environment is loaded

        Examples:
            >>> env = client.get_environment()
            >>> if env:
            ...     print(f"Using {env['env_name']}")
        """
        self._check_setup()
        return self._environment

    def load_environment(self, environment_id: str):
        """
        Loads an environment by its ID.

        Args:
            environment_id (str): Platform ID of the environment to load

        Returns:
            dict: Loaded environment information

        Raises:
            EnvironmentError: If environment cannot be loaded

        Examples:
            >>> client.load_environment("env-123456")
            >>> client.watch()  # Watch random agent
        """
        self._check_setup()

        with self._console.status(f"Loading environment {environment_id}...") as status:
            return self._load_environment(environment_id, status=status)

    def list_environments(self, show_table: bool = True):
        """
        Lists all available environments.

        Args:
            show_table (bool): Whether to display a formatted table of environments

        Returns:
            list[dict]: List of environment information including:
                - id: Environment ID
                - name: Environment name
                - description: Environment description
                - link: URL to view in platform

        Examples:
            >>> # Show table and get data
            >>> environments = client.list_environments()
            >>>
            >>> # Get data only
            >>> environments = client.list_environments(show_table=False)
        """
        self._check_setup()
        self._console.print()

        with self._console.status("Loading environments...") as status:
            environments = self._api.environment.list()
            if environments is None:
                self._console.warning("No environments found.")
                return []

            if show_table:
                status.update("Displaying environments...")
                table = self._console.table("Available Environments")

                table.add_column("ID", style="yellow")
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Description", style="magenta")
                table.add_column("View in Platform", style="green", justify="center")

                for env in environments:
                    table.add_row(
                        env.get("env_name"),
                        env.get("name"),
                        env.get("description"),
                        f"[link={env.get('link')}]View →[/link]",
                    )

                self._console.print(table)
                self._console.print()

            return environments

    def reset(self):
        """
        Clears the currently loaded environment.

        This removes all references to the current environment, allowing
        you to load a different one or start fresh.

        Examples:
            >>> client.reset_environment()
            >>> client.load_environment("new-env-id")
        """
        self._check_setup()
        self._competition = None
        self._environment = None
        self._package = None

    def make_env(self, render_mode: Literal["human", "rgb_array"] = None, **kwargs):
        """
        Creates a new instance of the competition environment.

        Args:
            render_mode (Literal["human", "rgb_array"]): How to render the environment
                - "human": Display environment in a window
                - "rgb_array": Return RGB array for video recording
            **kwargs: Additional keyword arguments to pass to the environment
                Note: These will be ignored when using a competition environment

        Returns:
            gym.Env: A Gymnasium environment instance

        Raises:
            CompetitionError: If no competition is loaded

        Examples:
            >>> env = client.make_env()
            >>> obs, _ = env.reset()
            >>> env.render()

            >>> # With custom environment args (only works for non-competition environments)
            >>> env = client.make_env(truncate_episode_steps=100)
        """
        self._check_setup()
        return self._make_new_env(render_mode=render_mode, **kwargs)

    def watch(
        self,
        model: Optional[ModelType] = None,
        action_function: Optional[str | Callable] = None,
        preprocessor_class: Optional[str | type] = None,
        *,
        model_type: Optional[ModelLibraryType] = None,
        algorithm: Optional[str] = None,
        num_runs: int = 1,
    ):
        """
        Watch a model (or random agent) interact with the environment.

        Args:
            model (Optional[ModelType]): Model to watch. Can be one of:
                - PyTorch model (torch.nn.Module)
                - TensorFlow model (tf.Module or tensorflow.compat.v1)
                - Keras model (tf.keras.Model)
                - Stable-Baselines3 model (BaseAlgorithm)
                - ONNX model (OnnxAgentWrapper)
                - URL or file path (str)
                If None, uses random actions
            model_type (Optional[ModelLibraryType]): Framework used. One of:
                - "pytorch"
                - "tensorflow"
                - "keras"
                - "stable_baselines3"
                - "onnx"
            runs (int): Number of episodes to run (default: 1)

        Raises:
            BenchmarkError: If watching fails
            CompetitionError: If no competition is loaded

        Examples:
            >>> # Watch random agent
            >>> client.watch()
            >>>
            >>> # Watch PyTorch model
            >>> model = torch.load("model.pt")
            >>> client.watch(model=model, model_type="pytorch", runs=3)
        """
        self._check_setup()
        if not self._environment:
            raise EnvironmentError("Environment not loaded")

        env = None
        self._console.print()
        with self._console.status("Setting up environment...") as status:
            try:
                env = self._make_new_env(render_mode="human")

                if model is not None:
                    model_manager = ModelManager(
                        env=env,
                        model=model,
                        model_type=model_type,
                        algorithm=algorithm,
                        preprocessor_class=preprocessor_class,
                        action_function=action_function,
                        console=self._console,
                        status=status,
                    )
                    status.update(
                        f"Watching {model_manager.model_type} model in '{env.spec.id}' environment..."  # type: ignore
                    )
                else:
                    model_manager = None
                    status.update(
                        f"Watching random agent in '{env.spec.id}' environment..."  # type: ignore
                    )

                self._console.print()

                for run_index in range(num_runs):
                    self._console.info(
                        f"Running watch {run_index + 1} of {num_runs}..."
                    )

                    obs, _ = env.reset()
                    terminated = False
                    truncated = False
                    scores = 0
                    timesteps = 0

                    while not terminated and not truncated:
                        if model_manager:
                            action = model_manager.get_action(obs)[0]
                        else:
                            action = env.action_space.sample()

                        obs, reward, terminated, truncated, info = env.step(action)
                        env.render()

                        scores += reward  # type: ignore
                        timesteps += 1

                    env.close()

                    self._console.success(
                        f"Episode finished after {timesteps} timesteps with score: {scores}"
                    )

                self._console.print()

            except Exception as e:
                self._console.error(f"Unable to watch model: {e}")
                raise BenchmarkError(e)

            finally:
                if env:
                    env.close()

    def benchmark(
        self,
        model: Optional[ModelType] = None,
        action_function: Optional[str | Callable] = None,
        preprocessor_class: Optional[str | type] = None,
        *,
        model_type: Optional[ModelLibraryType] = None,
        algorithm: Optional[str] = None,
        num_envs: Optional[int] = None,
        record: bool = False,
        video_dir: Optional[str] = "results",
        show_progress: bool = True,
        throw_errors: bool = True,
        timeout: int = 600,
        use_custom_eval: bool = False
    ) -> BenchmarkResults:
        """
        Run benchmark evaluation of a model.

        Args:
            model (Optional[ModelType]): Model to evaluate. Can be one of:
                - PyTorch model (torch.nn.Module)
                - TensorFlow model (tf.Module or tensorflow.compat.v1)
                - Keras model (tf.keras.Model)
                - Stable-Baselines3 model (BaseAlgorithm)
                - ONNX model (onnxruntime.InferenceSession)
                - URL or file path (str)
                If None, uses random actions
            model_type (Optional[ModelLibraryType]): Framework used. One of:
                - "pytorch"
                - "tensorflow"
                - "keras"
                - "stable_baselines3"
                - "onnx"
            video_dir (Optional[str]): Path to save video recording
                If None, no video is recorded
            show_progress (bool): Whether to show progress bar during benchmark
                Defaults to True
            throw_errors (bool): Whether to raise exceptions on errors
                If False, returns error in results instead
                Defaults to True

        Returns:
            BenchmarkResults: Results containing:
                - status: "success", "error", or "timeout"
                - score: Total reward achieved
                - duration: Time taken in seconds
                - error: Error message if failed

        Raises:
            BenchmarkError: If benchmark fails and throw_errors is True
            CompetitionError: If no competition is loaded

        Examples:
            >>> # Benchmark random agent
            >>> results = client.benchmark()
            >>> print(f"Score: {results['score']}")
            >>>
            >>> # Benchmark PyTorch model with video
            >>> model = torch.load("model.pt")
            >>> results = client.benchmark(
            ...     model=model,
            ...     model_type="pytorch",
            ...     video_path="benchmark.mp4"
            ... )
        """
        self._console.print()

        results: BenchmarkResults = {
            "status": "error",
            "score": None,
            "duration": 0,
            "matches": [],
            "logs": None,
            "error": None,
        }

        env = None
        with self._console.status("Setting up benchmark...") as status:
            try:
                self._check_setup()
                if not self._environment:
                    raise EnvironmentError("Environment not loaded")
            except Exception as e:
                results["status"] = "error"
                results["error"] = str(e)

                if throw_errors and results.get("status") == "error":
                    raise BenchmarkError(results.get("error"))
                return results

            try:
                status.update("Setting up environment...")
                env = self._make_new_env()

                if env is None:
                    raise EnvironmentError("Environment not loaded")

                render_mode = None
                if record:
                    # Check if the environment supports video recording
                    render_modes = env.metadata.get("render_modes", [])

                    if "rgb_array" in render_modes:
                        render_mode = "rgb_array"
                    elif "human" in render_modes:
                        render_mode = "human"
                    elif self._environment.get("type") == "pufferlib":
                        render_mode = "rgb_array"
                    else:
                        self._console.warning(
                            "Video recording not supported for this environment. "
                            "Continuing without video."
                        )

                model_manager = None
                if model is not None:
                    model_manager = ModelManager(
                        console=self._console,
                        env=env,
                        model=model,
                        model_type=model_type,
                        algorithm=algorithm,
                        preprocessor_class=preprocessor_class,
                        action_function=action_function,
                        status=status,
                    )
                else:
                    self._console.warning("No model provided. Using random actions.")

                self._console.print()
                env.close()
                env = None
                self._env = None

                env_factory = self._create_env_factory(use_custom_eval)
                num_environments = (
                    num_envs
                    if num_envs is not None
                    else self._competition.get("numberOfBenchmarks")
                    if self._competition
                    and self._competition.get("numberOfBenchmarks") is not None
                    else 20
                )

                results, actions, seeds = run_benchmark(
                    env_creator=env_factory,
                    console=self._console,
                    seed=self._competition.get("seed") if self._competition else None,
                    model=model_manager,
                    num_envs=num_environments or 20,
                    status=status,
                    show_progress=show_progress,
                    save_actions=record,
                    timeout=timeout,
                )

                if seeds is not None:
                    scores = {
                        seed: results["matches"][i]["score"]
                        for i, seed in enumerate(seeds)
                    }

                    # Check if all scores are the same
                    unique_scores = set(scores.values())

                    seeds_to_record = {}
                    if len(unique_scores) == 1:
                        # All scores are identical - just pick different seeds for variety
                        seed_list = list(scores.keys())
                        seeds_to_record = {
                            "best": seed_list[0],
                            "worst": seed_list[min(1, len(seed_list) - 1)],
                            "average": seed_list[min(2, len(seed_list) - 1)],
                        }
                    else:
                        best_seed, _ = max(scores.items(), key=lambda x: x[1])
                        worst_seed, _ = min(scores.items(), key=lambda x: x[1])

                        # Find average score seed that's different from best and worst
                        used_seeds = {best_seed, worst_seed}
                        remaining_scores = [
                            (seed, score)
                            for seed, score in scores.items()
                            if seed not in used_seeds
                        ]

                        avg_score = sum(scores.values()) / len(scores)
                        average_seed, _ = min(
                            remaining_scores, key=lambda x: abs(x[1] - avg_score)
                        )

                        seeds_to_record = {
                            "best": best_seed,
                            "worst": worst_seed,
                            "average": average_seed,
                        }

                    should_record = record and render_mode and video_dir
                    if should_record and results["status"] == "timeout":
                        self._console.warning(
                            "The benchmark was interrupted by the timeout, match recordings will not be saved."
                        )

                    if should_record and results["status"] == "success":
                        assert render_mode is not None
                        assert video_dir is not None

                        if not os.path.exists(video_dir):
                            os.makedirs(video_dir)

                        for label, seed in seeds_to_record.items():
                            match_index = seeds.index(seed)
                            video_path = os.path.join(video_dir, f"{label}.mp4")
                            record_episode(
                                env_creator=env_factory,  # type: ignore
                                render_mode=render_mode,
                                seed=seed,
                                actions=actions[match_index],
                                output_path=video_path,
                            )
                            self._console.info(
                                f"✓ {label.capitalize()} episode finished recording."
                            )
                            results["matches"][match_index]["videoKey"] = label

                self._console.print()
                self._console.debug(
                    f"\n[bold]Results:[/bold]\n{json.dumps(results, indent=2)}"
                )

                if results["status"] == "success":
                    self._console.success("Benchmark completed successfully")

            except Exception as e:
                results["status"] = "error"
                results["error"] = str(e)

            finally:
                if env:
                    env.close()

                if self._log_capture:
                    results["logs"] = self._get_logs()

            if throw_errors and results.get("status") == "error":
                raise BenchmarkError(results.get("error"))

            self._console.print()
            return results

    # ---- Model Methods ----
    def submit_model(
        self,
        name: str,
        model: ModelType,
        action_function: Optional[str | Callable] = None,
        preprocessor_class: Optional[str | type] = None,
        *,
        model_type: Optional[ModelLibraryType] = None,
        algorithm: Optional[str] = None,
        use_onnx: bool = False,
        tag: str = "default",
    ):
        return self.submit(
            name=name,
            model=model,
            action_function=action_function,
            preprocessor_class=preprocessor_class,
            model_type=model_type,
            algorithm=algorithm,
            use_onnx=use_onnx,
            tag=tag,
        )

    def submit(
        self,
        name: str,
        model: ModelType,
        action_function: Optional[str | Callable] = None,
        preprocessor_class: Optional[str | type] = None,
        *,
        model_type: Optional[ModelLibraryType] = None,
        algorithm: Optional[str] = None,
        use_onnx: bool = False,
        tag: str = "default",
    ):
        """
        Submits a model to the current competition.

        Args:
            name (str): Name for the submission
            model (ModelType): Model to submit. Can be one of:
                - PyTorch model (torch.nn.Module)
                - TensorFlow model (tf.Module or tensorflow.compat.v1)
                - Keras model (tf.keras.Model)
                - Stable-Baselines3 model (BaseAlgorithm)
                - ONNX model (OnnxAgentWrapper)
                - URL or file path (str)
            model_type (Optional[ModelLibraryType]): Framework used. One of:
                - "pytorch" - For PyTorch models
                - "tensorflow" - For TensorFlow v1 and v2 models
                - "keras" - For Keras models
                - "stable_baselines3" - For Stable-Baselines3 models
                - "onnx" - For ONNX models
            preprocessor_class (Optional[str | type]): Preprocess class code
            action_function (Optional[str | Callable]): Action function code
            use_onnx (bool): Whether to convert the model to ONNX format before submission
            skip_warning (bool): Skip validation warnings related to action function configuration

        Returns:
            dict: Submission information including:
                - id: Unique submission ID
                - name: Submission name
                - type: Model framework type
                - status: Current submission status
                - created_at: Timestamp of submission
                - updated_at: Timestamp of last update

        Raises:
            SubmissionError: If submission fails validation checks or upload fails
            CompetitionError: If no competition is currently loaded
            ValueError: If model type is invalid or incompatible with provided model

        Examples:
            >>> # Submit PyTorch model
            >>> model = torch.load("model.pt")
            >>> result = client.submit_model(
            ...     name="My Model v1",
            ...     model=model,
            ...     model_type="pytorch"
            ... )
            >>>
            >>> # Submit with action function and ONNX conversion
            >>> def action_fn(policy):
            ...     return np.argmax(policy, axis=1)
            >>>
            >>> result = client.submit_model(
            ...     name="My Model v2",
            ...     model=model,
            ...     model_type="pytorch",
            ...     action_function=action_fn,
            ...     use_onnx=True
            ... )
        """
        self._check_setup()

        if not self._api.api_key:
            raise AuthenticationError("No API key provided.\n\nPlease run 'sai login' to authenticate with your user.\n")

        if not self._competition:
            raise CompetitionError(
                "No competition is loaded, please load a competition first using SAIClient(competition_id='')"
            )

        if self._competition["opensource"]:
            raise SubmissionError(
                "Cannot use python to submit to an open source competition. Please submit through the SAI website."
            )

        with self._console.status("Submitting model to the competition...") as status:
            env = self._make_new_env()

            model_manager = ModelManager(
                console=self._console,
                env=env,
                model=model,
                model_type=model_type,
                algorithm=algorithm,
                preprocessor_class=preprocessor_class,
                action_function=action_function,
            )

            self._console.print()

            self._print_submission_details(
                name,
                model_manager,  # use_onnx, action_function
            )

            file_extension = {
                "stable_baselines3": ".zip",
                "pytorch": ".pt",
                "tensorflow": ".pb",
                "keras": ".keras",
                "onnx": ".onnx",
            }.get("onnx" if use_onnx else model_manager.model_type, "")

            isTensorflowV2 = False
            if model_manager.model_type == "tensorflow" and not use_onnx:
                isTensorflowV2 = model_manager._handler.is_tf2_model(model)

            random_id = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=6)
            )
            os.makedirs(config.temp_path, exist_ok=True)
            temp_model_path = f"{config.temp_path}/{random_id}{file_extension if not isTensorflowV2 else ''}"
            model_manager.save_model(temp_model_path, use_onnx=use_onnx)

            if preprocessor_class:
                temp_preprocess_code_path = f"{config.temp_path}/preprocess_{random_id}.py"
                model_manager.save_preprocess_code(temp_preprocess_code_path)                

            if action_function:
                temp_action_fn_path = f"{config.temp_path}/action_{random_id}.py"
                model_manager.save_action_function(temp_action_fn_path)

            status.update("Creating submission...")

            adj_temp_model_path = (
                f"{temp_model_path}{'/saved_model.pb' if isTensorflowV2 else ''}"
            )
            files = {
                "model": (
                    os.path.basename(adj_temp_model_path),
                    open(adj_temp_model_path, "rb"),
                    "application/octet-stream",
                ),
            }

            if preprocessor_class:
                files["preprocessCode"] = (
                    os.path.basename(temp_preprocess_code_path),
                    open(temp_preprocess_code_path, "rb"),
                    "text/plain",
                )

            if action_function:
                files["actionFunction"] = (
                    os.path.basename(temp_action_fn_path),
                    open(temp_action_fn_path, "rb"),
                    "text/plain",
                )

            is_submission_success = False
            try:
                is_submission_success = self._api.submission.create(
                    {
                        "name": name,
                        "type": model_manager.model_type,
                        "competitionId": self._competition.get("id"),
                        "algorithm": model_manager.algorithm,
                        "method": "python",
                        "tag": tag,
                    },
                    files=files,
                )
            finally:
                for file_tuple in files.values():
                    file_tuple[1].close()

            if not is_submission_success:
                raise SubmissionError("Failed to create submission")

            if os.path.exists(temp_model_path):
                if isTensorflowV2 and os.path.isdir(temp_model_path):
                    shutil.rmtree(temp_model_path)  # remove directory
                else:
                    os.remove(temp_model_path)  # remove file
            else:
                self._console.warning("Temporary model file not found.")

            self._console.success("Model submitted successfully.")

            return is_submission_success

    def check_model_compliance(self, env, model: ModelType):
        model_manager = ModelManager(env, model)
        compliant = model_manager.check_compliance()
        if compliant:
            print("Your model is compliant with SAI submissions ✅")
        else:
            print("Your model is NOT compliant with SAI submissions ❌")
        return compliant

    def save_model(
        self,
        name: str,
        model: ModelType,
        model_type: Optional[ModelLibraryType] = None,
        algorithm: Optional[str] = None,
        use_onnx: bool = False,
        output_path: str = "./",
    ):
        """
        Saves a model to disk in the appropriate format.

        Args:
            name (str): Name for the saved model file (without extension)
            model (ModelType): Model to save. Can be one of:
                - PyTorch model (torch.nn.Module)
                - TensorFlow model (tf.Module or tensorflow.compat.v1)
                - Keras model (tf.keras.Model)
                - Stable-Baselines3 model (BaseAlgorithm)
                - ONNX model (OnnxAgentWrapper)
                - URL or file path (str)
            model_type (Optional[ModelLibraryType]): Framework used. One of:
                - "pytorch" (.pt)
                - "tensorflow" (.pb)
                - "keras" (.keras)
                - "stable_baselines3" (.zip)
                - "onnx" (.onnx)
            use_onnx (bool): Whether to convert and save model in ONNX format (default: False)
            output_path (str): Directory to save the model file (default: "./")

        Returns:
            str: Full path to the saved model file

        Raises:
            ModelError: If model cannot be saved or converted to ONNX
            CompetitionError: If no competition is loaded

        Note:
            - File extension is automatically added based on model_type
            - If use_onnx=True, model will be converted and saved in ONNX format regardless of original type

        Examples:
            >>> # Save PyTorch model
            >>> model = torch.load("model.pt")
            >>> path = client.save_model(
            ...     name="my_model",
            ...     model=model,
            ...     model_type="pytorch",
            ...     output_path="./models"
            ... )  # Saves to ./models/my_model.pt
            >>> print(path)
            './models/my_model.pt'

            >>> # Save model in ONNX format
            >>> path = client.save_model(
            ...     name="my_model",
            ...     model=model,
            ...     model_type="pytorch",
            ...     use_onnx=True,
            ...     output_path="./models"
            ... )  # Saves to ./models/my_model.onnx
        """
        self._check_setup()
        self._console.print()

        with self._console.status("Setting up model...") as status:
            env = self._make_new_env()

            model_manager = ModelManager(
                console=self._console,
                env=env,
                model=model,
                model_type=model_type,
                algorithm=algorithm,
            )

            file_extension = {
                "stable_baselines3": ".zip",
                "pytorch": ".pt",
                "tensorflow": ".pb",
                "keras": ".keras",
                "onnx": ".onnx",
            }.get("onnx" if use_onnx else model_manager.model_type, "")

            save_path = f"{output_path}/{name}{file_extension}"
            os.makedirs(output_path, exist_ok=True)

            status.update("Saving model...")
            model_manager.save_model(save_path, use_onnx=use_onnx)

            self._console.success(f"Model saved to {save_path}")

        return save_path

    # ---- Package Methods ----
    def get_package(self, package: str) -> str:
        """
        Gets information about a specific package.

        Args:
            package (str): Name of the package to get information about

        Returns:
            PackageType: Package information including:
                - id: Package ID
                - name: Package name
                - description: Package description
                - version: Package version
            None: If package is not found

        Examples:
            >>> info = client.get_package("sai-pygame")
            >>> if info:
            ...     print(f"Latest version: {info['version']}")
        """
        self._check_setup()

        return self._api.package.get(package)  # type: ignore

    def update_package(self, package: str) -> None:
        """
        Updates a package to its latest version.

        Args:
            package (str): Name of the package to update

        Raises:
            PackageError: If the package cannot be updated

        Note: If package is an editable install, update will be skipped

        Examples:
            >>> client.update_package("sai-pygame")
        """
        self._check_setup()

        with self._console.status("Updating package...") as status:
            self._package_control.update(package, status)

    def install_package(self, package: str) -> None:
        """
        Installs a package if not already installed.

        Args:
            package (str): Name of the package to install

        Raises:
            PackageError: If the package cannot be installed

        Examples:
            >>> client.install_package("sai-pygame")
        """
        self._check_setup()

        with self._console.status("Installing package...") as status:
            self._package_control.update(package, status)

    def uninstall_package(self, package: str) -> None:
        """
        Uninstalls a package.

        Args:
            package (str): Name of the package to uninstall

        Raises:
            PackageError: If the package cannot be uninstalled

        Examples:
            >>> client.uninstall_package("sai-pygame")
        """
        self._check_setup()

        with self._console.status("Uninstalling package...") as status:
            self._package_control.uninstall(package, status)

    def list_packages(self, show_table: bool = True):
        """
        Lists all available packages and their installation status.

        Args:
            show_table (bool): Whether to display a formatted table of packages

        Returns:
            list[PackageType]: List of package information including:
                - id: Package ID
                - name: Package name
                - description: Package description
                - version: Latest version available

                Note: When show_table=True, displays additional information:
                    - Installed Version: Currently installed version
                    - Latest Version: Latest available version
                    - SAIStatus: Up to date/Update available/Not installed
                    - Install Type: Editable/Regular/Not installed

        Examples:
            >>> # Show table and get data
            >>> packages = client.list_packages()
            >>>
            >>> # Get data only
            >>> packages = client.list_packages(show_table=False)
            >>> for pkg in packages:
            ...     print(f"{pkg['name']}: {pkg['version']}")
        """
        self._check_setup()
        self._console.print()

        with self._console.status("Loading packages...") as status:
            packages = self._api.package.list()
            if not packages:
                self._console.warning("No packages found.")
                return []

            if show_table:
                status.update("Displaying packages...")
                table = self._console.table("Available Packages")

                table.add_column("Name", style="cyan")
                table.add_column("Installed Version", style="yellow")
                table.add_column("Latest Version", style="green")
                table.add_column("Status", style="magenta")
                table.add_column("Install Type", style="blue")

                for package in packages:
                    latest_version = package.get("version")
                    installed_version = self._package_control._get_package_version(
                        package["name"]
                    )

                    is_latest = latest_version == installed_version
                    is_installed = installed_version is not None
                    is_editable = self._package_control._is_editable_install(
                        package["name"]
                    )

                    status = (
                        "Up to date"
                        if is_latest
                        else "Update available"
                        if is_installed
                        else "Not installed"
                    )

                    install_type = (
                        "Editable"
                        if is_editable
                        else "Regular"
                        if is_installed
                        else "—"
                    )

                    table.add_row(
                        package.get("name"),
                        installed_version or "Not installed",
                        latest_version or "Unknown",
                        status,
                        install_type,
                    )

                self._console.print(table)
                self._console.print()

            return packages

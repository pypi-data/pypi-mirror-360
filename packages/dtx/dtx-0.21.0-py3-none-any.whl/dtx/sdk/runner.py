"""
High-level SDK interface for red-team evaluations (builder edition).

Quick demo
----------
from dtx.sdk.runner import DtxRunner, DtxRunnerConfigBuilder
from dtx.plugins.providers.dummy.echo import EchoAgent   # toy agent

cfg = (
    DtxRunnerConfigBuilder()
      .agent(EchoAgent())
      .max_prompts(5)
      .build()              # no plan / plan_file / dataset supplied
)

report = DtxRunner(cfg).run()
print(report.json(indent=2))
"""

from __future__ import annotations

from typing import List, Optional
import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from dtx.cli.runner import RedTeamTestRunner
from dtx.cli.planner import RedTeamPlanGenerator, PlanInput
from dtx.cli.scoping import RedTeamScopeCreator, ScopeInput
from dtx.cli.console_output import BaseResultCollector
from dtx.plugins.providers.base.agent import BaseAgent

from dtx_models.analysis import RedTeamPlan, PromptDataset
from dtx_models.evaluator import EvaluatorInScope
from dtx_models.results import EvalReport
from dtx_models.tactic import PromptMutationTactic
from dtx_models.providers.base import ProviderType
from dtx.cli.providers import ProviderFactory


# --------------------------------------------------------------------------- #
#  Fallback / dummy collector                                                 #
# --------------------------------------------------------------------------- #

class _NullCollector(BaseResultCollector):
    """No-op collector used when the user does not supply one."""
    def __init__(self) -> None:
        self.results: list = []

    def add_result(self, result) -> None:   # noqa: ANN001
        self.results.append(result)

    def finalize(self) -> None:             # noqa: D401
        pass


# --------------------------------------------------------------------------- #
#  CONFIG DATA CLASS                                                          #
# --------------------------------------------------------------------------- #

class DtxRunnerConfig(BaseModel):
    """
    Immutable configuration consumed by `DtxRunner`.
    Prefer using `DtxRunnerConfigBuilder()` to construct it fluently.
    """
    # --- mandatory ---
    agent: BaseAgent

    # --- optional ---
    collector: Optional[BaseResultCollector] = None
    plan: Optional[RedTeamPlan] = None
    plan_file: Optional[str] = None
    dataset: PromptDataset = PromptDataset.HF_JAILBREAKV   # <-- default dataset!

    tactics: Optional[List[PromptMutationTactic]] = None
    evaluator: Optional[EvaluatorInScope] = None

    max_prompts: int = 20
    max_prompts_per_plugin: int = 5
    max_goals_per_plugin: int = 2

    save_yaml_path: Optional[str] = None
    save_json_path: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def _validate(cls, values):
        # If both plan and plan_file are empty, dataset *always* has a value (default),
        # so the config is valid.
        return values


# --------------------------------------------------------------------------- #
#  CONFIG BUILDER                                                             #
# --------------------------------------------------------------------------- #

class DtxRunnerConfigBuilder:
    """
    Fluent builder for `DtxRunnerConfig`.
    Defaults to `PromptDataset.HF_JAILBREAKV` if no dataset is set.
    """

    def __init__(self) -> None:
        self._data: dict = {}

    # ---------- required --------- #
    def agent(self, agent: BaseAgent) -> "DtxRunnerConfigBuilder":
        self._data["agent"] = agent
        return self


    def agent_from_provider(
        self,
        provider_type: ProviderType,
        url: str = "",
    ) -> "DtxRunnerConfigBuilder":
        """
        Instantiate a BaseAgent from <provider_type, url/model> and store it
        directly in the config.

        Example
        -------
        cfg = (
            DtxRunnerConfigBuilder()
              .agent_from_provider(ProviderType.OPENAI, "gpt-4o-mini")
              .max_prompts(3)
              .build()
        )
        """
        scope = RedTeamScopeCreator(
            ScopeInput(description="Builder-generated provider scope")
        ).run()

        agent = ProviderFactory().get_agent(
            scope=scope,
            provider_type=provider_type,
            url=url,
        )

        if not agent.is_available():
            raise Exception("Agent is not evailable. Set required API keys")
        self._data["agent"] = agent
        return self


    # ---------- plan selection ---- #
    def plan(self, plan: RedTeamPlan) -> "DtxRunnerConfigBuilder":
        self._data["plan"] = plan
        return self

    def plan_file(self, path: str) -> "DtxRunnerConfigBuilder":
        self._data["plan_file"] = path
        return self

    def dataset(self, ds: PromptDataset) -> "DtxRunnerConfigBuilder":
        self._data["dataset"] = ds
        return self

    # ---------- optional overrides #
    def collector(self, collector: BaseResultCollector) -> "DtxRunnerConfigBuilder":
        self._data["collector"] = collector
        return self

    def tactics(self, tactics: List[PromptMutationTactic]) -> "DtxRunnerConfigBuilder":
        self._data["tactics"] = tactics
        return self

    def evaluator(self, evaluator: EvaluatorInScope) -> "DtxRunnerConfigBuilder":
        self._data["evaluator"] = evaluator
        return self

    # ---------- execution limits --- #
    def max_prompts(self, n: int) -> "DtxRunnerConfigBuilder":
        self._data["max_prompts"] = n
        return self

    def max_prompts_per_plugin(self, n: int) -> "DtxRunnerConfigBuilder":
        self._data["max_prompts_per_plugin"] = n
        return self

    def max_goals_per_plugin(self, n: int) -> "DtxRunnerConfigBuilder":
        self._data["max_goals_per_plugin"] = n
        return self

    # ---------- output paths -------- #
    def save_yaml(self, path: str) -> "DtxRunnerConfigBuilder":
        self._data["save_yaml_path"] = path
        return self

    def save_json(self, path: str) -> "DtxRunnerConfigBuilder":
        self._data["save_json_path"] = path
        return self

    # ---------- finalization -------- #
    def build(self) -> DtxRunnerConfig:
        """Return a validated `DtxRunnerConfig` with sensible defaults."""
        # Auto-inject defaults if missing
        self._data.setdefault("dataset", PromptDataset.HF_JAILBREAKV)
        self._data.setdefault("collector", _NullCollector())

        try:
            return DtxRunnerConfig(**self._data)
        except ValidationError as e:
            raise ValueError(f"Invalid DtxRunnerConfig: {e}") from e


# --------------------------------------------------------------------------- #
#  MAIN RUNNER                                                                #
# --------------------------------------------------------------------------- #

class DtxRunner:
    """Executes a red-team evaluation per the supplied config."""

    def __init__(self, cfg: DtxRunnerConfig) -> None:
        self.cfg = cfg
        self._report: Optional[EvalReport] = None

    # --------------------------- PUBLIC API -------------------------------- #

    def run(self) -> EvalReport:
        collector = self.cfg.collector or _NullCollector()     # safety net
        plan = self._load_or_generate_plan()
        self._report = self._execute_plan(plan, collector)
        self._maybe_persist()
        return self._report

    # -------------------------- INTERNALS ---------------------------------- #

    def _load_or_generate_plan(self) -> RedTeamPlan:
        if self.cfg.plan:
            return self.cfg.plan
        if self.cfg.plan_file:
            return RedTeamPlanGenerator.load_yaml(self.cfg.plan_file)

        scope = RedTeamScopeCreator(ScopeInput(description="SDK-generated scope")).run()
        scope.redteam.max_prompts = self.cfg.max_prompts
        scope.redteam.max_prompts_per_plugin = self.cfg.max_prompts_per_plugin
        scope.redteam.max_goals_per_plugin = self.cfg.max_goals_per_plugin

        if self.cfg.evaluator:
            scope.redteam.global_evaluator = self.cfg.evaluator

        plan_cfg = PlanInput(dataset=self.cfg.dataset)
        return RedTeamPlanGenerator(scope=scope, config=plan_cfg).run()

    def _execute_plan(
        self,
        plan: RedTeamPlan,
        collector: BaseResultCollector,
    ) -> EvalReport:
        runner = RedTeamTestRunner()
        return runner.run(
            plan=plan,
            agent=self.cfg.agent,
            collector=collector,
            override_tactics=self.cfg.tactics,
            max_prompts=self.cfg.max_prompts,
        )

    def _maybe_persist(self) -> None:
        if not self._report:
            return
        if self.cfg.save_yaml_path:
            with open(self.cfg.save_yaml_path, "w") as fh:
                yaml.dump(self._report.model_dump(), fh, default_flow_style=False)
        if self.cfg.save_json_path:
            with open(self.cfg.save_json_path, "w") as fh:
                fh.write(self._report.model_dump_json(indent=2))


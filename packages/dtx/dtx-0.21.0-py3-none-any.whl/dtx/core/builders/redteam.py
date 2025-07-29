from typing import List, Optional, Union

from dtx_models.evaluator import EvaluatorInScope
from dtx_models.providers.gradio import GradioProvider
from dtx_models.providers.hf import HFProvider
from dtx_models.providers.http import HttpProvider
from dtx_models.providers.litellm import LitellmProvider
from dtx_models.providers.ollama import OllamaProvider
from dtx_models.providers.openai import OpenaiProvider
from dtx_models.scope import (
    AgentInfo,
    PluginInScopeConfig,
    PluginsInScope,
    ProviderVars,
    RedTeamScope,
    RedTeamSettings,
)
from dtx_models.tactic import PromptMutationTactic
from dtx_models.template.prompts.langhub import LangHubPromptTemplate
from dtx_models.repo.plugin import Plugin, PluginRepo


class RedTeamScopeBuilder:
    """
    Flexible Builder class for RedTeamScope with full configurability.
    """

    def __init__(self):
        # Core components
        self.agent: Optional[AgentInfo] = None
        self.plugins: PluginsInScope = PluginsInScope(plugins=[])
        self.num_tests: int = 5

        # Extended components
        self.providers: List[
            Union[
                HttpProvider,
                HFProvider,
                GradioProvider,
                OllamaProvider,
                OpenaiProvider,
                LitellmProvider,
            ]
        ] = []

        self.prompts: List[LangHubPromptTemplate] = []
        self.environments: List[ProviderVars] = []

        self.tactics: List[PromptMutationTactic] = []
        self.global_evaluator: Optional[EvaluatorInScope] = None

    def set_agent(self, agent: AgentInfo):
        self.agent = agent
        return self

    def set_num_tests(self, num_tests: int):
        self.num_tests = num_tests
        return self

    def add_plugin(self, plugin: Union[str, PluginInScopeConfig]):
        self.plugins.plugins.append(
            plugin if isinstance(plugin, (str, PluginInScopeConfig)) else plugin.id
        )
        return self

    def set_plugins(self, plugins: List[Union[str, PluginInScopeConfig]]):
        self.plugins.plugins = plugins
        return self

    def add_plugins_from_repo(self, keywords: Optional[List[str]] = None):
        """
        Add multiple plugins from the PluginRepo, optionally filtered by keywords.
        If no keywords are provided, add all plugins.
        """
        all_plugins: List[Plugin] = PluginRepo.get_all_plugins()

        if keywords:
            keywords_lower = [kw.lower() for kw in keywords]

            matched_plugins = [
                plugin
                for plugin in all_plugins
                if any(kw in plugin.lower() for kw in keywords_lower)
            ]
        else:
            matched_plugins = all_plugins

        # Add plugins to the scope
        for plugin in matched_plugins:
            self.add_plugin(plugin)

        return self

    def add_provider(
        self,
        provider: Union[
            HttpProvider,
            HFProvider,
            GradioProvider,
            OllamaProvider,
            OpenaiProvider,
            LitellmProvider,
        ],
    ):
        self.providers.append(provider)
        return self

    def set_providers(
        self,
        providers: List[
            Union[
                HttpProvider,
                HFProvider,
                GradioProvider,
                OllamaProvider,
                OpenaiProvider,
                LitellmProvider,
            ]
        ],
    ):
        self.providers = providers
        return self

    def add_prompt(self, prompt: LangHubPromptTemplate):
        self.prompts.append(prompt)
        return self

    def set_prompts(self, prompts: List[LangHubPromptTemplate]):
        self.prompts = prompts
        return self

    def add_environment(self, environment: ProviderVars):
        self.environments.append(environment)
        return self

    def set_environments(self, environments: List[ProviderVars]):
        self.environments = environments
        return self

    def set_tactics(self, tactics: List[PromptMutationTactic]):
        self.tactics = tactics
        return self

    def set_global_evaluator(self, evaluator: EvaluatorInScope):
        self.global_evaluator = evaluator
        return self

    def build(self) -> RedTeamScope:
        if not self.agent:
            raise ValueError("Agent must be set before building RedTeamScope.")

        redteam_settings = RedTeamSettings(
            max_prompts_per_plugin=self.num_tests,
            max_plugins=self.num_tests,
            max_prompts_per_tactic=self.num_tests,
            plugins=self.plugins,
            tactics=self.tactics,
            global_evaluator=self.global_evaluator,
        )

        return RedTeamScope(
            agent=self.agent,
            providers=self.providers,
            prompts=self.prompts,
            environments=self.environments,
            redteam=redteam_settings,
        )

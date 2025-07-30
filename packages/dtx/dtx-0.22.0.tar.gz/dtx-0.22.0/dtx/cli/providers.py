from dtx.core.builders.provider_vars import ProviderVarsBuilder
from dtx_models.providers.base import ProviderType
from dtx_models.providers.litellm import LitellmProvider, LitellmProviderConfig
from dtx_models.providers.ollama import OllamaProvider, OllamaProviderConfig
from dtx_models.providers.openai import OpenaiProvider, OpenaiProviderConfig
from dtx_models.scope import RedTeamScope
from dtx.plugins.providers.dummy.echo import EchoAgent
from dtx.plugins.providers.eliza.agent import ElizaAgent
from dtx.plugins.providers.gradio.agent import GradioAgent
from dtx.plugins.providers.http.agent import HttpAgent
from dtx.plugins.providers.litellm.agent import LitellmAgent
from dtx.plugins.providers.ollama.agent import OllamaAgent
from dtx.plugins.providers.openai.agent import OpenAIAgent


class ProviderFactory:
    def _build_env_vars(self, scope):
        env_vars = {}
        if scope.environments:
            env_vars = next(ProviderVarsBuilder(scope.environments[0]).build(), {})
        return env_vars

    def get_agent(
        self,
        scope: RedTeamScope,
        provider_type: ProviderType,
        url: str = "",
    ):
        from dtx.config import globals
        from dtx.plugins.providers.hf.agent import HFAgent

        if provider_type == ProviderType.ECHO:
            return EchoAgent()
        elif provider_type == ProviderType.ELIZA:
            return ElizaAgent(url)
        elif provider_type == ProviderType.HF:
            model = globals.get_llm_models().get_huggingface_model(url)
            return HFAgent(model)
        elif provider_type == ProviderType.HTTP:
            env_vars = self._build_env_vars(scope)
            return HttpAgent(provider=scope.providers[0], vars=env_vars)
        elif provider_type == ProviderType.GRADIO:
            env_vars = self._build_env_vars(scope)
            return GradioAgent(provider=scope.providers[0], vars=env_vars)
        elif provider_type == ProviderType.OLLAMA:
            config = OllamaProviderConfig(model=url)
            provider = OllamaProvider(config=config)
            return OllamaAgent(provider)
        elif provider_type == ProviderType.OPENAI:
            config = OpenaiProviderConfig(model=url)
            provider = OpenaiProvider(config=config)
            if scope.prompts:
                prompt_template = scope.prompts[0]
            else:
                prompt_template = None
            return OpenAIAgent(provider, prompt_template=prompt_template)
        elif provider_type == ProviderType.LITE_LLM:
            if scope.prompts:
                prompt_template = scope.prompts[0]
            else:
                prompt_template = None
            config = LitellmProviderConfig(model=url)
            provider = LitellmProvider(config=config)
            return LitellmAgent(provider, prompt_template=prompt_template)
        # elif provider_type == ProviderType.GROQ:
        #     config = GroqProviderConfig(model=url)
        #     provider = GroqProvider(config=config)
        #     return GroqAgent(provider)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

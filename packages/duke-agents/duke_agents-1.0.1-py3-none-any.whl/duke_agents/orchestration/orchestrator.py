from typing import List, Dict, Any, Union, Optional
from ..agents.base_agent import BaseAgent
from ..agents.atomic_agent import AtomicAgent
from ..agents.codeact_agent import CodeActAgent
from ..models.atomic_models import AtomicInput, AtomicOutput
from ..models.codeact_models import CodeActInput, CodeActOutput
from .context_manager import ContextManager
from ..llm.mistral_client import MistralClient
import logging
import json


class Orchestrator:
    """Orchestrateur principal pour gérer les workflows d'agents"""

    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        self.agents = {}
        self.llm_client = MistralClient()
        self.logger = logging.getLogger("Orchestrator")

    def register_agent(self, agent: BaseAgent) -> None:
        """Enregistre un agent"""
        self.agents[agent.name] = agent

    def execute_linear_workflow(self,
                                workflow: List[Dict[str, Any]]) -> List[Union[AtomicOutput, CodeActOutput]]:
        """Exécute un workflow linéaire"""
        results = []

        for step in workflow:
            agent_name = step['agent']
            input_type = step['input_type']
            input_data = step['input_data']

            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not registered")

            agent = self.agents[agent_name]

            # Préparer l'input selon le type d'agent
            if isinstance(agent, CodeActAgent):
                agent_input = CodeActInput(
                    prompt=input_data.get('prompt', ''),
                    data_context=self.context_manager.get_agent_context(agent_name),
                    memory=self.context_manager.get_memory()
                )
                result = agent.run(agent_input)

            elif isinstance(agent, AtomicAgent):
                agent_input = AtomicInput(
                    task_id=input_data.get('task_id', f'task_{len(results)}'),
                    parameters=input_data.get('parameters', {}),
                    context=self.context_manager.get_agent_context(agent_name),
                    memory=self.context_manager.get_memory()
                )
                result = agent.run(agent_input)

            else:
                raise ValueError(f"Unknown agent type: {type(agent)}")

            results.append(result)

            # Mettre à jour le contexte si succès
            if result.success:
                self.context_manager.update_agent_context(
                    agent_name,
                    {'last_result': result.result}
                )

            # Arrêter si échec et pas de fallback
            if not result.success and not step.get('continue_on_failure', False):
                self.logger.error(f"Workflow stopped due to failure in {agent_name}")
                break

        return results

    def execute_llm_driven_workflow(self,
                                    max_steps: int = 10) -> List[Union[AtomicOutput, CodeActOutput]]:
        """Exécute un workflow piloté par LLM"""
        results = []
        step = 0

        while step < max_steps:
            # Demander au LLM quelle est la prochaine action
            next_action = self._get_next_action()

            if next_action is None or next_action.get('action') == 'complete':
                self.logger.info("Workflow completed by LLM decision")
                break

            # Exécuter l'action
            agent_name = next_action['agent']
            if agent_name not in self.agents:
                self.logger.error(f"Agent '{agent_name}' not found")
                break

            agent = self.agents[agent_name]

            # Préparer et exécuter selon le type
            if isinstance(agent, CodeActAgent):
                agent_input = CodeActInput(
                    prompt=next_action.get('prompt', ''),
                    data_context=self.context_manager.get_agent_context(agent_name),
                    memory=self.context_manager.get_memory()
                )
                result = agent.run(agent_input)

            elif isinstance(agent, AtomicAgent):
                agent_input = AtomicInput(
                    task_id=f'llm_task_{step}',
                    parameters=next_action.get('parameters', {}),
                    context=self.context_manager.get_agent_context(agent_name),
                    memory=self.context_manager.get_memory()
                )
                result = agent.run(agent_input)

            results.append(result)
            step += 1

        return results

    def _get_next_action(self) -> Optional[Dict[str, Any]]:
        """Demande au LLM la prochaine action"""
        prompt = f"""Based on the current workflow state, decide the next action.

User Question: {self.context_manager.workflow_memory.user_question}

Current Memory:
{self.context_manager.workflow_memory.to_context_string()}

Available Agents: {list(self.agents.keys())}

Decide the next action in JSON format:
{{
    "action": "execute" or "complete",
    "agent": "agent_name",
    "prompt": "prompt for CodeActAgent" or null,
    "parameters": {{}} for AtomicAgent or null,
    "reasoning": "why this action"
}}

If the user's question has been fully answered, use action: "complete".
"""

        response = self.llm_client.generate(
            prompt=prompt,
            temperature=0.3,
            system_prompt="You are an orchestration assistant. Always respond with valid JSON."
        )

        try:
            # Extraire le JSON de la réponse
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                action_json = json.loads(response[json_start:json_end])
                self.logger.info(f"Next action: {action_json}")
                return action_json
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse LLM response: {response}")

        return None
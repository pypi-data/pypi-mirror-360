import logging
from duke_agents.orchestration.context_manager import ContextManager
from duke_agents.orchestration.orchestrator import Orchestrator
from duke_agents.agents.atomic_agent import AtomicAgent
from duke_agents.agents.codeact_agent import CodeActAgent
from duke_agents.orchestration.utils import create_workflow_summary

# Configuration du logging
logging.basicConfig(level=logging.INFO)


# Créer un agent personnalisé
class DataAnalysisAgent(AtomicAgent):
    def process(self, input_data):
        # Logique d'analyse des données
        data = input_data.parameters.get('data', [])
        return {
            'count': len(data),
            'summary': f"Analysed {len(data)} items"
        }

    def evaluate_satisfaction(self, result, input_data):
        if result and 'count' in result:
            return 0.9
        return 0.1


# Initialiser le système
def main():
    # Question utilisateur
    user_question = "Analyse mes données de vente et génère un rapport"

    # Créer le gestionnaire de contexte
    context_manager = ContextManager(user_question)

    # Créer l'orchestrateur
    orchestrator = Orchestrator(context_manager)

    # Enregistrer les agents
    orchestrator.register_agent(DataAnalysisAgent(name="DataAnalyzer"))
    orchestrator.register_agent(CodeActAgent(name="ReportGenerator"))

    # Définir le workflow
    workflow = [
        {
            'agent': 'DataAnalyzer',
            'input_type': 'atomic',
            'input_data': {
                'task_id': 'analyze_sales',
                'parameters': {
                    'data': [100, 200, 150, 300, 250]  # Exemple de données
                }
            }
        },
        {
            'agent': 'ReportGenerator',
            'input_type': 'codeact',
            'input_data': {
                'prompt': 'Generate a Python script that creates a sales report with the analysis results'
            }
        }
    ]

    # Exécuter le workflow
    results = orchestrator.execute_linear_workflow(workflow)

    # Afficher le résumé
    summary = create_workflow_summary(results)
    print(f"Workflow Summary: {summary}")

    # Ajouter le feedback utilisateur
    context_manager.add_user_feedback("Le rapport était très utile, merci!")

    # Sauvegarder l'état
    context_manager.save_state("workflow_state.json")


if __name__ == "__main__":
    main()
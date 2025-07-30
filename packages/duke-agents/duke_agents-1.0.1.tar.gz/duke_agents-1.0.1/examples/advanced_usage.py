"""
Exemples d'utilisation de DUKE Agents après publication sur PyPI
"""

# ============================================
# 1. INSTALLATION ET IMPORT BASIQUE
# ============================================

# Installation via pip
# $ pip install duke-agents

# Import standard
from duke_agents import AtomicAgent, CodeActAgent, Orchestrator, ContextManager

# Import avec alias
import duke_agents as duke

# Imports spécifiques
from duke_agents.models import WorkflowMemory, AtomicInput, CodeActOutput
from duke_agents.agents.base_agent import BaseAgent
from duke_agents.config import Config

# ============================================
# 2. CONFIGURATION INITIALE
# ============================================

import os
from duke_agents import Config

# Méthode 1: Variables d'environnement
os.environ["MISTRAL_API_KEY"] = "your-mistral-api-key"
os.environ["DUKE_MAX_RETRIES"] = "5"
os.environ["DUKE_SATISFACTION_THRESHOLD"] = "0.8"

# Méthode 2: Fichier .env
from dotenv import load_dotenv
load_dotenv(".env.duke")

# Méthode 3: Configuration programmatique
Config.MISTRAL_API_KEY = "your-mistral-api-key"
Config.MAX_RETRIES = 5
Config.SATISFACTION_THRESHOLD = 0.8

# Validation de la configuration
Config.validate()  # Lève une exception si configuration invalide

# ============================================
# 3. USAGE SIMPLE - ATOMIC AGENT
# ============================================

from duke_agents import AtomicAgent, ContextManager, Orchestrator
from duke_agents.models import AtomicInput

def simple_atomic_example():
    """Exemple simple avec AtomicAgent"""
    
    # 1. Initialiser le contexte
    context = ContextManager("Traiter des données clients")
    
    # 2. Créer l'orchestrateur
    orchestrator = Orchestrator(context)
    
    # 3. Créer et enregistrer un agent
    data_processor = AtomicAgent(name="data_processor")
    orchestrator.register_agent(data_processor)
    
    # 4. Définir le workflow
    workflow = [{
        'agent': 'data_processor',
        'input_type': 'atomic',
        'input_data': {
            'task_id': 'process_001',
            'parameters': {
                'action': 'clean',
                'data': ['item1', 'item2', 'item3']
            }
        }
    }]
    
    # 5. Exécuter
    results = orchestrator.execute_linear_workflow(workflow)
    
    # 6. Traiter les résultats
    for result in results:
        if result.success:
            print(f"Succès: {result.result}")
            print(f"Score de satisfaction: {result.satisfaction_score}")
        else:
            print(f"Erreur: {result.error}")
    
    return results

# ============================================
# 4. USAGE AVANCÉ - CODE GENERATION
# ============================================

from duke_agents import CodeActAgent, ContextManager, Orchestrator

def code_generation_example():
    """Exemple de génération de code avec CodeActAgent"""
    
    # Contexte pour génération de code
    context = ContextManager("Générer du code d'analyse de données")
    orchestrator = Orchestrator(context)
    
    # Agent de génération de code
    code_agent = CodeActAgent(name="code_generator")
    orchestrator.register_agent(code_agent)
    
    # Données de contexte pour le code
    data_context = {
        'dataframe': 'sales_data',
        'columns': ['date', 'product', 'quantity', 'revenue'],
        'requirements': 'Calculer les ventes totales par produit'
    }
    
    # Mettre à jour le contexte global
    orchestrator.context_manager.update_global_context(data_context)
    
    # Workflow de génération
    workflow = [{
        'agent': 'code_generator',
        'input_type': 'codeact',
        'input_data': {
            'prompt': """
            Générer une fonction Python qui:
            1. Prend un DataFrame pandas en entrée
            2. Calcule les ventes totales par produit
            3. Retourne un dictionnaire avec les résultats triés
            Inclure la gestion d'erreurs et des tests.
            """
        }
    }]
    
    # Exécuter
    results = orchestrator.execute_linear_workflow(workflow)
    
    # Afficher le code généré
    if results[0].success:
        print("Code généré:")
        print(results[0].generated_code)
        print("\nRésultat d'exécution:")
        print(results[0].execution_result)
    
    return results[0]

# ============================================
# 5. AGENT PERSONNALISÉ
# ============================================

from duke_agents.agents import BaseAgent
from duke_agents.models import AtomicInput, AtomicOutput
import requests

class WeatherAgent(BaseAgent):
    """Agent personnalisé pour récupérer la météo"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(name="weather_agent", **kwargs)
        self.api_key = api_key
        
    def process(self, input_data: AtomicInput) -> dict:
        """Récupère les données météo pour une ville"""
        city = input_data.parameters.get('city', 'Paris')
        
        # Appel API météo (exemple)
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather",
            params={'q': city, 'appid': self.api_key}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'city': city,
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description']
            }
        else:
            raise Exception(f"Erreur API: {response.status_code}")
            
    def evaluate_satisfaction(self, result: dict, input_data: AtomicInput) -> float:
        """Évalue la qualité du résultat"""
        if result and 'temperature' in result:
            return 0.9
        return 0.0

def custom_agent_example():
    """Utilisation d'un agent personnalisé"""
    
    # Initialisation
    context = ContextManager("Obtenir la météo")
    orchestrator = Orchestrator(context)
    
    # Créer et enregistrer l'agent personnalisé
    weather_agent = WeatherAgent(api_key="your-weather-api-key")
    orchestrator.register_agent(weather_agent)
    
    # Workflow
    workflow = [{
        'agent': 'weather_agent',
        'input_type': 'atomic',
        'input_data': {
            'task_id': 'weather_check',
            'parameters': {'city': 'Paris'}
        }
    }]
    
    # Exécuter
    results = orchestrator.execute_linear_workflow(workflow)
    return results

# ============================================
# 6. WORKFLOW MULTI-AGENTS
# ============================================

def multi_agent_workflow():
    """Workflow complexe avec plusieurs agents"""
    
    # Contexte pour analyse complète
    context = ContextManager(
        "Analyser les ventes et générer un rapport automatique"
    )
    orchestrator = Orchestrator(context)
    
    # Créer plusieurs agents
    data_agent = AtomicAgent("data_loader")
    analysis_agent = CodeActAgent("data_analyzer")
    report_agent = CodeActAgent("report_generator")
    
    # Enregistrer tous les agents
    for agent in [data_agent, analysis_agent, report_agent]:
        orchestrator.register_agent(agent)
    
    # Workflow en plusieurs étapes
    workflow = [
        {
            'agent': 'data_loader',
            'input_type': 'atomic',
            'input_data': {
                'task_id': 'load_sales',
                'parameters': {
                    'source': 'sales_2024.csv',
                    'validate': True
                }
            }
        },
        {
            'agent': 'data_analyzer',
            'input_type': 'codeact',
            'input_data': {
                'prompt': """
                Analyser les données de ventes chargées:
                1. Calculer les statistiques par mois
                2. Identifier les produits top 10
                3. Détecter les tendances
                """
            }
        },
        {
            'agent': 'report_generator',
            'input_type': 'codeact',
            'input_data': {
                'prompt': """
                Générer un rapport HTML avec:
                1. Résumé exécutif
                2. Graphiques des tendances
                3. Tableau des top produits
                4. Recommandations
                """
            }
        }
    ]
    
    # Exécuter le workflow complet
    results = orchestrator.execute_linear_workflow(workflow)
    
    # Sauvegarder le rapport si succès
    if all(r.success for r in results):
        with open("sales_report.html", "w") as f:
            f.write(results[-1].execution_result)
        print("Rapport généré: sales_report.html")
    
    return results

# ============================================
# 7. WORKFLOW PILOTÉ PAR LLM
# ============================================

def llm_driven_workflow():
    """Workflow où le LLM décide des prochaines étapes"""
    
    # Question complexe nécessitant plusieurs étapes
    context = ContextManager(
        "Créer une application web de suivi de budget personnel"
    )
    orchestrator = Orchestrator(context)
    
    # Enregistrer plusieurs agents spécialisés
    agents = {
        'requirements_analyst': AtomicAgent("requirements_analyst"),
        'database_designer': CodeActAgent("database_designer"),
        'backend_developer': CodeActAgent("backend_developer"),
        'frontend_developer': CodeActAgent("frontend_developer"),
        'tester': CodeActAgent("tester")
    }
    
    for agent in agents.values():
        orchestrator.register_agent(agent)
    
    # Laisser le LLM orchestrer le workflow
    results = orchestrator.execute_llm_driven_workflow(max_steps=10)
    
    # Afficher le parcours d'exécution
    print("Étapes exécutées par le LLM:")
    for i, result in enumerate(results):
        agent_name = result.memory.records[-1].agent_name
        print(f"{i+1}. {agent_name}: {'✓' if result.success else '✗'}")
    
    return results

# ============================================
# 8. GESTION DE LA MÉMOIRE ET DU FEEDBACK
# ============================================

def memory_and_feedback_example():
    """Exemple d'utilisation de la mémoire et du feedback"""
    
    # Initialisation
    context = ContextManager("Optimiser un algorithme")
    orchestrator = Orchestrator(context)
    
    # Agent d'optimisation
    optimizer = CodeActAgent("optimizer")
    orchestrator.register_agent(optimizer)
    
    # Première tentative
    workflow = [{
        'agent': 'optimizer',
        'input_type': 'codeact',
        'input_data': {
            'prompt': "Implémenter un tri rapide optimisé"
        }
    }]
    
    results = orchestrator.execute_linear_workflow(workflow)
    
    # Ajouter du feedback utilisateur
    context.add_user_feedback(
        "L'algorithme est correct mais pourrait être plus rapide pour les petits tableaux"
    )
    
    # Deuxième tentative avec le feedback en mémoire
    workflow[0]['input_data']['prompt'] = """
    Améliorer l'implémentation précédente du tri rapide
    en tenant compte du feedback utilisateur
    """
    
    results2 = orchestrator.execute_linear_workflow(workflow)
    
    # Afficher l'évolution
    print("Historique de la mémoire:")
    print(context.get_memory().to_context_string())
    
    # Sauvegarder l'état pour réutilisation future
    context.save_state("optimization_session.json")
    
    return results2

# ============================================
# 9. INTÉGRATION DANS UNE APPLICATION
# ============================================

from flask import Flask, request, jsonify
from duke_agents import CodeActAgent, ContextManager, Orchestrator

app = Flask(__name__)

# Initialisation globale
context = ContextManager("Assistant de développement")
orchestrator = Orchestrator(context)
code_agent = CodeActAgent("assistant")
orchestrator.register_agent(code_agent)

@app.route('/generate_code', methods=['POST'])
def generate_code_endpoint():
    """Endpoint API pour génération de code"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        # Workflow de génération
        workflow = [{
            'agent': 'assistant',
            'input_type': 'codeact',
            'input_data': {'prompt': prompt}
        }]
        
        results = orchestrator.execute_linear_workflow(workflow)
        
        if results[0].success:
            return jsonify({
                'success': True,
                'code': results[0].generated_code,
                'execution_result': str(results[0].execution_result),
                'satisfaction_score': results[0].satisfaction_score
            })
        else:
            return jsonify({
                'success': False,
                'error': results[0].error
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# 10. TESTS UNITAIRES
# ============================================

import pytest
from unittest.mock import Mock, patch
from duke_agents import AtomicAgent, ContextManager
from duke_agents.models import AtomicInput, AtomicOutput

def test_atomic_agent():
    """Test unitaire pour AtomicAgent"""
    
    # Créer un agent de test
    agent = AtomicAgent("test_agent")
    
    # Préparer l'input
    context = ContextManager("Test")
    input_data = AtomicInput(
        task_id="test_001",
        parameters={"action": "test"},
        context={},
        memory=context.get_memory()
    )
    
    # Mock du process
    with patch.object(agent, 'process', return_value="Test result"):
        with patch.object(agent, 'evaluate_satisfaction', return_value=0.9):
            result = agent.run(input_data)
    
    # Assertions
    assert result.success is True
    assert result.result == "Test result"
    assert result.satisfaction_score == 0.9
    assert len(result.memory.records) == 1

# ============================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================

if __name__ == "__main__":
    # Configurer l'API key
    os.environ["MISTRAL_API_KEY"] = "your-key-here"
    
    print("=== Exemple Simple ===")
    simple_atomic_example()
    
    print("\n=== Génération de Code ===")
    code_generation_example()
    
    print("\n=== Workflow Multi-Agents ===")
    multi_agent_workflow()
    
    print("\n=== Mémoire et Feedback ===")
    memory_and_feedback_example()
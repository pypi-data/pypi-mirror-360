import openai
from typing import List, Dict, Any, Optional
import json
import base64
import asyncio
from .logger import logging

class AIController:
    """
    Controlador para integrar capacidades de IA en PyWebWizard.
    Permite análisis de tareas y toma de decisiones basadas en IA.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Inicializa el controlador de IA.
        
        :param api_key: Clave de API de OpenAI
        :param model: Modelo de IA a utilizar (por defecto: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key
        
    async def analyze_task(self, task_description: str, current_page_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analiza una tarea y devuelve una secuencia de acciones ejecutables.
        
        :param task_description: Descripción de la tarea a realizar
        :param current_page_info: Información del estado actual de la página
        :return: Lista de acciones a ejecutar
        """
        try:
            # Preparamos el mensaje para la IA
            system_prompt = """
            Eres un asistente de automatización web. Tu tarea es analizar la descripción de una tarea 
            y generar una secuencia de acciones ejecutables por PyWebWizard.
            
            Devuelve SOLO un JSON con un array de objetos, donde cada objeto representa una acción.
            Cada acción debe tener un campo 'action' que indique el tipo de acción a realizar.
            
            Ejemplo de respuesta:
            [
                {"action": "navigate", "url": "https://ejemplo.com"},
                {"action": "fill", "interface": "id", "query": "usuario", "content": "mi_usuario"},
                {"action": "click", "interface": "xpath", "query": "//button[@type='submit']"}
            ]
            """
            
            user_message = f"""
            TAREA: {task_description}
            
            INFORMACIÓN DE LA PÁGINA ACTUAL:
            {json.dumps(current_page_info, indent=2, ensure_ascii=False)}
            
            Genera una lista de acciones en formato JSON.
            """
            
            # Realizamos la llamada a la API de OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Extraemos y validamos la respuesta
            content = response.choices[0].message['content']
            actions = json.loads(content)
            
            if not isinstance(actions, list):
                actions = [actions]
                
            return actions
            
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar la respuesta de la IA: {str(e)}")
            logging.debug(f"Respuesta recibida: {content}")
            raise ValueError("La IA no devolvió un JSON válido")
            
        except Exception as e:
            logging.error(f"Error en el análisis de la tarea: {str(e)}")
            raise

    async def decide_next_action(self, current_state: Dict[str, Any], available_actions: List[str]) -> Dict[str, Any]:
        """
        Decide la siguiente acción a realizar basada en el estado actual.
        
        :param current_state: Estado actual de la aplicación/página web
        :param available_actions: Lista de acciones disponibles
        :return: Acción a realizar
        """
        try:
            system_prompt = """
            Eres un asistente de automatización web. Tu tarea es analizar el estado actual 
            de la página y decidir la mejor acción a realizar a continuación.
            
            Devuelve SOLO un JSON con la acción a realizar.
            Ejemplo de respuesta:
            {"action": "click", "interface": "xpath", "query": "//button[contains(text(),'Siguiente')]"}
            """
            
            user_message = f"""
            ESTADO ACTUAL:
            {json.dumps(current_state, indent=2, ensure_ascii=False)}
            
            ACCIONES DISPONIBLES:
            {json.dumps(available_actions, indent=2, ensure_ascii=False)}
            
            ¿Cuál es la mejor acción a realizar? Responde SOLO con el JSON de la acción.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            # Extraemos y validamos la respuesta
            content = response.choices[0].message['content']
            action = json.loads(content)
            
            if not isinstance(action, dict) or 'action' not in action:
                raise ValueError("La acción devuelta no tiene el formato esperado")
                
            return action
            
        except Exception as e:
            logging.error(f"Error al decidir la siguiente acción: {str(e)}")
            raise

    @staticmethod
    def _take_screenshot_as_base64(driver) -> Optional[str]:
        """
        Toma una captura de pantalla y la devuelve en formato base64.
        
        :param driver: Instancia del navegador
        :return: Imagen en base64 o None si hay un error
        """
        try:
            screenshot = driver.get_screenshot_as_base64()
            return f"data:image/png;base64,{screenshot}"
        except Exception as e:
            logging.warning(f"No se pudo tomar la captura de pantalla: {str(e)}")
            return None

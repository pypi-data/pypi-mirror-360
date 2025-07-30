from ...prompts.system_prompts import (
    chat_asistant,
    select_service,
    create_args,
    preproccess_query,
    language_prompt,
)
from ...prompts.user_prompts import query_and_data, query_and_services, service2args
from .....config.llm_config import ConfigGPT
from ...llm import LLM
from .....mcp_manager.services.service import Service
from openai import OpenAI, AsyncOpenAI
import json


class GPT(LLM):
    """
    ## GPT
    ### Args:
    - `model`: modelo de gpt que a usar
    - `max_history_len`: largo maximo del historial que se para como input al modelo
    """

    def __init__(
        self,
        model=ConfigGPT.DEFAULT_MODEL_NAME,
        max_history_len: int = 10,
    ):
        super().__init__()
        self.client = OpenAI(api_key=ConfigGPT.OPENAI_API_KEY)
        """Cliente secuencial de GPT"""
        self.asyncclient = AsyncOpenAI(api_key=ConfigGPT.OPENAI_API_KEY)
        """Cliente asincrono de GPT"""
        self.max_len_history: int = max_history_len
        """Maxima cantidad de mensajes previos que se le pasan como input"""
        self.chat_history: list[list[dict[str, str]]] = []
        """Historial del chat asosiado a esta instancia de GPT, en forma lista de listas, por ejemplo 
        ```
        chat_history: str = [
            [
                {"role": "user", "content": "query1"},
                {"role": "assistant", "content": "response1"}
            ],
            [
                {"role": "user", "content": "query2"},
                {"role": "assistant", "content": "response2"}
            ]
        ]
        ```
        """
        self.model: str = model
        self.current_price: float = 0

    def append_chat_history(self):
        """Agrega una historia vacia para crear el espacio"""
        self.chat_history.append([])
        self.chat_history[-1].append({})

    def call_completion(
        self, system_message: str, query: str, json_format: bool = False
    ):
        """ """
        self.chat_history[-1][0] = {"role": "user", "content": query}

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_message}
        ] + [
            message
            for messages in self.chat_history[-self.max_len_history :]
            for message in messages
        ]
        if json_format:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
            )
        else:

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        self.get_price(completion.usage)
        return completion.choices[0].message.content

    def get_price(self, usage) -> float:
        """
        ### Args
            - `usage`: uso de la api retornado en el completion respuesta del llamado a la api de gpt
        ### Outs:
            - `price`: precio final del llamado a la api.
        """

        input_tokens: int = usage.prompt_tokens
        output_tokens: int = usage.completion_tokens

        input_price: float = ConfigGPT.MODEL_PRICE[self.model]["input"]
        output_price: float = ConfigGPT.MODEL_PRICE[self.model]["output"]
        price: float = input_tokens * input_price + output_tokens * output_price

        # Aumenta el valod asociado al costo de uso de la API en esta instancia de GPT
        self.current_price += price
        return price

    def preprocess_query(self, query: str) -> dict:
        system_message: str = preproccess_query(
            services=self.client_manager_mcp.get_services()
        )
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ]
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        self.get_price(completion.usage)
        response = completion.choices[0].message.content
        return json.loads(response)

    def simple_query(self, query: str, use_services_contex: bool = False) -> str:
        system_message: str = chat_asistant(
            self.client_manager_mcp.get_services() if use_services_contex else None
        ) + language_prompt(self.current_language)
        response = self.call_completion(system_message=system_message, query=query)

        # Se agrega la respuesta a la historia
        self.chat_history[-1].append({"role": "assistant", "content": response})
        return response

    def select_service(self, query: str) -> str:
        """
        Funcion encargada de seleccionar los servicios utiles para el contexto de la consulta, usando los servicios expuestos por cada uno
        de los servidores
        """
        system_message: str = select_service
        return self.call_completion(
            system_message=system_message,
            query=query_and_services(
                query=query, services=self.client_manager_mcp.get_services()
            ),
            json_format=True,
        )

    def generate_args(self, query: str, service: Service) -> str:
        """
        Funcion encargada de crear argumentos para los servicios expuestos que se usaran
        """
        system_message: str = create_args

        service = str(service)

        return self.call_completion(
            system_message=system_message,
            query=service2args(query=query, service=service),
            json_format=True,
        )

    def final_response(self, query: str, data: str | dict) -> str:
        system_message: str = chat_asistant() + language_prompt(self.current_language)
        user_message = query_and_data(query=query, data=data)

        response = self.call_completion(
            system_message=system_message,
            query=user_message,
            json_format=False,
        )

        # Se agrega la respuesta a la historia
        self.chat_history[-1].append({"role": "assistant", "content": response})
        return response

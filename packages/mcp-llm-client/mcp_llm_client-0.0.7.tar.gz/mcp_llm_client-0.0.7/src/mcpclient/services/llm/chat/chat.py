from ..llm import LLM
from ..models.openai_service.gpt import GPT
from typing import Generator
from .step import Step
from .step import Step, StepMessage, DataStep, ResponseStep, QueryStep
import json


class Chat:
    def __init__(
        self,
        name="openai",
        model="gpt4o-mini",
        len_context: int = 10,
        history: list = [],
        id: str | None = None,
    ):
        self.id = id
        self.llm: LLM = GPT(max_history_len=len_context)

    def __call__(self, query: str) -> Generator[Step]:
        yield Step(step_type=StepMessage.ANALYZE_QUERY)

        processed_query: dict = self.llm.preprocess_query(query=query)
        querys: list[str] = processed_query["querys"]
        self.llm.current_language = processed_query["language"]

        yield DataStep(data={"querys": querys})

        for query in querys:
            for step in self.proccess_query(query):
                yield step

    def proccess_query(self, query: str) -> Generator[Step]:
        """ """
        self.llm.append_chat_history()
        yield QueryStep(query)
        yield Step(step_type=StepMessage.SELECT_SERVICE)
        # Cargar los servicios utiles
        service = json.loads(self.llm.select_service(query))["service"]

        if len(service) == 0:
            yield DataStep(data={"service": None})
            yield ResponseStep(
                response=self.llm.simple_query(query, use_services_contex=True),
                data=None,
            )
            return
        else:
            yield DataStep(data={"service": service})
            service = (
                self.llm.client_manager_mcp.resources[service]
                if (self.llm.client_manager_mcp.service_type(service) == "resource")
                else (
                    self.llm.client_manager_mcp.tools[service]
                    if (self.llm.client_manager_mcp.service_type(service) == "tool")
                    else None
                )
            )

        yield Step(step_type=StepMessage.CREATE_ARGUMENTS)
        args = json.loads(self.llm.generate_args(query=query, service=service))["args"]
        data = service(args)[0].text
        yield DataStep(data={"args": args})

        response = self.llm.final_response(query, data)
        yield ResponseStep(response=response, data=data)
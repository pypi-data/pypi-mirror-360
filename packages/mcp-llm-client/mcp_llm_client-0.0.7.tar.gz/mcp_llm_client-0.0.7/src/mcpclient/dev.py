from mcpclient.services.llm.chat.chat import Chat
from mcpclient.tools.clear_console import clear_console
import os


def open_local_chat():
    clear_console()
    chat: Chat = Chat()
    print("\n")

    md: str = ""
    filename: str | None = None
    sep = os.path.sep

    while True:
        query = input("> ")
        if query == "exit" or query == "":
            if md != "":
                chats_path = f"{os.getcwd()}{sep}chats{sep}"
                os.makedirs(os.path.dirname(chats_path), exist_ok=True)
                with open(f"{chats_path}{filename}.md", "w") as file:
                    file.write(md)
            break

        if filename is None:
            filename = f"{query[:15]}..."

        md += f"# {query}"
        index = 1
        for step in chat(query):
            md += str(step)
            if step.type == "response":
                print(f"<< {step.response}")
            if step.type == "query":
                print(f">> {step.query}")
                index = 1
            if step.type == "data":
                print(f'   {str(step).replace("*", "").replace("- ", "• ")}')
            if step.type == "step":
                print(f"  {index}. {step.step}")
                index += 1
        md += "\n"

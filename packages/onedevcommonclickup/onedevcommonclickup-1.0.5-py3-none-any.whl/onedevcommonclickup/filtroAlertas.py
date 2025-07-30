import requests

# classe para buscar as tarefas no ClickUp
class ClickUpTaskFetcher:
    def __init__(self, api_token, list_id):
        self.api_token = api_token
        self.list_id = list_id
        self.headers = {"Authorization": self.api_token}

    # busca as tarefas no ClickUp
    def fetch_tasks(self):
        response = requests.get(
            f"https://api.clickup.com/api/v2/list/{self.list_id}/task?archived=false",
            headers=self.headers
        )
        data = response.json()
        tasks = data.get("tasks", [])
        return self._process_tasks(tasks)


    # busca os campos customizados no ClickUp
    def _get_custom_field(self, task, field_name):
        for field in task.get("custom_fields", []):
            if field.get("name") == field_name:
                selected_value = field.get("value")
                options = field.get("type_config", {}).get("options", [])

                if selected_value is None or not options:
                    return f"Sem {field_name}"

                # Se selected_value for índice inteiro
                if isinstance(selected_value, int) and selected_value < len(options):
                    return options[selected_value]["name"]

                # Se selected_value for ID
                for option in options:
                    if option["id"] == selected_value:
                        return option["name"]

                return str(selected_value)  # fallback: mostra o que veio
        return f"Sem {field_name}"

    # processa as tarefas
    def _process_tasks(self, tasks):
        dados_tratados = []
        for t in tasks:
            dados_tratados.append({
                "ID": t["id"],
                "Nome": t["name"],
                "Status": t["status"]["status"],
                "Descrição": t["description"],
                "Tags": t["tags"][0]['name'] if t['tags'] else "Sem tags",
                "Prioridade": t["priority"]["priority"] if t.get("priority") else "Sem prioridade",
                "Criador": t["creator"]["username"] if t.get("creator") else "Ninguém",
                "Responsáveis": [assignee["username"] for assignee in t.get("assignees", [])] if t.get("assignees") else ["Ninguém"],
                "Categorias": self._get_custom_field(t, "Categoria"),
                "Classificação": self._get_custom_field(t, "Classificação"),
                "SLA": self._get_custom_field(t, "⏲️ SLA"),
            })
        return dados_tratados

# Teste de uso
if __name__ == "__main__":

    token = "x"

    list_id = "x"

    task_fetcher = ClickUpTaskFetcher(token, list_id)
    tasks = task_fetcher.fetch_tasks()

    for task in tasks:
        print(task)
        print()

import requests

class ClickUpTaskUpdater:
    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }

    def update_task(self, task_id, name=None, description=None, priority=None, tags=None):
        url = f'https://api.clickup.com/api/v2/task/{task_id}'
        
        payload = {}
        if name:
            payload['name'] = name
        if description:
            payload['description'] = description
        if priority:
            payload['priority'] = priority
        if tags:
            payload['tags'] = tags


        response = requests.put(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            print("Tarefa atualizada com sucesso!")
            return response.json()
        else:
            print(f"Erro ao atualizar a tarefa: {response.status_code}")
            print(response.text)
            return None

if __name__ == "__main__":
    task_updater = ClickUpTaskUpdater("x")

    task_id = "x"
    result = task_updater.update_task(
        task_id=task_id,
        name="Teste esta atualizado",
        description="Teste foi atualizado",
        priority=1,
        tags=["Atualizado", "Monitoramento"]
    )
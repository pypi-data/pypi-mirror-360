import requests 
import re

# Função utilitária para limpar nomes de campos/opções
def limpar_nome(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    texto = re.sub(r'[^\w\s]', '', texto)  # Remove emojis e caracteres especiais
    return texto.strip().lower()


class ClickUpTaskCreator:
    def __init__(self, api_token, list_id):
        self.api_token = api_token
        self.list_id = list_id
        self.base_url = f'https://api.clickup.com/api/v2/list/{self.list_id}/task'
        self.headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }


    def create_task(self, name, description, priority=3, tags=None, custom_fields=None):
        payload = {
            "name": name,
            "description": description, 
            "priority": priority,
            "tags": tags,
            "custom_fields": custom_fields
        }

        response = requests.post(self.base_url, headers=self.headers, json=payload)

        if response.status_code in [200, 201]:
            print("Tarefa criada com sucesso!")
            return response.json()
        else:
            print("Erro ao criar a tarefa:", response.status_code)
            print(response.text)
            return None


    def get_custom_field_option_id(self, campo_nome, opcao_nome):
        url = f"https://api.clickup.com/api/v2/list/{self.list_id}/field"
        response = requests.get(url, headers=self.headers)
        data = response.json()

        campos = data.get("fields", [])

        for campo in campos:
            if limpar_nome(campo["name"]) == limpar_nome(campo_nome):
                if campo["type"] == "drop_down":
                    for opcao in campo["type_config"]["options"]:
                        if limpar_nome(opcao["name"]) == limpar_nome(opcao_nome):
                            return campo["id"], opcao["id"]
        print(f"Campo ou opção não encontrada: {campo_nome} -> {opcao_nome}")
        return None, None   


    def montar_campos_customizados(self, alerta):
        campos = []

        # Adiciona campo de categoria
        if alerta.get("categoria"):
            campo_id, valor_id = self.get_custom_field_option_id("categoria", alerta["categoria"])
            if campo_id and valor_id:
                campos.append({"id": campo_id, "value": valor_id})

        # Adiciona campo de classificação
        if alerta.get("classificação"):
            campo_id, valor_id = self.get_custom_field_option_id("classificação", alerta["classificação"])
            if campo_id and valor_id:
                campos.append({"id": campo_id, "value": valor_id})

        # Adiciona campo de SLA
        if alerta.get("sla"):
            campo_id, valor_id = self.get_custom_field_option_id("sla", alerta["sla"])
            if campo_id and valor_id:
                campos.append({"id": campo_id, "value": valor_id})

        return campos

# Executa somente quando rodar diretamente
if __name__ == "__main__":

    alerta = {
        "empresa": "x",
        "nomeDoAlerta": "SegundoTeste via api",
        "descricaoDoAlerta": "Isso é um teste que cria os campos personalizados via api",
        "prioridade": 3,
        "categoria": "hdi",                # Informação do campo tem que ser exatamente igual ao nome do campo no ClickUp
        "classificação": "solicitação",    # Informação do campo tem que ser exatamente igual ao nome do campo no ClickUp
        "sla": "p0"                        # Informação do campo tem que ser exatamente igual ao nome do campo no ClickUp
    }

    list_id = "x"

    criaAlertaClickUp = ClickUpTaskCreator(api_token="x", list_id=list_id)

    try:
        campos_customizados = criaAlertaClickUp.montar_campos_customizados(alerta)
        print("Campos customizados:", campos_customizados)
    except Exception as e:
        print(f"Erro ao tentar criar a tarefa, verifique se os campos estão corretos: {e}")
        exit()

    # Se for preciso execulte um teste antes de criar a tarefa
    teste = criaAlertaClickUp.get_custom_field_option_id("classificação", alerta["classificação"])
    print(teste)

    # Descomente para criar a tarefa
    criaAlertaClickUp.create_task(
        name=alerta["nomeDoAlerta"],
        description=alerta["descricaoDoAlerta"],
        priority=alerta["prioridade"],
        tags=["Monitoramento", "Sistema"],
        custom_fields=campos_customizados
    )

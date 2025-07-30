# 🚀 ClickUp Task Automation

Automação para criação e atualização de tarefas no ClickUp via API, com suporte a múltiplas empresas e campos personalizados.

---

## 📚 Sobre o Projeto

Este projeto automatiza a criação, filtro e atualização de tarefas no ClickUp a partir de alertas gerados por outros sistemas, preenchendo campos customizados conforme a empresa de destino. Ideal para times que precisam centralizar e agilizar o fluxo de trabalho entre diferentes plataformas.

---


## 🗂️ Estrutura do Projeto

```
onedev-common-clickup/
├── criaAlerta.py              # Função principal de criação de tarefas
├── filtroAlertas.py           # Funções para filtrar/processar alertas
├── updateTasks.py             # Atualização de tarefas existentes
```

---

## ⚙️ Configuração

1. **Clone o repositório:**
   ```bash
   pip install onedevcommonclickup
   ```

2. **Crie o arquivo `.env` com as variáveis necessárias:**
   ```
   API_TOKEN=seu_token_clickup
   LIST_ID=lista_id
   LIST_ID=lista_id
   LIST_ID=lista_id
   ```

3. **Instale as dependências (se houver):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o script desejado:**
   ```bash
   python criaAlerta.py
   ```

---

## 📝 Observações

- O arquivo `.env` **NÃO** deve ser versionado.
- Adapte os scripts conforme a necessidade de cada empresa.
- Consulte os arquivos de cada subpasta para lógicas específicas.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

## 📄 Licença

Este projeto está sob a licença MIT.

---
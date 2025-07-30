import os
import copy
import functools
from databricks.sdk import WorkspaceClient
import proxai.types as types
import proxai.connectors.providers.databricks_mock as databricks_mock
import proxai.connectors.model_connector as model_connector


class DatabricksConnector(model_connector.ProviderModelConnector):
  def get_provider_name(self):
    return 'databricks'

  def init_model(self):
    w = WorkspaceClient()
    return w.serving_endpoints.get_open_ai_client()

  def init_mock_model(self):
    return databricks_mock.DatabricksMock()

  def generate_text_proc(self, query_record: types.QueryRecord) -> str:
    # Note: Databricks tries to use same parameters with OpenAI.
    # Some parameters seems not working as expected for some models. For
    # example, the system instruction doesn't have any effect on the completion
    # for databricks-dbrx-instruct. But the stop parameter works as expected for
    # this model. However, system instruction works for
    # databricks-llama-2-70b-chat.
    query_messages = []
    if query_record.system != None:
      query_messages.append({'role': 'system', 'content': query_record.system})
    if query_record.prompt != None:
      query_messages.append({'role': 'user', 'content': query_record.prompt})
    if query_record.messages != None:
      query_messages.extend(query_record.messages)
    provider_model = query_record.provider_model

    create = functools.partial(
        self.api.chat.completions.create,
        model=provider_model.provider_model_identifier,
        messages=query_messages)
    if query_record.max_tokens != None:
      create = functools.partial(create, max_tokens=query_record.max_tokens)
    if query_record.temperature != None:
      create = functools.partial(create, temperature=query_record.temperature)
    if query_record.stop != None:
      create = functools.partial(create, stop=query_record.stop)

    completion = create()
    return completion.choices[0].message.content

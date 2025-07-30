import copy
import functools
from openai import OpenAI
import proxai.types as types
import proxai.connectors.providers.openai_mock as openai_mock
import proxai.connectors.model_connector as model_connector


class OpenAIConnector(model_connector.ProviderModelConnector):
  def get_provider_name(self):
    return 'openai'

  def init_model(self):
    return OpenAI()

  def init_mock_model(self):
    return openai_mock.OpenAIMock()

  def generate_text_proc(self, query_record: types.QueryRecord) -> str:
    # Note: OpenAI uses 'system', 'user', and 'assistant' as roles.
    query_messages = []
    if query_record.system is not None:
      query_messages.append({'role': 'system', 'content': query_record.system})
    if query_record.prompt is not None:
      query_messages.append({'role': 'user', 'content': query_record.prompt})
    if query_record.messages is not None:
      query_messages.extend(query_record.messages)
    provider_model = query_record.provider_model

    create = functools.partial(
        self.api.chat.completions.create,
        model=provider_model.provider_model_identifier,
        messages=query_messages)
    if query_record.max_tokens is not None:
      create = functools.partial(
          create, max_completion_tokens=query_record.max_tokens)
    if query_record.temperature is not None:
      create = functools.partial(create, temperature=query_record.temperature)
    if query_record.stop is not None:
      create = functools.partial(create, stop=query_record.stop)

    completion = create()
    return completion.choices[0].message.content

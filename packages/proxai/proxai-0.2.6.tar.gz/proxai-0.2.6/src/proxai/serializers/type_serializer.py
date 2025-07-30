import datetime
import json
from typing import Any, Dict
import proxai.types as types
import proxai.stat_types as stat_types
import proxai.connectors.model_configs as model_configs


def encode_provider_model_type(
    provider_model_type: types.ProviderModelType) -> Dict[str, Any]:
  record = {}
  record['provider'] = provider_model_type.provider
  record['model'] = provider_model_type.model
  record['provider_model_identifier'] = (
      provider_model_type.provider_model_identifier)
  return record


def decode_provider_model_type(
    record: Dict[str, Any]) -> types.ProviderModelType:
  if 'provider' not in record:
    raise ValueError(f'Provider not found in record: {record=}')
  if 'model' not in record:
    raise ValueError(f'Model not found in record: {record=}')
  if 'provider_model_identifier' not in record:
    raise ValueError(
        f'Provider model identifier not found in record: {record=}')
  provider_model = model_configs.ALL_MODELS[record['provider']][record['model']]
  if provider_model.provider_model_identifier != record[
      'provider_model_identifier']:
    raise ValueError(
        'Provider model identifier mismatch: '
        f'{record["provider_model_identifier"]} != '
        f'{provider_model.provider_model_identifier}'
        '\nThis can happen if the model config has changed in recent versions.')
  return provider_model


def encode_query_record(
    query_record: types.QueryRecord) -> Dict[str, Any]:
  record = {}
  if query_record.call_type != None:
    record['call_type'] = query_record.call_type.value
  if query_record.provider_model != None:
    record['provider_model'] = encode_provider_model_type(
        query_record.provider_model)
  if query_record.prompt != None:
    record['prompt'] = query_record.prompt
  if query_record.system != None:
    record['system'] = query_record.system
  if query_record.messages != None:
    record['messages'] = query_record.messages
  if query_record.max_tokens != None:
    record['max_tokens'] = str(query_record.max_tokens)
  if query_record.temperature != None:
    record['temperature'] = str(query_record.temperature)
  if query_record.stop != None:
    record['stop'] = query_record.stop
  if query_record.hash_value != None:
    record['hash_value'] = query_record.hash_value
  if query_record.token_count != None:
    record['token_count'] = str(query_record.token_count)
  return record


def decode_query_record(
    record: Dict[str, Any]) -> types.QueryRecord:
  query_record = types.QueryRecord()
  if 'call_type' in record:
    query_record.call_type = types.CallType(record['call_type'])
  if 'provider_model' in record:
    query_record.provider_model = decode_provider_model_type(
        record['provider_model'])
  query_record.prompt = record.get('prompt', None)
  query_record.system = record.get('system', None)
  query_record.messages = record.get('messages', None)
  if 'max_tokens' in record:
    query_record.max_tokens = int(record['max_tokens'])
  if 'temperature' in record:
    query_record.temperature = float(record['temperature'])
  query_record.stop = record.get('stop', None)
  query_record.hash_value = record.get('hash_value', None)
  if 'token_count' in record:
    query_record.token_count = int(record['token_count'])
  return query_record


def encode_query_response_record(
    query_response_record: types.QueryResponseRecord
) -> Dict[str, Any]:
  record = {}
  if query_response_record.response != None:
    record['response'] = query_response_record.response
  if query_response_record.error != None:
    record['error'] = query_response_record.error
  if query_response_record.start_utc_date != None:
    record['start_utc_date'] = query_response_record.start_utc_date.isoformat()
  if query_response_record.end_utc_date != None:
    record['end_utc_date'] = query_response_record.end_utc_date.isoformat()
  if query_response_record.local_time_offset_minute != None:
    record['local_time_offset_minute'] = (
        query_response_record.local_time_offset_minute)
  if query_response_record.response_time != None:
    record['response_time'] = (
        query_response_record.response_time.total_seconds())
  if query_response_record.estimated_cost != None:
    record['estimated_cost'] = query_response_record.estimated_cost
  if query_response_record.token_count != None:
    record['token_count'] = str(query_response_record.token_count)
  return record


def decode_query_response_record(
    record: Dict[str, Any]) -> types.QueryResponseRecord:
  query_response_record = types.QueryResponseRecord()
  query_response_record.response = record.get('response', None)
  query_response_record.error = record.get('error', None)
  if 'start_utc_date' in record:
    query_response_record.start_utc_date = datetime.datetime.fromisoformat(
        record['start_utc_date'])
  if 'end_utc_date' in record:
    query_response_record.end_utc_date = datetime.datetime.fromisoformat(
        record['end_utc_date'])
  if 'local_time_offset_minute' in record:
    query_response_record.local_time_offset_minute = (
        record['local_time_offset_minute'])
  if 'response_time' in record:
    query_response_record.response_time = datetime.timedelta(
        seconds=record['response_time'])
  if 'estimated_cost' in record:
    query_response_record.estimated_cost = record['estimated_cost']
  if 'token_count' in record:
    query_response_record.token_count = int(record['token_count'])
  return query_response_record


def encode_cache_record(
    cache_record: types.CacheRecord) -> Dict[str, Any]:
  record = {}
  if cache_record.query_record != None:
    record['query_record'] = encode_query_record(
        cache_record.query_record)
  if cache_record.query_responses != None:
    record['query_responses'] = []
    for query_response_record in cache_record.query_responses:
      record['query_responses'].append(
          encode_query_response_record(query_response_record))
  if cache_record.shard_id != None:
    try:
      record['shard_id'] = int(cache_record.shard_id)
    except ValueError:
      record['shard_id'] = cache_record.shard_id
  if cache_record.last_access_time != None:
    record['last_access_time'] = cache_record.last_access_time.isoformat()
  if cache_record.call_count != None:
    record['call_count'] = cache_record.call_count
  return record


def decode_cache_record(
    record: Dict[str, Any]) -> types.CacheRecord:
  cache_record = types.CacheRecord()
  if 'query_record' in record:
    cache_record.query_record = decode_query_record(
        record['query_record'])
  if 'query_responses' in record:
    cache_record.query_responses = []
    for query_response_record in record['query_responses']:
      cache_record.query_responses.append(
          decode_query_response_record(query_response_record))
  if 'shard_id' in record:
    try:
      cache_record.shard_id = int(record['shard_id'])
    except ValueError:
      cache_record.shard_id = record['shard_id']
  if 'last_access_time' in record:
    cache_record.last_access_time = datetime.datetime.fromisoformat(
        record['last_access_time'])
  if 'call_count' in record:
    cache_record.call_count = int(record['call_count'])
  return cache_record


def encode_light_cache_record(
    light_cache_record: types.LightCacheRecord) -> Dict[str, Any]:
  record = {}
  if light_cache_record.query_record_hash != None:
    record['query_record_hash'] = light_cache_record.query_record_hash
  if light_cache_record.query_response_count != None:
    record['query_response_count'] = light_cache_record.query_response_count
  if light_cache_record.shard_id != None:
    try:
      record['shard_id'] = int(light_cache_record.shard_id)
    except ValueError:
      record['shard_id'] = light_cache_record.shard_id
  if light_cache_record.last_access_time != None:
    record['last_access_time'] = (
        light_cache_record.last_access_time.isoformat())
  if light_cache_record.call_count != None:
    record['call_count'] = light_cache_record.call_count
  return record


def decode_light_cache_record(
    record: Dict[str, Any]) -> types.LightCacheRecord:
  light_cache_record = types.LightCacheRecord()
  light_cache_record.query_record_hash = record.get('query_record_hash', None)
  if 'query_response_count' in record:
    light_cache_record.query_response_count = int(
        record['query_response_count'])
  if 'shard_id' in record:
    try:
      light_cache_record.shard_id = int(record['shard_id'])
    except ValueError:
      light_cache_record.shard_id = record['shard_id']
  if 'last_access_time' in record:
    light_cache_record.last_access_time = datetime.datetime.fromisoformat(
        record['last_access_time'])
  if 'call_count' in record:
    light_cache_record.call_count = int(record['call_count'])
  return light_cache_record


def encode_logging_record(
    logging_record: types.LoggingRecord) -> Dict[str, Any]:
  record = {}
  if logging_record.query_record != None:
    record['query_record'] = encode_query_record(
        logging_record.query_record)
  if logging_record.response_record != None:
    record['response_record'] = encode_query_response_record(
        logging_record.response_record)
  if logging_record.response_source != None:
    record['response_source'] = logging_record.response_source.value
  if logging_record.look_fail_reason != None:
    record['look_fail_reason'] = logging_record.look_fail_reason.value
  return record


def decode_logging_record(
    record: Dict[str, Any]) -> types.LoggingRecord:
  logging_record = types.LoggingRecord()
  if 'query_record' in record:
    logging_record.query_record = decode_query_record(
        record['query_record'])
  if 'response_record' in record:
    logging_record.response_record = decode_query_response_record(
        record['response_record'])
  if 'response_source' in record:
    logging_record.response_source = (
        types.ResponseSource(record['response_source']))
  if 'look_fail_reason' in record:
    logging_record.look_fail_reason = (
        types.CacheLookFailReason(record['look_fail_reason']))
  return logging_record


def encode_model_status(
    model_status: types.ModelStatus) -> Dict[str, Any]:
  record = {}
  if model_status.unprocessed_models != None:
    record['unprocessed_models'] = []
    for provider_model in model_status.unprocessed_models:
      record['unprocessed_models'].append(
          encode_provider_model_type(provider_model))
  if model_status.working_models != None:
    record['working_models'] = []
    for provider_model in model_status.working_models:
      record['working_models'].append(
          encode_provider_model_type(provider_model))
  if model_status.failed_models != None:
    record['failed_models'] = []
    for provider_model in model_status.failed_models:
      record['failed_models'].append(encode_provider_model_type(provider_model))
  if model_status.filtered_models != None:
    record['filtered_models'] = []
    for provider_model in model_status.filtered_models:
      record['filtered_models'].append(
          encode_provider_model_type(provider_model))
  if model_status.provider_queries != None:
    record['provider_queries'] = {}
    for provider_model, provider_query in model_status.provider_queries.items():
      provider_model = json.dumps(encode_provider_model_type(provider_model))
      record['provider_queries'][provider_model] = (
          encode_logging_record(provider_query))
  return record


def decode_model_status(
    record: Dict[str, Any]) -> types.ModelStatus:
  model_status = types.ModelStatus()
  if 'unprocessed_models' in record:
    for provider_model_record in record['unprocessed_models']:
      model_status.unprocessed_models.add(
          decode_provider_model_type(provider_model_record))
  if 'working_models' in record:
    for provider_model_record in record['working_models']:
      model_status.working_models.add(
          decode_provider_model_type(provider_model_record))
  if 'failed_models' in record:
    for provider_model_record in record['failed_models']:
      model_status.failed_models.add(
          decode_provider_model_type(provider_model_record))
  if 'filtered_models' in record:
    for provider_model_record in record['filtered_models']:
      model_status.filtered_models.add(
          decode_provider_model_type(provider_model_record))
  if 'provider_queries' in record:
    for provider_model, provider_query_record in record[
        'provider_queries'].items():
      provider_model = json.loads(provider_model)
      provider_model = decode_provider_model_type(provider_model)
      model_status.provider_queries[provider_model] = (
          decode_logging_record(provider_query_record))
  return model_status


def encode_logging_options(
    logging_options: types.LoggingOptions) -> Dict[str, Any]:
  record = {}
  if logging_options.logging_path != None:
    record['logging_path'] = logging_options.logging_path
  if logging_options.stdout != None:
    record['stdout'] = logging_options.stdout
  if logging_options.hide_sensitive_content != None:
    record['hide_sensitive_content'] = logging_options.hide_sensitive_content
  return record


def encode_cache_options(
    cache_options: types.CacheOptions) -> Dict[str, Any]:
  record = {}
  if cache_options.cache_path != None:
    record['cache_path'] = cache_options.cache_path
  if cache_options.unique_response_limit != None:
    record['unique_response_limit'] = cache_options.unique_response_limit
  if cache_options.retry_if_error_cached != None:
    record['retry_if_error_cached'] = cache_options.retry_if_error_cached
  if cache_options.clear_query_cache_on_connect != None:
    record['clear_query_cache_on_connect'] = (
        cache_options.clear_query_cache_on_connect)
  if cache_options.clear_model_cache_on_connect != None:
    record['clear_model_cache_on_connect'] = (
        cache_options.clear_model_cache_on_connect)
  return record


def encode_proxdash_options(
    proxdash_options: types.ProxDashOptions) -> Dict[str, Any]:
  record = {}
  if proxdash_options.stdout != None:
    record['stdout'] = proxdash_options.stdout
  if proxdash_options.hide_sensitive_content != None:
    record['hide_sensitive_content'] = proxdash_options.hide_sensitive_content
  if proxdash_options.disable_proxdash != None:
    record['disable_proxdash'] = proxdash_options.disable_proxdash
  return record


def encode_run_options(
    run_options: types.RunOptions) -> Dict[str, Any]:
  record = {}
  if run_options.run_type != None:
    record['run_type'] = run_options.run_type.value
  if run_options.hidden_run_key != None:
    record['hidden_run_key'] = run_options.hidden_run_key
  if run_options.experiment_path != None:
    record['experiment_path'] = run_options.experiment_path
  if run_options.root_logging_path != None:
    record['root_logging_path'] = run_options.root_logging_path
  if run_options.default_model_cache_path != None:
    record['default_model_cache_path'] = run_options.default_model_cache_path
  if run_options.logging_options != None:
    record['logging_options'] = encode_logging_options(
        run_options.logging_options)
  if run_options.cache_options != None:
    record['cache_options'] = encode_cache_options(
        run_options.cache_options)
  if run_options.proxdash_options != None:
    record['proxdash_options'] = encode_proxdash_options(
        run_options.proxdash_options)
  if run_options.allow_multiprocessing != None:
    record['allow_multiprocessing'] = run_options.allow_multiprocessing
  if run_options.model_test_timeout != None:
    record['model_test_timeout'] = run_options.model_test_timeout
  if run_options.strict_feature_test != None:
    record['strict_feature_test'] = run_options.strict_feature_test
  if run_options.suppress_provider_errors != None:
    record['suppress_provider_errors'] = run_options.suppress_provider_errors
  return record


def decode_logging_options(
    record: Dict[str, Any]) -> types.LoggingOptions:
  logging_options = types.LoggingOptions()
  if 'logging_path' in record:
    logging_options.logging_path = record['logging_path']
  if 'stdout' in record:
    logging_options.stdout = record['stdout']
  if 'hide_sensitive_content' in record:
    logging_options.hide_sensitive_content = record['hide_sensitive_content']
  return logging_options


def decode_cache_options(
    record: Dict[str, Any]) -> types.CacheOptions:
  cache_options = types.CacheOptions()
  if 'cache_path' in record:
    cache_options.cache_path = record['cache_path']
  if 'unique_response_limit' in record:
    cache_options.unique_response_limit = record['unique_response_limit']
  if 'retry_if_error_cached' in record:
    cache_options.retry_if_error_cached = record['retry_if_error_cached']
  if 'clear_query_cache_on_connect' in record:
    cache_options.clear_query_cache_on_connect = (
        record['clear_query_cache_on_connect'])
  if 'clear_model_cache_on_connect' in record:
    cache_options.clear_model_cache_on_connect = (
        record['clear_model_cache_on_connect'])
  return cache_options


def decode_proxdash_options(
    record: Dict[str, Any]) -> types.ProxDashOptions:
  proxdash_options = types.ProxDashOptions()
  if 'stdout' in record:
    proxdash_options.stdout = record['stdout']
  if 'hide_sensitive_content' in record:
    proxdash_options.hide_sensitive_content = record['hide_sensitive_content']
  if 'disable_proxdash' in record:
    proxdash_options.disable_proxdash = record['disable_proxdash']
  return proxdash_options


def decode_run_options(
    record: Dict[str, Any]) -> types.RunOptions:
  run_options = types.RunOptions()
  if 'run_type' in record:
    run_options.run_type = types.RunType(record['run_type'])
  if 'hidden_run_key' in record:
    run_options.hidden_run_key = record['hidden_run_key']
  if 'experiment_path' in record:
    run_options.experiment_path = record['experiment_path']
  if 'root_logging_path' in record:
    run_options.root_logging_path = record['root_logging_path']
  if 'default_model_cache_path' in record:
    run_options.default_model_cache_path = record['default_model_cache_path']
  if 'logging_options' in record:
    run_options.logging_options = decode_logging_options(
        record['logging_options'])
  if 'cache_options' in record:
    run_options.cache_options = decode_cache_options(
        record['cache_options'])
  if 'proxdash_options' in record:
    run_options.proxdash_options = decode_proxdash_options(
        record['proxdash_options'])
  if 'allow_multiprocessing' in record:
    run_options.allow_multiprocessing = record['allow_multiprocessing']
  if 'model_test_timeout' in record:
    run_options.model_test_timeout = record['model_test_timeout']
  if 'strict_feature_test' in record:
    run_options.strict_feature_test = record['strict_feature_test']
  if 'suppress_provider_errors' in record:
    run_options.suppress_provider_errors = record['suppress_provider_errors']
  return run_options


def encode_base_provider_stats(
    base_provider_stats: stat_types.BaseProviderStats) -> Dict[str, Any]:
  record = {}
  if base_provider_stats.total_queries:
    record['total_queries'] = base_provider_stats.total_queries
  if base_provider_stats.total_successes:
    record['total_successes'] = base_provider_stats.total_successes
  if base_provider_stats.total_fails:
    record['total_fails'] = base_provider_stats.total_fails
  if base_provider_stats.total_token_count:
    record['total_token_count'] = base_provider_stats.total_token_count
  if base_provider_stats.total_query_token_count:
    record['total_query_token_count'] = (
        base_provider_stats.total_query_token_count)
  if base_provider_stats.total_response_token_count:
    record['total_response_token_count'] = (
        base_provider_stats.total_response_token_count)
  if base_provider_stats.total_response_time:
    record['total_response_time'] = base_provider_stats.total_response_time
  if base_provider_stats.avr_response_time:
    record['avr_response_time'] = base_provider_stats.avr_response_time
  if base_provider_stats.estimated_cost:
    record['estimated_cost'] = base_provider_stats.estimated_cost
  if base_provider_stats.total_cache_look_fail_reasons:
    record['total_cache_look_fail_reasons'] = {}
    for k, v in base_provider_stats.total_cache_look_fail_reasons.items():
      record['total_cache_look_fail_reasons'][k.value] = v
  return record


def decode_base_provider_stats(
    record: Dict[str, Any]) -> stat_types.BaseProviderStats:
  base_provider_stats = stat_types.BaseProviderStats()
  if 'total_queries' in record:
    base_provider_stats.total_queries = record['total_queries']
  if 'total_successes' in record:
    base_provider_stats.total_successes = record['total_successes']
  if 'total_fails' in record:
    base_provider_stats.total_fails = record['total_fails']
  if 'total_token_count' in record:
    base_provider_stats.total_token_count = record['total_token_count']
  if 'total_query_token_count' in record:
    base_provider_stats.total_query_token_count = (
        record['total_query_token_count'])
  if 'total_response_token_count' in record:
    base_provider_stats.total_response_token_count = (
        record['total_response_token_count'])
  if 'total_response_time' in record:
    base_provider_stats.total_response_time = record['total_response_time']
  if 'estimated_cost' in record:
    base_provider_stats.estimated_cost = record['estimated_cost']
  if 'total_cache_look_fail_reasons' in record:
    base_provider_stats.total_cache_look_fail_reasons = {}
    for k, v in record['total_cache_look_fail_reasons'].items():
      base_provider_stats.total_cache_look_fail_reasons[
          types.CacheLookFailReason(k)] = v
  return base_provider_stats


def encode_base_cache_stats(
    base_cache_stats: stat_types.BaseCacheStats) -> Dict[str, Any]:
  record = {}
  if base_cache_stats.total_cache_hit:
    record['total_cache_hit'] = base_cache_stats.total_cache_hit
  if base_cache_stats.total_success_return:
    record['total_success_return'] = base_cache_stats.total_success_return
  if base_cache_stats.total_fail_return:
    record['total_fail_return'] = base_cache_stats.total_fail_return
  if base_cache_stats.saved_token_count:
    record['saved_token_count'] = base_cache_stats.saved_token_count
  if base_cache_stats.saved_query_token_count:
    record['saved_query_token_count'] = base_cache_stats.saved_query_token_count
  if base_cache_stats.saved_response_token_count:
    record['saved_response_token_count'] = (
        base_cache_stats.saved_response_token_count)
  if base_cache_stats.saved_total_response_time:
    record['saved_total_response_time'] = (
        base_cache_stats.saved_total_response_time)
  if base_cache_stats.saved_avr_response_time:
    record['saved_avr_response_time'] = base_cache_stats.saved_avr_response_time
  if base_cache_stats.saved_estimated_cost:
    record['saved_estimated_cost'] = base_cache_stats.saved_estimated_cost
  return record


def decode_base_cache_stats(record) -> stat_types.BaseCacheStats:
  base_cache_stats = stat_types.BaseCacheStats()
  if 'total_cache_hit' in record:
    base_cache_stats.total_cache_hit = record['total_cache_hit']
  if 'total_success_return' in record:
    base_cache_stats.total_success_return = record['total_success_return']
  if 'total_fail_return' in record:
    base_cache_stats.total_fail_return = record['total_fail_return']
  if 'saved_token_count' in record:
    base_cache_stats.saved_token_count = record['saved_token_count']
  if 'saved_query_token_count' in record:
    base_cache_stats.saved_query_token_count = record['saved_query_token_count']
  if 'saved_response_token_count' in record:
    base_cache_stats.saved_response_token_count = (
        record['saved_response_token_count'])
  if 'saved_total_response_time' in record:
    base_cache_stats.saved_total_response_time = (
        record['saved_total_response_time'])
  if 'saved_estimated_cost' in record:
    base_cache_stats.saved_estimated_cost = record['saved_estimated_cost']
  return base_cache_stats


def encode_provider_model_stats(
    provider_model_stats: stat_types.ProviderModelStats) -> Dict[str, Any]:
  record = {}
  if provider_model_stats.provider_model:
    record['provider_model'] = encode_provider_model_type(
        provider_model_stats.provider_model)
  if provider_model_stats.provider_stats:
    record['provider_stats'] = encode_base_provider_stats(
        provider_model_stats.provider_stats)
  if provider_model_stats.cache_stats:
    record['cache_stats'] = encode_base_cache_stats(
        provider_model_stats.cache_stats)
  return record


def decode_provider_model_stats(
    record: Dict[str, Any]) -> stat_types.ProviderModelStats:
  provider_model_stats = stat_types.ProviderModelStats()
  if 'provider_model' in record:
    provider_model_stats.provider_model = decode_provider_model_type(
        record['provider_model'])
  if 'provider_stats' in record:
    provider_model_stats.provider_stats = decode_base_provider_stats(
        record['provider_stats'])
  if 'cache_stats' in record:
    provider_model_stats.cache_stats = decode_base_cache_stats(
        record['cache_stats'])
  return provider_model_stats


def encode_provider_stats(
    provider_stats: stat_types.ProviderStats) -> Dict[str, Any]:
  record = {}
  if provider_stats.provider:
    record['provider'] = provider_stats.provider
  if provider_stats.provider_stats:
    record['provider_stats'] = encode_base_provider_stats(
        provider_stats.provider_stats)
  if provider_stats.cache_stats:
    record['cache_stats'] = encode_base_cache_stats(provider_stats.cache_stats)
  if provider_stats.provider_models:
    record['provider_models'] = []
    for k, v in provider_stats.provider_models.items():
      value = encode_provider_model_type(k)
      value['provider_model_stats'] = encode_provider_model_stats(v)
      record['provider_models'].append(value)
  return record


def decode_provider_stats(record: Dict[str, Any]) -> stat_types.ProviderStats:
  provider_stats = stat_types.ProviderStats()
  if 'provider' in record:
    provider_stats.provider = record['provider']
  if 'provider_stats' in record:
    provider_stats.provider_stats = decode_base_provider_stats(
        record['provider_stats'])
  if 'cache_stats' in record:
    provider_stats.cache_stats = decode_base_cache_stats(
        record['cache_stats'])
  if 'provider_models' in record:
    provider_stats.provider_models = {}
    for provider_model_record in record['provider_models']:
      provider_model_type = decode_provider_model_type({
          'provider': provider_model_record['provider'],
          'model': provider_model_record['model'],
          'provider_model_identifier': provider_model_record[
              'provider_model_identifier']
      })
      provider_stats.provider_models[provider_model_type] = (
          decode_provider_model_stats(
              provider_model_record['provider_model_stats']))
  return provider_stats


def encode_run_stats(
    run_stats: stat_types.RunStats) -> Dict[str, Any]:
  record = {}
  if run_stats.provider_stats:
    record['provider_stats'] = encode_base_provider_stats(
        run_stats.provider_stats)
  if run_stats.cache_stats:
    record['cache_stats'] = encode_base_cache_stats(run_stats.cache_stats)
  if run_stats.providers:
    record['providers'] = {}
    for k, v in run_stats.providers.items():
      record['providers'][k] = encode_provider_stats(v)
  return record


def decode_run_stats(
    record: Dict[str, Any]) -> stat_types.RunStats:
  run_stats = stat_types.RunStats()
  if 'provider_stats' in record:
    run_stats.provider_stats = decode_base_provider_stats(
        record['provider_stats'])
  if 'cache_stats' in record:
    run_stats.cache_stats = decode_base_cache_stats(record['cache_stats'])
  if 'providers' in record:
    run_stats.providers = {}
    for k, v in record['providers'].items():
      run_stats.providers[k] = decode_provider_stats(v)
  return run_stats

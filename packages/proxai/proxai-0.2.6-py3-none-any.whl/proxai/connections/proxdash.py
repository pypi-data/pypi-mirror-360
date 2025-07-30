import os
import copy
import json
import requests
from functools import wraps
import proxai.types as types
import proxai.experiment.experiment as experiment
import proxai.logging.utils as logging_utils
import proxai.state_controllers.state_controller as state_controller
from typing import Any, Callable, Dict, List, Optional, Union, Tuple

_PROXDASH_STATE_PROPERTY = '_proxdash_connection_state'
_NOT_SET_EXPERIMENT_PATH_VALUE = '(not set)'


class ProxDashConnection(state_controller.StateControlled):
  _status: Optional[types.ProxDashConnectionStatus]
  _hidden_run_key: Optional[str]
  _experiment_path: Optional[str]
  _get_experiment_path: Optional[Callable[[], str]]
  _logging_options: Optional[types.LoggingOptions]
  _get_logging_options: Optional[Callable[[], types.LoggingOptions]]
  _proxdash_options: Optional[types.ProxDashOptions]
  _get_proxdash_options: Optional[Callable[[], types.ProxDashOptions]]
  _key_info_from_proxdash: Optional[Dict]
  _connected_experiment_path: Optional[str]
  _proxdash_connection_state: Optional[types.ProxDashConnectionState]

  def __init__(
      self,
      hidden_run_key: Optional[str] = None,
      experiment_path: Optional[str] = None,
      get_experiment_path: Optional[Callable[[], str]] = None,
      logging_options: Optional[types.LoggingOptions] = None,
      get_logging_options: Optional[Callable[[], types.LoggingOptions]] = None,
      proxdash_options: Optional[types.ProxDashOptions] = None,
      get_proxdash_options: Optional[
          Callable[[], types.ProxDashOptions]] = None,
      init_state: Optional[types.ProxDashConnectionState] = None):
    if init_state and (
        hidden_run_key is not None or
        experiment_path is not None or get_experiment_path is not None or
        logging_options is not None or get_logging_options is not None or
        proxdash_options is not None or get_proxdash_options is not None):
      raise ValueError(
          'If init_state is provided, none of the other arguments should be '
          'provided.')

    super().__init__(
        hidden_run_key=hidden_run_key,
        experiment_path=experiment_path,
        get_experiment_path=get_experiment_path,
        logging_options=logging_options,
        get_logging_options=get_logging_options,
        proxdash_options=proxdash_options,
        get_proxdash_options=get_proxdash_options)

    self.init_state()
    self.set_property_value(
        'status', types.ProxDashConnectionStatus.INITIALIZING)

    if init_state:
      self.load_state(init_state)
    else:
      initial_state = self.get_state()
      self._get_experiment_path = get_experiment_path
      self._get_logging_options = get_logging_options
      self._get_proxdash_options = get_proxdash_options

      self.hidden_run_key = hidden_run_key
      self.logging_options = logging_options
      self.proxdash_options = proxdash_options
      self.experiment_path = experiment_path
      self.handle_changes(initial_state, self.get_state())

  def get_internal_state_property_name(self):
    return _PROXDASH_STATE_PROPERTY

  def get_internal_state_type(cls):
    return types.ProxDashConnectionState

  def handle_changes(
      self,
      old_state: types.ProxDashConnectionState,
      current_state: types.ProxDashConnectionState):
    result_state = copy.deepcopy(old_state)
    if current_state.logging_options is not None:
      result_state.logging_options = current_state.logging_options
    if current_state.proxdash_options is not None:
      result_state.proxdash_options = current_state.proxdash_options
    if current_state.key_info_from_proxdash is not None:
      result_state.key_info_from_proxdash = current_state.key_info_from_proxdash
    if current_state.experiment_path is not None:
      result_state.experiment_path = current_state.experiment_path
    if current_state.connected_experiment_path is not None:
      result_state.connected_experiment_path = (
          current_state.connected_experiment_path)
    if current_state.status is not None:
      result_state.status = current_state.status

    if result_state.proxdash_options is None:
      raise ValueError(
          'ProxDash options are not set for both old and new states. '
          'This creates an invalid state change.')
    if result_state.logging_options is None:
      raise ValueError(
          'Logging options are not set for both old and new states. '
          'This creates an invalid state change.')

    proxdash_disabled = result_state.proxdash_options.disable_proxdash
    if proxdash_disabled:
      self.status = types.ProxDashConnectionStatus.DISABLED
      self.key_info_from_proxdash = None
      # Note: There is no longer any connection to ProxDash. This change
      # shouldn't be logged, so, self.connected_experiment_path setter should
      # not be used here.
      self.set_property_value_without_triggering_getters(
          'connected_experiment_path', None)
      return

    if result_state.proxdash_options.api_key is None:
      if 'PROXDASH_API_KEY' not in os.environ:
        self.status = types.ProxDashConnectionStatus.API_KEY_NOT_FOUND
        self.key_info_from_proxdash = None
        # Note: There is no longer any connection to ProxDash. This change
        # shouldn't be logged, so, self.connected_experiment_path setter should
        # not be used here.
        self.set_property_value_without_triggering_getters(
            'connected_experiment_path', None)
        return
      else:
        # Note: Setting api_key from environment variable.
        self.proxdash_options.api_key = os.environ['PROXDASH_API_KEY']
        current_state.proxdash_options.api_key = os.environ['PROXDASH_API_KEY']
        result_state.proxdash_options.api_key = os.environ['PROXDASH_API_KEY']

    api_key_query_required = False

    old_api_key = None
    if old_state.proxdash_options:
      old_api_key = old_state.proxdash_options.api_key
    if old_api_key != result_state.proxdash_options.api_key:
      api_key_query_required = True
    if old_api_key == result_state.proxdash_options.api_key and (
        result_state.status == types.ProxDashConnectionStatus.INITIALIZING or
        result_state.status == types.ProxDashConnectionStatus.DISABLED or
        result_state.status == types.ProxDashConnectionStatus.API_KEY_NOT_FOUND
    ):
      api_key_query_required = True

    old_base_url = types.ProxDashOptions.base_url
    if old_state.proxdash_options:
      old_base_url = old_state.proxdash_options.base_url
    if old_base_url != result_state.proxdash_options.base_url:
      api_key_query_required = True

    if api_key_query_required:
      validation_status, key_info_from_proxdash = self._check_api_key_validity(
          base_url=result_state.proxdash_options.base_url,
          api_key=result_state.proxdash_options.api_key)
      result_state.status = validation_status
      result_state.key_info_from_proxdash = key_info_from_proxdash

    if result_state.status == types.ProxDashConnectionStatus.API_KEY_NOT_VALID:
      self.status = types.ProxDashConnectionStatus.API_KEY_NOT_VALID
      self.key_info_from_proxdash = None
      raise ValueError(
          'ProxDash API key not valid. Please provide a valid API key.\n'
          f'base_url: {result_state.proxdash_options.base_url}\n'
          f'api_key: {result_state.proxdash_options.api_key[:3]}...\n\n'
          'To fix this issue:\n'
          '1. Check that your PROXDASH_API_KEY in your .bashrc or .zshrc file '
          'is correct if it exists\n'
          '2. Check that px.ProxDashOptions(api_key="your_api_key") is correct '
          'if you set it directly\n'
          '3. Verify that your key matches what appears on '
          'https://proxai.co/dashboard/api-keys\n'
          '4. If you don\'t want to use ProxDash, make sure PROXDASH_API_KEY '
          'is not set in your environment variables\n'
          'For more information, see: '
          'https://www.proxai.co/proxai-docs/advanced/proxdash-connection')

    if result_state.status == types.ProxDashConnectionStatus.PROXDASH_INVALID_RETURN:
      self.status = types.ProxDashConnectionStatus.PROXDASH_INVALID_RETURN
      self.key_info_from_proxdash = None
      raise ValueError(
          'ProxDash returned an invalid response.\nPlease report this '
          'issue to the https://github.com/proxai/proxai.\n'
          'Also, please check latest stable version of ProxAI.')

    if result_state.status != types.ProxDashConnectionStatus.CONNECTED:
      raise ValueError(
          'Unknown ProxDash connection status.\n'
          f'result_state.status: {result_state.status}\n'
          'result_state.key_info_from_proxdash: '
          f'{result_state.key_info_from_proxdash}')

    if (self.status != result_state.status or
        old_base_url != result_state.proxdash_options.base_url or
        old_api_key != result_state.proxdash_options.api_key):
      # Note: This is good for logging purposes.
      self.status = result_state.status
    if self.key_info_from_proxdash != result_state.key_info_from_proxdash:
      self.key_info_from_proxdash = result_state.key_info_from_proxdash
    if self.connected_experiment_path != self.experiment_path:
      self.connected_experiment_path = self.experiment_path

  @property
  def hidden_run_key(self) -> Optional[str]:
    return self.get_property_value('hidden_run_key')

  @hidden_run_key.setter
  def hidden_run_key(self, hidden_run_key: Optional[str]):
    self.set_property_value('hidden_run_key', hidden_run_key)

  @property
  def logging_options(self) -> types.LoggingOptions:
    return self.get_property_value('logging_options')

  @logging_options.setter
  def logging_options(self, logging_options: types.LoggingOptions):
    self.set_property_value('logging_options', logging_options)

  @property
  def proxdash_options(self) -> types.ProxDashOptions:
    return self.get_property_value('proxdash_options')

  @proxdash_options.setter
  def proxdash_options(self, proxdash_options: types.ProxDashOptions):
    self.set_property_value('proxdash_options', proxdash_options)

  @property
  def key_info_from_proxdash(self) -> Optional[Dict]:
    return self.get_property_value('key_info_from_proxdash')

  @key_info_from_proxdash.setter
  def key_info_from_proxdash(self, key_info_from_proxdash: Optional[Dict]):
    self.set_property_value('key_info_from_proxdash', key_info_from_proxdash)

  @property
  def experiment_path(self) -> str:
    internal_experiment_path = self.get_property_internal_value(
        'experiment_path')
    internal_get_experiment_path = self.get_property_func_getter(
        'experiment_path')

    experiment_path = None
    if (internal_experiment_path is not None and
        internal_experiment_path != _NOT_SET_EXPERIMENT_PATH_VALUE):
      experiment_path = internal_experiment_path
    elif internal_get_experiment_path is not None:
      experiment_path = internal_get_experiment_path()

    if experiment_path is None:
      experiment_path = _NOT_SET_EXPERIMENT_PATH_VALUE

    self.set_property_internal_state_value(
        'experiment_path', experiment_path)
    return experiment_path

  @experiment_path.setter
  def experiment_path(self, experiment_path: Optional[str]):
    if experiment_path is not None:
      experiment.validate_experiment_path(experiment_path)
    else:
      experiment_path = _NOT_SET_EXPERIMENT_PATH_VALUE

    self.set_property_value('experiment_path', experiment_path)

  @property
  def connected_experiment_path(self) -> str:
    return self.get_property_value('connected_experiment_path')

  @connected_experiment_path.setter
  def connected_experiment_path(self, connected_experiment_path: Optional[str]):
    if self.status != types.ProxDashConnectionStatus.CONNECTED:
      if connected_experiment_path is not None:
        raise ValueError(
            'Connected experiment path can only be set if the ProxDash '
            'connection is connected.')
      self.set_property_value_without_triggering_getters(
          'connected_experiment_path', None)
      return

    previous_experiment_path = self.get_property_internal_value(
        'connected_experiment_path')
    if previous_experiment_path is None:
      previous_experiment_path = _NOT_SET_EXPERIMENT_PATH_VALUE

    new_experiment_path = connected_experiment_path
    if new_experiment_path is None:
      new_experiment_path = _NOT_SET_EXPERIMENT_PATH_VALUE

    if previous_experiment_path != new_experiment_path:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'Connected to ProxDash experiment: '
              f'{new_experiment_path}'),
          type=types.LoggingType.INFO)

    self.set_property_value(
        'connected_experiment_path', connected_experiment_path)

  @property
  def status(self) -> types.ProxDashConnectionStatus:
    return self.get_property_value('status')

  @status.setter
  def status(self, status: types.ProxDashConnectionStatus):
    self.set_property_value('status', status)
    if status == types.ProxDashConnectionStatus.INITIALIZING:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message='ProxDash connection initializing.',
          type=types.LoggingType.INFO)
    elif status == types.ProxDashConnectionStatus.DISABLED:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message='ProxDash connection disabled.',
          type=types.LoggingType.INFO)
    elif status == types.ProxDashConnectionStatus.API_KEY_NOT_FOUND:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'ProxDash connection disabled. Please provide a valid API key '
              'either as an argument or as an environment variable.'),
          type=types.LoggingType.ERROR)
    elif status == types.ProxDashConnectionStatus.API_KEY_NOT_VALID:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'ProxDash API key not valid. Please provide a valid API key.\n'
              'Check proxai.co/dashboard/api-keys page to get your API '
              'key.'),
          type=types.LoggingType.ERROR)
    elif status == types.ProxDashConnectionStatus.PROXDASH_INVALID_RETURN:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'ProxDash returned an invalid response.\nPlease report this '
              'issue to the https://github.com/proxai/proxai.\n'
              'Also, please check latest stable version of ProxAI.'),
          type=types.LoggingType.ERROR)
    elif status == types.ProxDashConnectionStatus.CONNECTED:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              f'Connected to ProxDash at {self.proxdash_options.base_url}'),
          type=types.LoggingType.INFO)

  def _check_api_key_validity(
      self,
      base_url: str,
      api_key: str) -> Tuple[
      Union[
          types.ProxDashConnectionStatus.API_KEY_NOT_VALID,
          types.ProxDashConnectionStatus.PROXDASH_INVALID_RETURN,
          types.ProxDashConnectionStatus.CONNECTED,
      ],
      Optional[Dict]]:
    response = requests.post(
        f'{base_url}/connect',
        data={'apiKey': api_key})
    if response.status_code != 201 or response.text == 'false':
      return types.ProxDashConnectionStatus.API_KEY_NOT_VALID, None
    try:
      api_response = json.loads(response.text)
      # New backend API response format
      if api_response.get('success') and api_response.get('data'):
        return types.ProxDashConnectionStatus.CONNECTED, api_response['data']
      # Old backend API response format
      if 'keyName' in api_response:
        return types.ProxDashConnectionStatus.CONNECTED, api_response
      return types.ProxDashConnectionStatus.PROXDASH_INVALID_RETURN, None
    except Exception:
      return types.ProxDashConnectionStatus.PROXDASH_INVALID_RETURN, None

  def _hide_sensitive_content_logging_record(
      self, logging_record: types.LoggingRecord) -> types.LoggingRecord:
    logging_record = copy.deepcopy(logging_record)
    if logging_record.query_record and logging_record.query_record.prompt:
      logging_record.query_record.prompt = '<sensitive content hidden>'
    if logging_record.query_record and logging_record.query_record.system:
      logging_record.query_record.system = '<sensitive content hidden>'
    if logging_record.query_record and logging_record.query_record.messages:
      logging_record.query_record.messages = [
        {
          'role': 'assistant',
          'content': '<sensitive content hidden>'
        }
      ]
    if (logging_record.response_record and
        logging_record.response_record.response):
      logging_record.response_record.response = '<sensitive content hidden>'
    return logging_record

  def upload_logging_record(self, logging_record: types.LoggingRecord):
    self.apply_external_state_changes()

    if self.status != types.ProxDashConnectionStatus.CONNECTED:
      return
    if ((self.proxdash_options and
         self.proxdash_options.hide_sensitive_content) or
        self._key_info_from_proxdash['permission'] == 'NO_PROMPT'):
      logging_record = self._hide_sensitive_content_logging_record(
        logging_record)

    if logging_record.query_record.messages is not None:
      messages = json.dumps(
          logging_record.query_record.messages,
          indent=2,
          sort_keys=True)
    else:
      messages = None

    if logging_record.query_record.stop is not None:
      stop = logging_record.query_record.stop
      if type(stop) == str:
        stop = [stop]
      stop = json.dumps(stop, indent=2, sort_keys=True)
    else:
      stop = None

    data = {
      'apiKey': self.proxdash_options.api_key,
      'hiddenRunKey': self.hidden_run_key,
      'experimentPath': self.experiment_path,
      'callType': logging_record.query_record.call_type,
      'provider': logging_record.query_record.provider_model.provider,
      'model': logging_record.query_record.provider_model.model,
      'providerModelIdentifier': (
          logging_record.query_record.provider_model.provider_model_identifier),
      'prompt': logging_record.query_record.prompt,
      'system': logging_record.query_record.system,
      'messages': messages,
      'maxTokens': logging_record.query_record.max_tokens,
      'temperature': logging_record.query_record.temperature,
      'stop': stop,
      'hashValue': logging_record.query_record.hash_value,
      'queryTokens': logging_record.query_record.token_count,
      'response': logging_record.response_record.response,
      'error': logging_record.response_record.error,
      'errorTraceback': logging_record.response_record.error_traceback,
      'startUTCDate': logging_record.response_record.start_utc_date.isoformat(),
      'endUTCDate': logging_record.response_record.end_utc_date.isoformat(),
      'localTimeOffsetMinute': (
          logging_record.response_record.local_time_offset_minute),
      'responseTime': (int(
          logging_record.response_record.response_time.total_seconds() * 1000)),
      'estimatedCost': logging_record.response_record.estimated_cost,
      'responseTokens': logging_record.response_record.token_count,
      'responseSource': logging_record.response_source,
      'lookFailReason': logging_record.look_fail_reason,
    }

    try:
      response = requests.post(
          f'{self.proxdash_options.base_url}/logging-record', json=data)
    except Exception as e:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'ProxDash could not log the record. Error: '
              f'{str(e)}'),
          type=types.LoggingType.ERROR)
      return

    if response.status_code != 201:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'ProxDash could not log the record. Status code: '
              f'{response.status_code}, Response: {response.text}'),
          type=types.LoggingType.ERROR)
      return

    try:
      api_response = json.loads(response.text)
    except Exception:
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'ProxDash could not log the record. Invalid JSON response: '
              f'{response.text}'),
          type=types.LoggingType.ERROR)
      return

    if not api_response.get('success'):
      logging_utils.log_proxdash_message(
          logging_options=self.logging_options,
          proxdash_options=self.proxdash_options,
          message=(
              'ProxDash could not log the record. Response: '
              f'{response.text}'),
          type=types.LoggingType.ERROR)

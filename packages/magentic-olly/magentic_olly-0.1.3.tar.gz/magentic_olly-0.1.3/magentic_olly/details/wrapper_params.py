import os
from typing import List, Optional

from opentelemetry import propagate
from opentelemetry.trace import SpanKind
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

from . import constants, magentic_instrumentor

class MagenticWrapperServiceParams:
    def __init__(self, service_name: Optional[str] = None, 
                 instrumentors_list: List[BaseInstrumentor] = [],
                 event: Optional[dict] = None,
                 lambda_context: Optional[object] = None):
        self.service_name = service_name or os.getenv(constants.SERVICE_NAME_ENV_NAME, "lambda-service")
        self.instrumentors_list = instrumentors_list
        self.instrumentors_list += [
            magentic_instrumentor.MagenticInstrumentor
        ]
        self._is_state_machine_event = False
        self._is_event_bridge_event = False
        self._main_event_data = None
        self.event = event
        self.lambda_context = lambda_context
        self.arn = hasattr(lambda_context, 'invoked_function_arn') and lambda_context.invoked_function_arn or None
        self.account_id = self._extract_account_id_from_arn(self.arn)
        self.region = self._extract_region_from_arn(self.arn)
        self._init()
        self.carrier:dict[str, str] = self._create_carrier()
        self.payload:dict[str, str] = self._create_payload()
        
    
    @property
    def otel_context(self):
        propagator = propagate.get_global_textmap()
        return propagator.extract(self.carrier)
    
    @property
    def client_service_name(self):
        if not self.has_magentic_span_attrs:
            return None
        return self.magentic_span_attrs.get(constants.CLIENT_NAME_KEY, None)
    
    @property
    def has_client_service_name(self):
        return self.client_service_name is not None
    
    @property
    def instance_id(self):
        if self.lambda_context and hasattr(self.lambda_context, 'aws_request_id'):
            return self.lambda_context.aws_request_id
        return None
    
    @property
    def has_instance_id(self):
        return self.instance_id is not None

    @property
    def is_state_machine_event(self):
        return self._is_state_machine_event

    @property
    def is_event_bridge_event(self):
        return self._is_event_bridge_event

    @property
    def main_event_data(self):
        return self._main_event_data
    
    def _init(self):
        self._main_event_data = self.event
        self._is_state_machine_event = (constants.STATE_MACHINE == self._get_serverless_system(self._main_event_data))
        if self._is_state_machine_event and self._is_state_machine_start_event():
            self._main_event_data = self._main_event_data.get(constants.STATE_MACHINE_ORIGINAL_PAYLOAD_KEY, {})
            
        details = self._get_details()
        if details:
            self._is_event_bridge_event = (constants.EVENT_BRIDGE == self._get_serverless_system(details))

    def _get_details(self):
        main_event_keys = ['Detail', 'detail']
        details = self._get_first_value(main_event_keys)
        return details

    @staticmethod
    def _get_serverless_system(event):
        return event.get(constants.MAGENTIC_SPAN_ATTRS, {}).get(constants.SERVERLESS_SYSTEM_KEY, None)

    def _get_first_value(self, keys):
        for key in keys:
            if key in self.main_event_data:
                return self.main_event_data[key]
        return None

    @property
    def service_span_kind(self):
        if self.is_event_bridge_event:
            print("Detected EventBridge event, setting span kind to CON")
            return SpanKind.CONSUMER
        print("Detected non-EventBridge event, setting span kind to SERVER")
        return SpanKind.SERVER
    
    @property
    def magentic_span_attrs(self) -> dict:
        attrs = self.main_event_data.get(constants.MAGENTIC_SPAN_ATTRS, {})
        if self.is_state_machine_event:
            attrs.update(self.event.get(constants.MAGENTIC_SPAN_ATTRS, {}))
        if not self.is_event_bridge_event:
            return attrs
        self._add_event_bridge_attrs(attrs)
        attrs.update(self._get_details().get(constants.MAGENTIC_SPAN_ATTRS, {}))
        return attrs

    def _add_event_bridge_attrs(self, attrs):
        attrs[constants.SERVERLESS_SYSTEM_KEY] = constants.EVENT_BRIDGE
        event_bridge_bus = self._get_details().get(constants.MAGENTIC_SPAN_ATTRS, {}).get(constants.AWS_EVENT_BRIDGE_BUS_KEY, None)
        account_id = self._get_first_value(['Account', 'account'])
        region = self._get_first_value(['Region', 'region'])
        bus_arn = f'arn:aws:events:{region}:{account_id}:event-bus/{event_bridge_bus}' if account_id and region and event_bridge_bus else None
        if event_bridge_bus:
            attrs[constants.AWS_EVENT_BRIDGE_BUS_KEY] = event_bridge_bus
        if bus_arn:
            attrs[constants.AWS_EVENT_BRIDGE_BUS_ARN] = bus_arn
        event_bridge_source = self._get_first_value(['Source', 'source'])
        if event_bridge_source:
            attrs[constants.AWS_EVENT_BRIDGE_SOURCE_KEY] = event_bridge_source
        event_bridge_detail_type = self._get_first_value(['DetailType', 'detail-type'])
        if event_bridge_detail_type:
            attrs[constants.AWS_EVENT_BRIDGE_DETAIL_TYPE_KEY] = event_bridge_detail_type
        

    @property
    def has_magentic_span_attrs(self):
        return (constants.MAGENTIC_SPAN_ATTRS in self.main_event_data) or self.is_event_bridge_event

    @property
    def propagation_tracing_context(self) -> dict:
        tracing_context = {}
        tracing_context[constants.MAGENTIC_SPAN_ATTRS] = {}
        for key, value in self.magentic_span_attrs.items():
            if key not in constants.IGNORE_PROPAGATION_KEYS:
                tracing_context[constants.MAGENTIC_SPAN_ATTRS][key] = value
        tracing_context[constants.MAGENTIC_SPAN_ATTRS][constants.CLIENT_NAME_KEY] = self.service_name
        return tracing_context

    def _create_carrier(self) -> dict:
        source = self._get_details() if self.is_event_bridge_event else self.main_event_data
        carrier = source.get(constants.OTEL_TRACE_CONTEXT_KEY, {})
        return carrier

    def _create_payload(self) -> dict:
        if self.is_state_machine_event and self._is_state_machine_start_event():
            return self.event.get(constants.STATE_MACHINE_ORIGINAL_PAYLOAD_KEY, {})
        return self.event
    
    def _is_state_machine_start_event(self) -> bool:
        return self.event.get(constants.MAGENTIC_SPAN_ATTRS, {}).get(constants.STATE_MACHINE_START_EVENT_KEY, False)

    @staticmethod
    def _extract_account_id_from_arn(arn: Optional[str]) -> Optional[str]:
        if arn:
            parts = arn.split(':')
            if len(parts) > 4:
                return parts[4]
        return None

    @staticmethod
    def _extract_region_from_arn(arn: Optional[str]) -> Optional[str]:
        if arn:
            parts = arn.split(':')
            if len(parts) > 3:
                return parts[3]
        return None
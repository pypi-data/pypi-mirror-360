from xmlrpc import client
import boto3
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

from . import params, event_bridge_instrumentor
    
class MagenticInstrumentor(BaseInstrumentor):
    _original_boto3_client = boto3.client
    _params_hook_dict = {
        'TableName': 'aws.dynamodb.table_name',
        'Bucket': 'aws.s3.bucket_name',
    }
    _exporter = None
    def instrumentation_dependencies(self):
        return []
    
    def _instrument(self, **kwargs):
        RequestsInstrumentor().instrument()
        HTTPXClientInstrumentor().instrument()
        URLLibInstrumentor().instrument()
        event_bridge_instrumentor.EventBridgeInstrumentor().instrument()
        self._instrument_botocore()

    def _uninstrument(self, **kwargs):
        RequestsInstrumentor().uninstrument()
        HTTPXClientInstrumentor().uninstrument()
        URLLibInstrumentor().uninstrument()
        event_bridge_instrumentor.EventBridgeInstrumentor().uninstrument()
        BotocoreInstrumentor().uninstrument()
        return super().uninstrument(**kwargs)

    def _instrument_botocore(self):
        botocore_instrumentor = BotocoreInstrumentor()
        botocore_instrumentor.uninstrument()
        botocore_instrumentor.instrument(
            request_hook=self._perform_botocore_request_hook,
        )
    
    def _perform_botocore_request_hook(self, span, service_name, operation_name, api_params):
        for key, value in self._params_hook_dict.items():
            if key in api_params:
                span.set_attribute(value, api_params[key])

    
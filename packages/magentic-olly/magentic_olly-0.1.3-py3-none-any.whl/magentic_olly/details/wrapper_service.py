from opentelemetry import propagate, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.trace import SpanKind, Status, StatusCode
from .wrapper_params import MagenticWrapperServiceParams
from . import constants, filter_exporter

class MagenticWrapperService:
    
    
    def __init__(self, params: MagenticWrapperServiceParams):
        self._params:MagenticWrapperServiceParams = params
        self._current_otel_context = self._params.otel_context
        self._client_span = None
        self._processor = self._get_batch_span_processor()
        

    def run_lambda_handler(self, func, *args, **kwargs):
       
        self._perform_pre_processing()
        
        response = {}
        with self._create_service_span_context_manager(func.__name__) as service_span:
            response = func(self._params.payload, self._params.lambda_context, *args, **kwargs)
            if response is None:
                response = {}
            self._set_span_attributes(service_span, response)
            self._inject_tracing_context(response)
            
        response = self._perform_post_processing(response)
        return response
            

    def _perform_pre_processing(self):
        if self._should_create_client_spans():
            self._create_client_service_tracer_provider()
            self._client_span = self._create_client_span()
         
        if self._client_span:
            self._current_otel_context = trace.set_span_in_context(self._client_span)
        
        self._create_current_service_tracer_provider()
        self._instrument_external_libs()
    
    def _perform_post_processing(self, response):
        if self._client_span and response:
            self._set_span_attributes(self._client_span, response)
            self._client_span.end()
        self._processor.force_flush()    
        return response
        
    def _should_create_client_spans(self):
        return self._params.has_client_service_name and not self._params.is_event_bridge_event

    def _create_client_service_tracer_provider(self):
        service_name = self._params.client_service_name
        self._create_tracer_provider(service_name)
        
    def _create_client_span(self):
        if not self._params.has_client_service_name:
            return None
        client_tracer = trace.get_tracer(__name__)
        client_span = client_tracer.start_span("retro-client-span", context=self._current_otel_context, kind=SpanKind.CLIENT)
        self._set_span_resource_attributes(client_span)
        return client_span
    
    def _set_span_attributes(self, service_span, response):
        self._set_span_resource_attributes(service_span)
        self._set_span_magentic_attributes(service_span)
        self._set_span_response_attributes(service_span, response)

    def _set_span_resource_attributes(self, span):
        if self._params.has_instance_id:
            span.set_attribute("server.instance.id", self._params.instance_id)
            
    def _set_span_magentic_attributes(self, span):
        if not self._params.has_magentic_span_attrs:
            return
        attrs = self._params.magentic_span_attrs
        for key, value in attrs.items():
            span.set_attribute(key, value)
            
    def _set_span_response_attributes(self, span, response):
        status_code = response.get("statusCode", None)
        if status_code is None:
            return
        if isinstance(status_code, int) and status_code >= 400:
            span.set_status(Status(StatusCode.ERROR))
        else:
            span.set_status(Status(StatusCode.OK))
        span.set_attribute("response.status_code", status_code)

    def _create_current_service_tracer_provider(self):
        self._create_tracer_provider(self._params.service_name)
    

    def _create_service_span_context_manager(self, func_name):
        service_tracer = trace.get_tracer(__name__)
        span_manager = service_tracer.start_as_current_span(func_name, 
                            context=self._current_otel_context,
                            kind=self._params.service_span_kind)
        return span_manager
    
    def _create_tracer_provider(self, service_name):
        resource_attributes = {"service.name": service_name}
        if self._params.has_instance_id:
            resource_attributes["server.instance.id"] = self._params.instance_id
        if self._params.arn:
            resource_attributes["resource.arn"] = self._params.arn
            resource_attributes["resource.platform"] = "AWS"
            resource_attributes["resource.type"] = "Lambda"
        if self._params.account_id:
            resource_attributes["aws.account.id"] = self._params.account_id
        if self._params.region:
            resource_attributes["aws.account.region"] = self._params.region
        resource = Resource.create(resource_attributes)
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(self._processor)
        trace._TRACER_PROVIDER = tracer_provider
    
    def _get_span_processor(self) -> SimpleSpanProcessor:
        exporter = filter_exporter.FilterExporter()
        return SimpleSpanProcessor(exporter)

    def _get_batch_span_processor(self) -> BatchSpanProcessor:
        exporter = filter_exporter.FilterExporter()
        return BatchSpanProcessor(exporter, max_export_batch_size=5, schedule_delay_millis=500)
        

    def _instrument_external_libs(self):
        for instrumentor in self._params.instrumentors_list:
            instrumentor().uninstrument()
            instrumentor().instrument()    

    def _inject_tracing_context(self, response:dict[str, any]):
        response.update(self._params.propagation_tracing_context)
        propagator = propagate.get_global_textmap()
        otel_context = {}
        propagator.inject(otel_context)
        response[constants.OTEL_TRACE_CONTEXT_KEY] = otel_context


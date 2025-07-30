from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from . import params

class FilterExporter(OTLPSpanExporter):
    _http_instrumentation_params = None
    
    def __init__(self) -> None:
        self._params = FilterExporter._http_instrumentation_params
        if not self._params:
            print('WARNING: No instrumentation parameters provided. Using default endpoint and token.')
            super().__init__()
            return
        super().__init__(endpoint=self._params.endpoint, 
                         headers={"Authorization": f"Bearer {self._params.token}"})

    def export(self, spans) -> SpanExportResult:
        if not self._params:
            print('WARNING: No instrumentation parameters provided. Skipping export.')
            return SpanExportResult.FAILURE
        
        filtered_spans = []
        for span in spans:
            if span.name == "EventBridge.PutEvents" and span.kind == SpanKind.CLIENT:
                continue
            filtered_spans.append(span)
                
        if filtered_spans:
            return super().export(filtered_spans)
        return SpanExportResult.SUCCESS
    
    @staticmethod
    def set_http_params(params: params.HttpExportParams):
        FilterExporter._http_instrumentation_params = params

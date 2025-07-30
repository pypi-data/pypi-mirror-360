from functools import wraps

from .details import filter_exporter, wrapper_service, params

def magentic_wrapper(wrapped_service_name, instrumentors_list=[]):
    def _magentic_wrapper(func):
        @wraps(func)
        def wrapper(event, context, *args, **kwargs):
            service_params = wrapper_service.MagenticWrapperServiceParams(
                service_name=wrapped_service_name,
                instrumentors_list=instrumentors_list,
                event=event,
                lambda_context=context
            )
            
            magentic_service = wrapper_service.MagenticWrapperService(service_params)
            response = magentic_service.run_lambda_handler(func, *args, **kwargs)
            return response
        
        return wrapper
    return _magentic_wrapper

def set_http_export_params(params: params.HttpExportParams):
    filter_exporter.FilterExporter.set_http_params(params)


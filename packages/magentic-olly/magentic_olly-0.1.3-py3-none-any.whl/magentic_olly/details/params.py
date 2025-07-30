import os
from typing import List, Optional
from pydantic import BaseModel
from typing import Optional
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor


class HttpExportParams(BaseModel):
    endpoint: str
    token: Optional[str] = None


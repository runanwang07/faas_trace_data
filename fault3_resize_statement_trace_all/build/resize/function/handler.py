import logging
import json
import base64
import logging
from urllib.request import urlopen
from PIL import Image
import io
import os
import requests as reqs
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import time

logging.basicConfig(
    format='[%(levelname)s] %(filename)s:%(lineno)d: %(message)s', level=logging.DEBUG)


def handle(req):
    span_exporter = OTLPSpanExporter(
        # optional
        endpoint=os.environ.get('COLLECTOR_ADDR'),
        # credentials=ChannelCredentials(credentials),
        # headers=(("metadata", "metadata")),
    )

    trace.set_tracer_provider(TracerProvider(resource=Resource.create(
        {SERVICE_NAME: os.environ.get(
            'SERVICE_NAME'), "PodName": os.environ.get('HOSTNAME')},
    )))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(span_exporter)
    )

    # Configure the tracer to use the collector exporter
    tracer = trace.get_tracer_provider().get_tracer(__name__)

    with tracer.start_as_current_span("resizeImage"):
        span = trace.get_current_span()
        trace_id = format(span.get_span_context().trace_id, "032x")
        logging.debug("Request TraceID: {}".format(trace_id))

        with tracer.start_as_current_span("loadImage"):
            try:
                image_url = req
                logging.debug("IPredicting from url: {} ".format(image_url))
                with urlopen(image_url) as testImage:
                    time.sleep(0.1)
                    image = Image.open(testImage)
            except:
                response_content = 'Bad input'
                return response_content

            w, h = image.size

            if h < 400 and w < 400:
                with tracer.start_as_current_span("less400"):
                    with tracer.start_as_current_span("less400ByteIo"):
                        img_byte_arr = io.BytesIO()
                        with tracer.start_as_current_span("less400ImageCovert"):
                            image.convert('RGB').save(
                                img_byte_arr, format='JPEG')
                            with tracer.start_as_current_span("less400ImageEncode"):
                                img_data = base64.encodebytes(
                                    img_byte_arr.getvalue()).decode('utf-8')

                                return img_data
            else:
                with tracer.start_as_current_span("large400"):
                    new_size = (400 * w // h, 400) if (h >
                                                       w) else (400, 400 * h // w)

                    with tracer.start_as_current_span("large400ImageResize"):
                        if max(new_size) / max(image.size) >= 0.5:
                            method = Image.BILINEAR
                        else:
                            method = Image.BICUBIC

                        image = image.resize(new_size, method)

                        with tracer.start_as_current_span("large400ByteIo"):
                            img_byte_arr = io.BytesIO()
                            with tracer.start_as_current_span("large400ImageCovert"):
                                image.convert('RGB').save(
                                    img_byte_arr, format='JPEG')

                                with tracer.start_as_current_span("large400ImageEncode"):
                                    img_data = base64.encodebytes(
                                        img_byte_arr.getvalue()).decode('utf-8')

                                return img_data

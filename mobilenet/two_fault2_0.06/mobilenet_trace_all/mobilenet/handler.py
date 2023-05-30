import logging
import os
import time
import onnxruntime
import numpy as np
from PIL import Image
from urllib.request import urlopen
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

logging.basicConfig(
    format='[%(levelname)s] %(filename)s:%(lineno)d: %(message)s', level=logging.DEBUG)

scriptpath = os.path.abspath(__file__)
scriptdir = os.path.dirname(scriptpath)
filename = os.path.join(scriptdir, 'mobilenetv2-7.onnx')
labels_filename = os.path.join(scriptdir, 'synset.txt')

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


def handle(req):
    with tracer.start_as_current_span("mobilenet"):
        span = trace.get_current_span()
        trace_id = format(span.get_span_context().trace_id, "032x")
        logging.debug("Request TraceID: {}".format(trace_id))

        with tracer.start_as_current_span("loadImage"):
            try:
                image_url = req
                logging.debug("IPredicting from url: {} ".format(image_url))
                with urlopen(image_url) as testImage:
                    image = Image.open(testImage)
            except:
                response_content = 'Bad input'
                return response_content

            with tracer.start_as_current_span("resizeImage"):
                w, h = image.size
                new_size = (1600 * w // h, 1600) if (h >
                                                     w) else (1600, 1600 * h // w)
                if max(new_size) / max(image.size) >= 0.5:
                    method = Image.BILINEAR
                else:
                    method = Image.BICUBIC
                image = image.resize(new_size, method)

                exif_orientation_tag = 0x0112
                if hasattr(image, '_getexif'):
                    with tracer.start_as_current_span("hasAttr"):
                        exif = image._getexif()
                        if exif != None and exif_orientation_tag in exif:
                            with tracer.start_as_current_span("getOrientation"):
                                orientation = exif.get(exif_orientation_tag, 1)
                                orientation -= 1
                                if orientation >= 4:
                                    with tracer.start_as_current_span("imageTRANSPOSE"):
                                        image = image.transpose(
                                            Image.TRANSPOSE)
                                elif orientation == 2 or orientation == 3 or orientation == 6 or orientation == 7:
                                    with tracer.start_as_current_span("imageFLIP_TOP_BOTTOM"):
                                        image = image.transpose(
                                            Image.FLIP_TOP_BOTTOM)
                                elif orientation == 1 or orientation == 2 or orientation == 5 or orientation == 6:
                                    with tracer.start_as_current_span("imageFLIP_LEFT_RIGHT"):
                                        image = image.transpose(
                                            Image.FLIP_LEFT_RIGHT)

                with tracer.start_as_current_span("resizeTargetSize"):
                    image_np = np.array(image)
                    img = image_np[:, :, (2, 1, 0)]
                    targetSize = (256, 256)
                    resize_image = np.empty(
                        (targetSize[0], targetSize[1], img.shape[2]), dtype=np.uint8)
                    img = resize_image

                    with tracer.start_as_current_span("convertImage"):
                        h, w = img.shape[:2]
                        cropx = 224
                        cropy = 224
                        startx = max(0, w//2-(cropx//2) - 1)
                        starty = max(0, h//2-(cropy//2) - 1)
                        resize_image = img[starty:starty +
                                           cropy, startx:startx+cropx]
                        ximg = image.convert('RGB')

                        with tracer.start_as_current_span("resizeXimg"):
                            ximg_resize = ximg.resize((224, 224))

                            with tracer.start_as_current_span("preprocessX"):
                                ximg224 = np.array(ximg_resize)
                                ximg224 = ximg224 / 255
                                x = ximg224.transpose(2, 0, 1)
                                x = x[np.newaxis, :, :, :]
                                x = x.astype(np.float32)

                                with tracer.start_as_current_span("getSession"):
                                    session = onnxruntime.InferenceSession(
                                        filename)
                                    time.sleep(0.06)

                                    with tracer.start_as_current_span("getModelmeta"):
                                        session.get_modelmeta()

                                        with tracer.start_as_current_span("runSession"):
                                            input_name = session.get_inputs()[
                                                0].name
                                            output_name = session.get_outputs()[
                                                0].name

                                            probs = session.run(
                                                [output_name], {input_name: x})
                                            time.sleep(0.06)
                                            results = np.argsort(
                                                -(probs[0][0]))

                                            with tracer.start_as_current_span("readLables"):
                                                with open(labels_filename, 'r') as f:
                                                    labels = [l.rstrip()
                                                              for l in f]
                                                result = labels[results[0]]

                                                return result

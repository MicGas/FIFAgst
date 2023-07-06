#!/usr/bin/env python3

# http://docs.gstreamer.com/display/GstSDK/Basic+tutorial+2%3A+GStreamer+concepts

import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version("GLib", "2.0")
gi.require_version("GObject", "2.0")
from gi.repository import Gst, GLib, GObject

# initialize GStreamer
Gst.init(None)

#create the elements
#   first source and properties
source = Gst.ElementFactory.make("srtsrc","source")
source.set_property("uri","srt://srt.nrkupload.com:19557")
source.set_property("passphrase","testtesttest")
#source.set_property("pbkeylen", 16)
#   so other elements
tsdemux = Gst.ElementFactory.make("tsdemux", "tsdemux")
queue1 = Gst.ElementFactory.make("queue", "queue1")
h264parse = Gst.ElementFactory.make("h264parse", "h264parse")
avdec_h264 = Gst.ElementFactory.make("avdec_h264", "avdec_h264")
videoconvert = Gst.ElementFactory.make("videoconvert", "video-convert")
sink = Gst.ElementFactory.make("autovideosink", "sink")

# create the empty pipeline
pipeline = Gst.Pipeline.new("test-pipeline")

if not pipeline or not source or not queue1 or not tsdemux or not h264parse or not avdec_h264 or not videoconvert or not sink:
    print("ERROR: Not all elements could be created")
    sys.exit(1)

# build the pipeline
#pipeline.add(source, tsdemux, queue1,h264parse, avdec_h264, videoconvert, sink)

pipeline.add(source)
pipeline.add(tsdemux)
pipeline.add(queue1)
pipeline.add(h264parse)
pipeline.add(avdec_h264)
pipeline.add(videoconvert)
pipeline.add(sink)

# Link the elements together
source.link(tsdemux)
tsdemux.link(queue1)
queue1.link(h264parse)
h264parse.link(avdec_h264)
avdec_h264.link(videoconvert)
videoconvert.link(sink)


if source.link(tsdemux):
    print('yes')

if not source.link(tsdemux):
    print("ERROR: Could not link source to tsdemux")
    sys.exit(1)

if not tsdemux.link(queue1):
    print("ERROR: Could not link tsdemux to queue1")
    sys.exit(1)

if not queue1.link(h264parse):
    print("ERROR: Could not link queue1 to h264parse")
    sys.exit(1)

if not h264parse.link(avdec_h264):
    print("ERROR: Could not link h264parse to avdec_h264")
    sys.exit(1)

if not avdec_h264.link(videoconvert):
    print("ERROR: Could not link avdec_h264 to videoconvert")
    sys.exit(1)

if not videoconvert.link(sink):
    print("ERROR: Could not link videoconvert to sink")
    sys.exit(1)

    
# start playing
ret = pipeline.set_state(Gst.State.PLAYING)
if ret == Gst.StateChangeReturn.FAILURE:
    print("ERROR: Unable to set the pipeline to the playing state")

# wait for EOS or error
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS
)

if msg:
    t = msg.type
    if t == Gst.MessageType.ERROR:
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)
        if dbg:
            print("debugging info:", dbg)
    elif t == Gst.MessageType.EOS:
        print("End-Of-Stream reached")
    else:
        # this should not happen. we only asked for ERROR and EOS
        print("ERROR: Unexpected message received.")

pipeline.set_state(Gst.State.NULL)

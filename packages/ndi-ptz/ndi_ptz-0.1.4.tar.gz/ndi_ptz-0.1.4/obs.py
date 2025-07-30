import obspython as obs
from cyndilib import Finder, Receiver, RecvColorFormat, RecvBandwidth

print("preloading…")

finder = Finder()
# finder.open()

print("loading…")

def script_load(_):
  # finder.open()
  pass

def script_unload():
  # finder.close()
  pass

def script_description():
  return "An OBS plugin to control NDI PTZ cameras"

def script_properties():
  props = obs.obs_properties_create()

  # finder.update_sources()
  p_ndi_sources = obs.obs_properties_add_list(props, "ndi_source_name", "NDI Source Name", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

  # for ndi_source in finder:
  #   obs.obs_property_list_add_string(p_ndi_sources, f"{ndi_source.name} ({ndi_source.stream_name})", ndi_source.name)

  return props

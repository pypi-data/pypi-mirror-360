# ndi-ptz

This is a CLI to control an NDI-enabled PTZ camera with a joystick.

Currently, everything in here requires a custom cyndilib,
see https://github.com/nocarryr/cyndilib/pull/25.

## Installation

```shell
uv tool install ndi-ptz

# or
pip install ndi-ptz
```

You also need to install the NDI Runtime,
unless you have the [NDI Tools][ndi-tools] or the [NDI SDK][ndi-sdk] installed

[ndi-tools]: https://ndi.video/tools/
[ndi-sdk]: https://ndi.video/for-developers/ndi-sdk/download/

- Windows: <http://ndi.link/NDIRedistV6>
- MacOS: <http://ndi.link/NDIRedistV6Apple>
- Linux: <https://downloads.ndi.tv/SDK/NDI_SDK_Linux/Install_NDI_SDK_v6_Linux.tar.gz>
  - see also <https://github.com/DistroAV/DistroAV/blob/master/CI/libndi-get.sh>

For further options, like `choco` or `brew`, consult [the DistroAV wiki][distroav].

[distroav]: https://github.com/DistroAV/DistroAV/wiki/1.-Installation#required-components---ndi-runtime

## Quick-Start

```shell
$ ndi-ptz list-sources
Looking for NDI sources in the next 5 seconds
TAIL_AIR_006666 (OBSBOT)

$ ndi-ptz list-joysticks
Looking for joysticks in the next 5 seconds
Nintendo Switch Pro Controller (0)

$ ndi-ptz control --source-name "TAIL_AIR_006666 (OBSBOT)" --joystick-instance 0
```

## Supported Joysticks

Currently only the following joysticks are supported:

- [Nintendo Switch Pro Controller](#nintendo-switch-pro-controller)

### Nintendo Switch Pro Controller

- You must hold `L` and `R` constantly to control the PTZ.
- Use the _left stick_ to control pan (left/right) and tilt (up/down).
- Use the _right stick_ to control the zoom (up/down).
- Press the _right stick_ to return the camera to the home position.
- Hold the `A` button to trigger the autofocus.

## Development

This project is managed with [UV](https://docs.astral.sh/uv/).

### Build & Publish

```bash
# edit the project version in pyproject.toml
uv sync
git commit -m "Prepare 0.1.4" .
git tag '0.1.4'
rm -rf dist
uv build
uv publish
git push --tags
git push
```

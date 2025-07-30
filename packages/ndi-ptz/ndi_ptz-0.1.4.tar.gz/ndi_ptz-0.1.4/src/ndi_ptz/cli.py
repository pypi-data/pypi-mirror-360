from importlib.metadata import requires

import click
import time

from click import ClickException
from cyndilib import Finder, Receiver, RecvColorFormat, RecvBandwidth

# Nintendo Switch Pro Controllers
LEFT_X_AXIS = 0
LEFT_Y_AXIS = 1
RIGHT_X_AXIS = 2
RIGHT_Y_AXIS = 3
A_BUTTON = 0
L_STICK = 7
R_STICK = 8
L_BUMPER = 9
R_BUMPER = 10


def silent_import_pygame():
    import contextlib
    with contextlib.redirect_stdout(None):
        import pygame
        return pygame


@click.group()
def cli():
    pass


@click.command()
@click.option("--timeout", default=5, help='The number of seconds to wait for any NDI sources to be detected')
def list_sources(timeout: int):
    click.echo(f"Looking for NDI sources in the next {timeout} seconds", err=True)

    with Finder() as finder:
        if not finder.wait(timeout=timeout):
            raise ClickException(f"No sources detected after {timeout} seconds")

        for source in finder:
            click.echo(source.name)


@click.command()
@click.option("--timeout", default=5, help='The number of seconds to wait for any joystick to be detected')
def list_joysticks(timeout: int):
    click.echo(f"Looking for joysticks in the next {timeout} seconds", err=True)

    pygame = silent_import_pygame()
    pygame.init()
    pygame.joystick.init()
    joysticks = []

    for _ in range(0, timeout):
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        if joysticks:
            break

        time.sleep(1)

    if not joysticks:
        raise ClickException(f"No joysticks detected after {timeout} seconds")

    for joystick in joysticks:
        click.echo(f"{joystick.get_name()} ({joystick.get_instance_id()})")


@click.command()
@click.option("-j", "--joystick-instance", default=0, help='The instance id of the joystick.')
@click.option("--joystick-timeout", default=5, help='The number of seconds to wait for the joystick to be detected.')
@click.option("-s", "--source-name", required=True, help='The name of the source.')
@click.option("--source-timeout", default=5, help='The number of seconds to wait for any NDI sources to be detected.')
@click.option("--connect-timeout", default=5,
              help='The number of seconds to wait for the connection to the NDI source to establish.')
@click.option("-n", "--receiver-name", default="ndi_ptz",
              help='The name used to identify this program when opening the connection to the NDI source.')
@click.option("--motion-threshold", default=0.1,
              help='The minimal amount of motion which the joystick must report before it is translated into a PTZ command.')
@click.option("--speed-factor", default=0.1,
              help='Reduce the reported movement distance of the joystick by this factor before sending it as PTZ command.')
@click.option("+r/-r", "--rumble/--no-rumble", default=True, help='Enable the rumble for feedback.')
def control(joystick_instance: int, joystick_timeout: int, source_name: str, source_timeout: int, connect_timeout: int,
            receiver_name: str, motion_threshold: float, speed_factor: float, rumble: bool):
    receiver = None
    do_rumble = rumble

    with Finder() as finder:
        if not finder.wait(timeout=source_timeout):
            raise ClickException("No sources detected")

        source = finder.get_source(source_name)

        if not source:
            raise ClickException(f"Source '{source_name}' not found")

        receiver = Receiver(
            color_format=RecvColorFormat.fastest,
            bandwidth=RecvBandwidth.metadata_only,
            recv_name=receiver_name,
        )
        receiver.set_source(source)

        for _ in range(0, connect_timeout * 10):
            time.sleep(.1)
            if receiver.is_connected():
                break

        if not receiver.is_connected():
            raise ClickException(f"Can't connect to the NDI device '{source_name}'")

        if not receiver.is_ptz_supported():
            raise ClickException(f"The NDI source '{source}' does not indicate PTZ support")

    ptz = receiver.ptz

    pygame = silent_import_pygame()
    pygame.init()
    pygame.joystick.init()

    joysticks = []
    joystick = None
    for _ in range(0, 10):
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

        if not joysticks:
            time.sleep(1)
            continue

        if joystick_instance > (len(joysticks) - 1):
            continue

        joystick = joysticks[joystick_instance]

    if not joysticks:
        raise ClickException(f"No joysticks detected after {joystick_timeout} seconds")

    if not joystick:
        raise ClickException(f"Joystick {joystick_instance} was not detected after {joystick_timeout} seconds")

    joystick.init()
    click.echo(
        f"Using joystick '{joystick.get_name()}' ({joystick.get_instance_id()}) "
        f"to control camera '{receiver.source_name}'"
    )
    if do_rumble:
        joystick.rumble(low_frequency=0.5, high_frequency=0.5, duration=250)

    autofocus_on = False
    home_on = False
    control_on = False

    click.echo("Use L_BUMP and R_BUMP to enable remote control.")
    click.echo("Use L_STICK for pan and tilt, R_STICK for zoom.")
    click.echo("Use BUTTON_A to trigger the autofocus.")
    while True:
        pygame.event.pump()

        rounding = 2
        p2 = round(joystick.get_axis(LEFT_X_AXIS) * -1, rounding)
        t2 = round(joystick.get_axis(LEFT_Y_AXIS) * -1, rounding)
        z2 = round(joystick.get_axis(RIGHT_Y_AXIS) * -1, rounding)

        threshold = motion_threshold
        pan = p2 if p2 < threshold * -1 or threshold < p2 else 0.0
        tilt = t2 if t2 < threshold * -1 or threshold < t2 else 0.0
        zoom = z2 if z2 < threshold * -1 or threshold < z2 else 0.0

        take_control = joystick.get_button(L_BUMPER) and joystick.get_button(R_BUMPER)
        trigger_af = joystick.get_button(A_BUTTON)
        trigger_home = joystick.get_button(L_STICK) or joystick.get_button(R_STICK)

        if not take_control and control_on:
            ptz.pan_and_tilt(.0, .0)
            ptz.zoom(.0)
            control_on = False
            if do_rumble:
                joystick.rumble(low_frequency=0.5, high_frequency=0.5, duration=150)
        elif take_control:
            if not control_on:
                control_on = True
                if do_rumble:
                    joystick.rumble(low_frequency=0.5, high_frequency=0.5, duration=50)

            if not trigger_home:
                # click.echo(f"Motion p {pan} t {tilt} z {zoom} speed_factor {speed_factor}")
                ptz.pan_and_tilt(pan * speed_factor, tilt * speed_factor)
                ptz.zoom(zoom * speed_factor)

            if trigger_home and not home_on:
                ptz.set_pan_and_tilt_values(.0, .0)
                ptz.set_zoom_level(.0)
                home_on = True
                if do_rumble:
                    joystick.rumble(low_frequency=0.5, high_frequency=0.5, duration=0)
            elif not trigger_home and home_on:
                home_on = False
                if do_rumble:
                    joystick.stop_rumble()

            if trigger_af and not autofocus_on:
                ptz.autofocus()
                autofocus_on = True
            elif not trigger_af and autofocus_on:
                autofocus_on = False

        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

    joystick.quit()
    pygame.quit()
    receiver.disconnect()


cli.add_command(control)
cli.add_command(list_joysticks)
cli.add_command(list_sources)

if __name__ == "__main__":
    cli()

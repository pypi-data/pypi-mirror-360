from typing import Optional

import typer

from viva.env import DroneEnv

app = typer.Typer()

@app.command()
def main(
    video_path: str = typer.Argument(..., help="Path to the background video file (e.g., videos/drone.MP4)"),
    render_mode: Optional[str] = typer.Option("human", help="The rendering mode ('human' or 'rgb_array')"),
    fixed: bool = typer.Option(False, help="Whether the background is a fixed image or a video"),
    show_fps_flag: bool = typer.Option(False, help="Whether to display the FPS"),
):
    """Run the ViVa SAFELAND simulation.
    """
    try:
        env = DroneEnv(
            render_mode=render_mode, video=video_path, fixed=fixed, show_fps_flag=show_fps_flag
        )
    except Exception as e:
        typer.echo(f"Error initializing environment: {e}")
        raise typer.Exit(code=1)

    obs, info = env.reset()
    terminated = False
    count = 0
    while not terminated and count < 100:
        count += 1
        # actions = env.action_space.sample()
        actions = [0.0, 0.0, 0.0]
        try:
            obs, terminated, info = env.step(actions)
        except Exception as e:
            typer.echo(f"Error during step: {e}")
            raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
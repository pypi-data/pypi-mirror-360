import re
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
import pygame

from viva.modules.render_drone import RenderDrone
from viva.modules.simulator import Simulator


class DroneEnv:
    """A simulated environment for validating vision-based drone navigation.

    This class provides a Gymnasium-like environment for a drone navigating in a
    simulated world. It handles rendering, physics, and state management.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}
    """Metadata for the environment, following Gymnasium's convention."""

    def __init__(
        self,
        render_mode: Optional[str] = None,
        video: str = "",
        fixed: bool = False,
        show_fps_flag: bool = False,
    ):
        """Initializes the DroneEnv.

        Args:
            render_mode (Optional[str]): The rendering mode ('human' or 'rgb_array').
            video (str): The path to the background video.
            fixed (bool): Whether the background is a fixed image or a video.
            show_fps_flag (bool): Whether to display the FPS.
        """
        super(DroneEnv, self).__init__()
        self.render_mode = render_mode

        self.frame_size = np.array((3840, 2160))
        self.window_size = np.array((1280, 720))
        self.drone_view_size = np.array((480, 288))

        srt_path = video.split(".")[0] + ".SRT"
        self.height = self._get_height(srt_path)
        self.simulator = Simulator(
            input_size=self.frame_size,
            output_size=self.drone_view_size,
            height_dron=self.height,
        )
        self.renderer: Optional[RenderDrone] = None

        self.background_path: str = video
        self.cam: Optional[cv2.VideoCapture] = None
        self.frame: Optional[np.ndarray] = None
        self.fixed: bool = fixed

        self.window: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None

        self.linear_factor: float = 15.0
        self.current_step: int = 0
        self.terminated_step: int = 5000

        self.show_fps_flag: bool = show_fps_flag
        if self.show_fps_flag:
            self.prev = cv2.getTickCount()

    def _get_height(self, srt_path: str) -> Optional[float]:
        """Extracts the relative altitude from an SRT file.

        Args:
            srt_path (str): The path to the SRT file.

        Returns:
            Optional[float]: The relative altitude, or None if not found.
        """
        pat_rel_alt = re.compile(r"rel_alt:\s*([\d\.]+)")
        rel_alt_value = None
        with open(srt_path, "r", encoding="utf-8") as f:
            for line in f:
                match = pat_rel_alt.search(line)
                if match:
                    rel_alt_value = float(match.group(1))
                    break
        return rel_alt_value

    def _show_fps(self) -> None:
        """Calculates and prints the current FPS."""
        current = cv2.getTickCount()
        fps = cv2.getTickFrequency() / (current - self.prev)
        self.prev = current
        print(f"FPS: {fps:.2f}")

    def _update_frame(self, reset: bool = False) -> None:
        """Updates the background frame from the video or image.

        Args:
            reset (bool): Whether to force a reset of the video capture.
        """
        if self.fixed and self.frame is None:
            self.cam = cv2.VideoCapture(self.background_path)
            ret, self.frame = self.cam.read()
            self.cam.release()
        elif not self.fixed:
            if reset and self.cam is not None:
                self.cam.release()
                self.cam = None
            if self.cam is None:
                self.cam = cv2.VideoCapture(self.background_path)
            ret, self.frame = self.cam.read()
            if not ret:
                # Reset the reader if we reach the end of the video
                self.cam.release()
                self.cam = cv2.VideoCapture(self.background_path)
                ret, self.frame = self.cam.read()

    def reset(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Resets the environment to an initial state.

        Returns:
            Tuple[np.ndarray, Dict[str, Any]]: A tuple containing:

            *   **observation (np.ndarray)**: The current drone camera view (RGB image).
            *   **info (Dict[str, Any])**: A dictionary containing auxiliary information,
                such as 'points' (coordinates for rendering), 'drone_state' (position and velocity),
                and 'actions' (the actions taken).
        """
        self.current_step = 0
        self._update_frame(reset=True)
        frame = self.frame.copy()
        lim_y = np.tan(np.radians(41.05)) * self.height
        lim_x = lim_y * 9 / 16

        x_ini = np.random.uniform(-lim_x + 1, lim_x - 1)
        y_ini = np.random.uniform(-lim_y + 1, lim_y - 1)
        z_ini = np.random.uniform(20, min(60, self.height - 1))

        self.simulator.reset(x_ini, y_ini, z_ini)

        actions = np.array([0.0, 0.0, 0.0])
        observation, points, drone_state = self.simulator.step(*actions, frame=frame)

        actions = np.insert(actions, 2, 0.0)  # ! No psi control
        info = {"points": points, "drone_state": drone_state, "actions": actions}

        # Globals for rendering
        self.drone_view = observation
        self.info = info

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, actions: List[float]) -> Tuple[np.ndarray, bool, Dict[str, Any]]:
        """Executes one time step in the environment.

        Args:
            actions (List[float]): The actions to take in the environment.

        Returns:
            Tuple[np.ndarray, bool, Dict[str, Any]]: A tuple containing:

            *   **observation (np.ndarray)**: The current drone camera view (RGB image).
            *   **terminated (bool)**: Whether the episode has terminated. This occurs when:

                *   The simulation reaches 5000 steps (approximately 166 seconds at 30 FPS).
                *   The virtual drone moves outside the simulation boundaries.
            *   **info (Dict[str, Any])**: A dictionary containing auxiliary information,
                such as 'points' (coordinates for rendering), 'drone_state' (position and velocity),
                and 'actions' (the actions taken).
        """
        self._update_frame()
        frame = self.frame.copy()
        actions[0] *= self.linear_factor
        actions[1] *= self.linear_factor
        actions[2] *= self.simulator.drone.g * self.simulator.drone.mass

        observation, points, drone_state = self.simulator.step(*actions, frame=frame)

        actions = np.insert(actions, 2, 0.0)  # ! No psi control
        info = {"points": points, "drone_state": drone_state, "actions": actions}

        self.current_step += 1
        lim_y = np.tan(np.radians(41.05)) * self.height
        lim_x = lim_y * 9 / 16
        terminated = self.current_step >= self.terminated_step
        if (
            abs(drone_state.pos.x) > lim_x
            or abs(drone_state.pos.y) > lim_y
            or drone_state.pos.z >= self.height
            or drone_state.pos.z <= 2
        ):
            terminated = True

        # Globals for rendering
        self.drone_view = observation
        self.info = info

        if self.show_fps_flag:
            self._show_fps()
        if self.render_mode == "human":
            self._render_frame()

        return observation, terminated, info

    def render(self) -> Optional[np.ndarray]:
        """Renders the environment.

        Returns:
            Optional[np.ndarray]: The rendered frame, if render_mode is 'rgb_array'.
        """
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self) -> Optional[np.ndarray]:
        """Renders a single frame.

        Returns:
            Optional[np.ndarray]: The rendered frame, if render_mode is 'rgb_array'.
        """
        if self.renderer is None:
            self.renderer = RenderDrone(
                frame_size=self.frame_size,
                drone_view_size=self.drone_view_size,
                window_size=self.window_size,
            )
        canvas = self.renderer.render(self.frame.copy(), self.drone_view, self.info)
        if self.render_mode == "human":
            if self.window is None:
                pygame.init()
                pygame.display.init()
                pygame.display.set_caption("ViVa-SAFELAND")
                self.window = pygame.display.set_mode(self.window_size)
                self.clock = pygame.time.Clock()
            canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
            canvas = pygame.surfarray.make_surface(np.flip(np.rot90(canvas), 0))
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])
            return None
        else:
            return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)

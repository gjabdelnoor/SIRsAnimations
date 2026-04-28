from manim import *
from manim import ThreeDScene as ManimThreeDScene
import numpy as np
from scipy.integrate import solve_ivp

# ============================================================
# Seasonality of Epidemics — 3D title-slide attractor animation
# Minimal version:
# - static camera
# - no extra text
# - only axis labels remain
# ============================================================

config.frame_width = 16
config.frame_height = 9
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_rate = 60
config.background_color = BLACK


# ----------------------------
# Forced SIR model parameters
# ----------------------------
MU = 0.02
GAMMA = 66.0
BETA0 = 1600.0
DELTA = 0.18
EPSILON = 1e-12

# Visual integration settings
TOTAL_YEARS = 140.0
BURN_IN_YEARS = 55.0
DISPLAY_YEARS = 24.0
SAMPLES_PER_YEAR = 240

# Animation settings
TRACE_SECONDS = 40 / 3
FINAL_HOLD_SECONDS = 5 / 3
FADE_OUT_SECONDS = 99 / 60

# Path downsampling
MAX_PATH_POINTS = 3800


def beta_norm(t: float) -> float:
    return 1.0 + DELTA * np.sin(TAU * t)


def beta(t: float) -> float:
    return BETA0 * beta_norm(t)


def rhs(t, y):
    S, I = y
    dS = MU - MU * S - beta(t) * S * (I + EPSILON)
    dI = beta(t) * S * (I + EPSILON) - (GAMMA + MU) * I
    return [dS, dI]


def integrate_forced_sir():
    n = int(TOTAL_YEARS * SAMPLES_PER_YEAR) + 1
    t_eval = np.linspace(0.0, TOTAL_YEARS, n)

    sol = solve_ivp(
        rhs,
        t_span=(0.0, TOTAL_YEARS),
        y0=[0.050, 1e-6],
        t_eval=t_eval,
        method="DOP853",
        rtol=1e-9,
        atol=1e-13,
        max_step=1.0 / 500.0,
    )

    if not sol.success:
        raise RuntimeError(sol.message)

    t = sol.t
    S = sol.y[0]
    I = sol.y[1]

    start = np.searchsorted(t, BURN_IN_YEARS)
    stop = np.searchsorted(t, BURN_IN_YEARS + DISPLAY_YEARS)

    t = t[start:stop] - t[start]
    S = S[start:stop]
    I = I[start:stop]

    if len(t) > MAX_PATH_POINTS:
        keep = np.linspace(0, len(t) - 1, MAX_PATH_POINTS).astype(int)
        t, S, I = t[keep], S[keep], I[keep]

    W = np.log10(np.maximum(I, 1e-12))
    B = np.array([beta_norm(float(x)) for x in t])

    return t, S, W, B


def make_curve_from_points(points, color=ORANGE, width=4.0, opacity=1.0, smooth=True):
    curve = VMobject()
    if smooth:
        curve.set_points_smoothly(points)
    else:
        curve.set_points_as_corners(points)
    curve.set_stroke(color=color, width=width, opacity=opacity)
    return curve


class SeasonalityAttractorMinimal(ManimThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK

        # Static camera only
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.88)

        t, S, W, B = integrate_forced_sir()

        # ----------------------------
        # 3D axes
        # ----------------------------
        axes = ThreeDAxes(
            x_range=[0.015, 0.075, 0.015],
            y_range=[-12, -1, 2],
            z_range=[0.80, 1.22, 0.10],
            x_length=6.6,
            y_length=4.6,
            z_length=3.2,
            axis_config={
                "stroke_width": 1.0,
                "include_tip": False,
                "include_ticks": True,
                "tick_size": 0.045,
                "color": "#8ad9d6",
            },
        )
        axes.move_to(ORIGIN).shift(DOWN * 0.15 + RIGHT * 0.35)

        # Custom axis tips pointing away from origin
        x_tip = Cone(base_radius=0.06, height=0.18, direction=RIGHT)
        x_tip.set_color("#8ad9d6")
        x_tip.move_to(axes.x_axis.get_end() + RIGHT * 0.09)
        axes.x_axis.add(x_tip)

        y_tip = Cone(base_radius=0.08, height=0.22, direction=DOWN)
        y_tip.set_color("#8ad9d6")
        y_tip.move_to(axes.y_axis.get_start() + DOWN * 0.11)
        axes.y_axis.add(y_tip)

        z_tip = Cone(base_radius=0.06, height=0.18, direction=OUT)
        z_tip.set_color("#8ad9d6")
        z_tip.move_to(axes.z_axis.get_end() + OUT * 0.09)
        axes.z_axis.add(z_tip)

        # Only text remaining: axis labels
        x_label = MathTex("S").scale(0.56).set_color("#b7fff5")
        y_label = MathTex(r"\log_{10} I").scale(0.56).set_color("#b7fff5")
        z_label = MathTex(r"\beta(t)/\beta_0").scale(0.50).set_color("#b7fff5")

        x_label.next_to(axes.x_axis.get_end(), RIGHT, buff=0.12)
        y_label.next_to(axes.y_axis.get_start(), DOWN, buff=0.18)
        z_label.next_to(axes.z_axis.get_end(), OUT, buff=0.12)

        self.add_fixed_orientation_mobjects(x_label, y_label, z_label)

        pts = [axes.c2p(float(s), float(w), float(b)) for s, w, b in zip(S, W, B)]

        # Restrained path glow only
        glow_outer = make_curve_from_points(
            pts,
            color="#ff6a00",
            width=0.9,
            opacity=0.06,
        )
        glow_mid = make_curve_from_points(
            pts,
            color="#ff9b2f",
            width=0.7,
            opacity=0.10,
        )
        core = make_curve_from_points(
            pts,
            color="#ff7a18",
            width=1.25,
            opacity=0.92,
        )

        # Floor grid
        floor = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            x_length=8,
            y_length=6,
            background_line_style={
                "stroke_color": "#1b5858",
                "stroke_width": 0.55,
                "stroke_opacity": 0.20,
            },
            axis_config={
                "stroke_color": "#1b5858",
                "stroke_width": 0.5,
                "stroke_opacity": 0.12,
            },
        )
        floor.rotate(PI / 2, axis=RIGHT)
        floor.shift(DOWN * 2.38 + RIGHT * 0.35)
        floor.set_opacity(0.30)

        self.add(floor, axes, x_label, y_label, z_label)

        self.play(
            Create(glow_outer),
            Create(glow_mid),
            Create(core),
            run_time=TRACE_SECONDS,
            rate_func=linear,
        )

        self.wait(FINAL_HOLD_SECONDS)

        self.play(
            FadeOut(core),
            FadeOut(glow_mid),
            FadeOut(glow_outer),
            run_time=FADE_OUT_SECONDS,
        )


# Alias so your old command still works
class Scene(SeasonalityAttractorMinimal):
    pass
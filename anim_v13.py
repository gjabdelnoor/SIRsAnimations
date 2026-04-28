from manim import *
import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import find_peaks

# ─── parameters ───────────────────────────────────────────────────
mu, gamma = 0.02, 66.0
beta0, delta = 1600.0, 0.18
epsilon = 1e-12
S_INIT, I_INIT = 0.03, 0.0001
YEARS = 250
SAMPLES_PER_YEAR = 1000

config.pixel_height = 2160
config.pixel_width = 3840
config.frame_rate = 60

# ─── model integration (once, at import) ──────────────────────────
def beta(t):
    return beta0 * (1.0 + (delta if (t % 1.0) >= 0.5 else -delta))

def rhs(t, y):
    S, I = y
    b = beta(t)
    dS = mu - mu * S - b * S * (I + epsilon)
    dI = b * S * (I + epsilon) - (gamma + mu) * I
    return [dS, dI]

t_eval = np.linspace(0, YEARS, int(YEARS * SAMPLES_PER_YEAR) + 1)
sol = solve_ivp(rhs, (0, YEARS), [S_INIT, I_INIT],
                t_eval=t_eval, method="DOP853",
                rtol=1e-9, atol=1e-12, max_step=1.0 / 1000)
t_all, S_all, I_all = sol.t, sol.y[0], sol.y[1]

# ─── auto-detect major peaks and build intervals ──────────────────
peaks_all, _ = find_peaks(I_all)
global_max_I = np.max(I_all)
MAJOR_THRESH = 0.20 * global_max_I
major_peak_mask = I_all[peaks_all] > MAJOR_THRESH
major_peaks = peaks_all[major_peak_mask]

INTERVALS = []
for i in range(len(major_peaks) - 1):
    p1i = major_peaks[i]
    p2i = major_peaks[i + 1]

    # post-epidemic S0: first point where S rises after peak
    diff_S = np.diff(S_all[p1i:p2i])
    rise_mask = diff_S > 0
    if np.any(rise_mask):
        s0_idx = p1i + np.argmax(rise_mask)
    else:
        s0_idx = p1i + np.argmin(S_all[p1i:p2i])

    INTERVALS.append({
        "p1_idx": p1i,
        "p2_idx": p2i,
        "s0_idx": s0_idx,
        "s0": float(S_all[s0_idx]),
        "tau": float(t_all[p2i] - t_all[p1i]),
    })

# Skip first 10 intervals (transient), then take 50
SKIP = 10
MAX_POINTS = 50
INTERVALS = INTERVALS[SKIP:SKIP + MAX_POINTS]

# ─── windowing: group intervals by ~5 peaks per window ────────────
PEAKS_PER_WINDOW = 5  # 5 peaks visible = 4 intervals processed per window
INTERVALS_PER_WINDOW = PEAKS_PER_WINDOW - 1

WINDOWS = []
for i in range(0, len(INTERVALS), INTERVALS_PER_WINDOW):
    w = INTERVALS[i:i + INTERVALS_PER_WINDOW]
    if w:
        WINDOWS.append(w)

# ─── helpers ──────────────────────────────────────────────────────
def theoretical_sc():
    return (gamma + mu) / beta0 - mu / 2.0


class ForcedEpidemicTauV13(Scene):
    def construct(self):
        sc = theoretical_sc()

        # ── persistent titles & labels ──
        main_title = Tex(
            r"\textbf{Seasonally forced SIR: inter-epidemic period}",
            font_size=32
        )
        main_title.to_edge(UP, buff=0.35)

        left_title = Tex(r"\textbf{Infectious time series (zoomed)}", font_size=26)
        left_title.shift(UP * 2.6 + LEFT * 3.3)

        left_ylabel = Tex(r"$I(t)$", font_size=24)
        left_ylabel.next_to(left_title, DOWN * 3.5 + LEFT * 0.2)
        left_ylabel.shift(LEFT * 1.2)

        left_xlabel = Tex(r"$t$ (years)", font_size=24)
        left_xlabel.shift(DOWN * 2.3 + LEFT * 0.5)

        # ── right panel (scatter) ──
        right_axes = Axes(
            x_range=[0.015, 0.050, 0.005],
            y_range=[0, 3.2, 0.5],
            x_length=6.0,
            y_length=4.5,
            axis_config={"color": WHITE, "include_tip": False, "tick_size": 0.06},
            tips=False,
        )
        right_axes.shift(RIGHT * 3.3 + UP * 0.3)
        right_axes.x_axis.add_numbers(font_size=16, num_decimal_places=3)
        right_axes.y_axis.add_numbers(font_size=16, num_decimal_places=1)

        right_title = Tex(r"\textbf{Inter-epidemic period}", font_size=26)
        right_title.move_to(right_axes.get_top() + UP * 0.45)

        right_xlabel = Tex(r"$S_0$", font_size=26)
        right_xlabel.next_to(right_axes, DOWN, buff=0.25)

        right_ylabel = Tex(r"$\tau$", font_size=26)
        right_ylabel.next_to(right_axes, LEFT, buff=0.25)

        thresh_line = DashedLine(
            right_axes.c2p(sc, 0),
            right_axes.c2p(sc, 3.2),
            color=RED,
            dash_length=0.08,
        )
        thresh_label = Tex(r"$S_c$", color=RED, font_size=22)
        thresh_label.next_to(thresh_line, UP, buff=0.1)
        thresh_label.shift(RIGHT * 0.15)

        # ── overview strip ──
        overview_axes = Axes(
            x_range=[0, 250, 50],
            y_range=[0, 0.008, 0.004],
            x_length=13.0,
            y_length=0.7,
            axis_config={"color": WHITE, "include_tip": False, "tick_size": 0.04},
            tips=False,
        )
        overview_axes.shift(DOWN * 3.0)
        overview_axes.x_axis.add_numbers(font_size=12)

        overview_label = Tex(r"\textbf{Full trajectory}", font_size=18)
        overview_label.next_to(overview_axes, LEFT, buff=0.15)

        overview_xlabel = Tex(r"$t$ (years)", font_size=18)
        overview_xlabel.next_to(overview_axes, DOWN, buff=0.1)

        overview_pts = np.column_stack((t_all, I_all))
        overview_curve = VMobject()
        overview_curve.set_points_as_corners(
            [overview_axes.c2p(x, y) for x, y in overview_pts]
        )
        overview_curve.set_stroke(BLUE, width=1.0, opacity=0.5)

        # ── intro animation ──
        self.play(Write(main_title), run_time=1.0)
        self.wait(0.5)

        self.play(
            Write(left_title), Write(left_ylabel), Write(left_xlabel),
            Create(right_axes), Write(right_xlabel), Write(right_ylabel),
            Create(thresh_line), Write(thresh_label), Write(right_title),
            Create(overview_axes), Write(overview_xlabel), Write(overview_label),
            Create(overview_curve),
            run_time=1.5
        )
        self.wait(0.5)

        # ── year counter (top-left) ──
        year_text = Tex("Year: --", font_size=20)
        year_text.to_edge(UL, buff=0.3)
        year_text.shift(RIGHT * 0.2)
        self.add(year_text)

        # ── process each window ──
        right_dots_group = VGroup()

        for w_idx, window in enumerate(WINDOWS):
            # window time bounds
            first_p1 = window[0]["p1_idx"]
            last_p2 = window[-1]["p2_idx"]
            t_start = float(t_all[first_p1]) - 0.5
            t_end = float(t_all[last_p2]) + 0.5

            # dynamic tick step based on span
            span = t_end - t_start
            if span <= 5:
                tick_step = 1.0
            elif span <= 10:
                tick_step = 2.0
            else:
                tick_step = 5.0

            # left axes for this window
            left_axes = Axes(
                x_range=[t_start, t_end, tick_step],
                y_range=[0, 0.008, 0.002],
                x_length=6.0,
                y_length=3.8,
                axis_config={"color": WHITE, "include_tip": False, "tick_size": 0.06},
                tips=False,
            )
            left_axes.shift(LEFT * 3.3 + DOWN * 0.2)
            left_axes.x_axis.add_numbers(font_size=16, num_decimal_places=0 if tick_step >= 1 else 1)
            left_axes.y_axis.add_numbers(font_size=16, num_decimal_places=3)

            # full curve for window
            mask = (t_all >= t_start) & (t_all <= t_end)
            t_win = t_all[mask]
            I_win = I_all[mask]
            pts = np.column_stack((t_win, I_win))
            curve = VMobject()
            curve.set_points_as_corners([left_axes.c2p(x, y) for x, y in pts])
            curve.set_stroke(BLUE, width=2.5)

            # zoom indicator for overview
            win_center = (t_start + t_end) / 2.0
            win_width = t_end - t_start
            overview_rect = Rectangle(
                width=overview_axes.c2p(t_start + win_width, 0)[0] - overview_axes.c2p(t_start, 0)[0],
                height=overview_axes.c2p(0, 0.008)[1] - overview_axes.c2p(0, 0)[1],
                stroke_color=RED,
                stroke_width=2,
                fill_color=RED,
                fill_opacity=0.15,
            )
            overview_rect.move_to(overview_axes.c2p(win_center, 0.004))

            # fade in window
            self.play(
                Create(left_axes), Create(curve),
                FadeIn(overview_rect),
                run_time=0.8
            )

            # process each interval in window
            for iv in window:
                p1i = iv["p1_idx"]
                p2i = iv["p2_idx"]
                s0i = iv["s0_idx"]
                s0 = iv["s0"]
                tau = iv["tau"]
                t1 = float(t_all[p1i])
                t2 = float(t_all[p2i])
                h1 = float(I_all[p1i])
                h2 = float(I_all[p2i])

                # update year counter
                new_year = Tex(f"Year: {t1:.1f}", font_size=20)
                new_year.to_edge(UL, buff=0.3)
                new_year.shift(RIGHT * 0.2)
                self.play(Transform(year_text, new_year), run_time=0.1)

                # peak dots
                p1_dot = Dot(left_axes.c2p(t1, h1), color=BLUE, radius=0.08)
                p2_dot = Dot(left_axes.c2p(t2, h2), color=BLUE, radius=0.08)

                # tau arrow
                y_arrow = 0.60 * max(h1, h2)
                arr_start = left_axes.c2p(t1, y_arrow)
                arr_end = left_axes.c2p(t2, y_arrow)
                arrow = DoubleArrow(arr_start, arr_end, buff=0.0, color=YELLOW, stroke_width=3.0)
                tau_label = Tex(f"$\\tau = {tau:.2f}$", font_size=26, color=YELLOW)
                tau_label.move_to((arr_start + arr_end) / 2 + UP * 0.30)

                # S0 label — fixed bottom-left of left panel, large & legible
                s0_label = Tex(f"$S_0 = {s0:.4f}$", font_size=28, color=GREEN)
                s0_label.move_to(left_axes.get_corner(DL) + RIGHT * 1.0 + UP * 0.35)

                # scatter target
                scatter_dot = Dot(right_axes.c2p(s0, tau), color=YELLOW, radius=0.08)

                # animate interval
                self.play(FadeIn(p1_dot), FadeIn(p2_dot), run_time=0.15)
                self.play(GrowFromCenter(arrow), Write(tau_label), run_time=0.25)
                self.play(Write(s0_label), run_time=0.15)
                self.play(TransformFromCopy(p1_dot, scatter_dot), run_time=0.35)
                right_dots_group.add(scatter_dot)
                self.wait(0.15)

                # fade out interval-specific elements (keep curve and axes)
                self.play(
                    FadeOut(p1_dot), FadeOut(p2_dot),
                    FadeOut(arrow), FadeOut(tau_label),
                    FadeOut(s0_label),
                    run_time=0.12
                )

            # fade out window before next
            self.play(
                FadeOut(left_axes), FadeOut(curve),
                FadeOut(overview_rect),
                run_time=0.3
            )

        # ── final hold ──
        self.wait(3.0)

        # ── outro ──
        fade_mobs = VGroup(*[m for m in self.mobjects if isinstance(m, VMobject)])
        self.play(FadeOut(fade_mobs), run_time=1.0)
        self.wait(0.5)

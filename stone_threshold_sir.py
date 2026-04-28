from manim import *

config.background_color = BLACK

class StoneThresholdSIR(Scene):
    def construct(self):
        # ===== START FROM FINAL STATE OF keeling_switching_attractors.py =====

        title = Text("SIR Model", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)

        equations = MathTex(
            r"\frac{dS}{dt} &= B - \beta(t) SI \\",
            r"\frac{dI}{dt} &= \beta(t) SI - \gamma I \\",
            r"\frac{dR}{dt} &= \gamma I - B",
            color=WHITE,
            font_size=40
        )
        equations.to_edge(LEFT, buff=0.7)
        equations.shift(UP * 0.3)

        forcing_eq = MathTex(
            r"\beta(t) = \beta_0 \, (1 + \beta_1)^{\text{Term}(t)}",
            color=YELLOW,
            font_size=32
        )
        forcing_eq.next_to(equations.get_bottom(), DOWN, buff=0.6)
        forcing_eq.align_to(equations, LEFT)

        term_label = Text(
            "Term(t) = +1 (school terms),  −1 (holidays)",
            font_size=20,
            color=GRAY
        )
        term_label.next_to(forcing_eq, DOWN, buff=0.15)
        term_label.align_to(forcing_eq, LEFT)

        sinks_title = Text("Two spiral sinks:", font_size=24, color=WHITE)
        sinks_title.next_to(term_label, DOWN, buff=0.3)
        sinks_title.align_to(forcing_eq, LEFT)

        sink_term = MathTex(
            r"\text{Term: } \beta^+ = \beta_0(1+\beta_1)",
            color=BLUE,
            font_size=24
        )
        sink_term.next_to(sinks_title, DOWN, buff=0.15)
        sink_term.align_to(sinks_title, LEFT)

        sink_hol = MathTex(
            r"\text{Holiday: } \beta^- = \beta_0/(1+\beta_1)",
            color=RED,
            font_size=24
        )
        sink_hol.next_to(sink_term, DOWN, buff=0.15)
        sink_hol.align_to(sink_term, LEFT)

        axes = Axes(
            x_range=[0, 4*PI, PI],
            y_range=[-1.5, 1.5, 1],
            x_length=3,
            y_length=1.2,
            axis_config={"color": GRAY, "stroke_width": 1},
            tips=False,
        )
        square_wave = axes.plot(
            lambda x: 0.8 if (x % (2*PI)) < PI else -0.8,
            color=YELLOW,
            stroke_width=2,
            discontinuities=[PI, 3*PI],
            dt=0.01,
        )
        wave_group = VGroup(axes, square_wave)
        wave_group.next_to(forcing_eq, RIGHT, buff=0.5)
        wave_group.scale(0.8)

        params_title = Text("Parameters", font_size=36, color=WHITE)
        params_title.to_edge(RIGHT, buff=0.8)
        params_title.align_to(equations, UP)
        params_title.shift(UP * 0.3)

        params = VGroup(
            MathTex(r"B", r"\text{ — birth / death rate}", color=WHITE, font_size=28),
            MathTex(r"\beta_0", r"\text{ — mean contact rate}", color=WHITE, font_size=28),
            MathTex(r"\beta_1", r"\text{ — seasonality strength}", color=WHITE, font_size=28),
            MathTex(r"\gamma", r"\text{ — recovery rate}", color=WHITE, font_size=28),
            MathTex(r"R_0 = \beta_0/\gamma", r"\text{ — basic reproduction ratio}", color=WHITE, font_size=28),
            MathTex(r"S + I + R = 1", r"\text{ — normalized population}", color=WHITE, font_size=28),
        )
        params.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        params.next_to(params_title, DOWN, buff=0.3)
        params.to_edge(RIGHT, buff=0.8)

        params[0][0].set_color(BLUE)
        params[1][0].set_color(YELLOW)
        params[2][0].set_color(YELLOW)
        params[3][0].set_color(GREEN)
        params[4][0].set_color(GREEN)
        params[5][0].set_color(WHITE)

        self.camera.frame_width *= 1.25
        self.camera.frame_height *= 1.25
        self.camera.max_allowable_norm = self.camera.frame_width
        self.add(title, equations, forcing_eq, term_label, sinks_title,
                 sink_term, sink_hol, wave_group, params_title, params)
        self.wait(0.5)

        # ===== TRANSITION TO STONE ET AL. (2007) SEASONALLY FORCED SIR =====

        # 1. Highlight the Keeling binary forcing, then fade out spiral-sink concepts
        self.play(
            Indicate(forcing_eq, color=YELLOW, scale_factor=1.1),
            Indicate(wave_group, color=YELLOW, scale_factor=1.1),
            run_time=1.0
        )
        self.wait(0.2)

        self.play(
            FadeOut(sinks_title),
            FadeOut(sink_term),
            FadeOut(sink_hol),
            FadeOut(term_label),
            run_time=0.6
        )
        self.wait(0.2)

        # 2. Morph square wave back into a sine wave (annual sinusoidal forcing)
        sine_wave = axes.plot(
            lambda x: 0.8 * np.sin(x),
            color=YELLOW,
            stroke_width=2
        )
        self.play(Transform(square_wave, sine_wave), run_time=1.5)
        self.wait(0.2)

        # 3. Replace forcing equation with Stone et al. sinusoidal form
        stone_forcing = MathTex(
            r"\beta(t) = \beta_0 \bigl[1 + \delta \sin(2\pi t)\bigr]",
            color=YELLOW,
            font_size=32
        )
        stone_forcing.move_to(forcing_eq)
        stone_forcing.align_to(forcing_eq, LEFT)

        self.play(Transform(forcing_eq, stone_forcing), run_time=1.5)
        self.wait(0.2)

        # 4. Add the two-season approximation below
        two_season = MathTex(
            r"\text{Two-season approx.: } \beta_1 = \beta_0(1+\delta),\; \beta_2 = \beta_0(1-\delta)",
            color=GRAY,
            font_size=20
        )
        two_season.next_to(stone_forcing, DOWN, buff=0.2)
        two_season.align_to(stone_forcing, LEFT)
        self.play(Write(two_season), run_time=1.0)
        self.wait(0.3)

        # 5. Transform equations to Stone et al. form with vital dynamics in all compartments
        stone_equations = MathTex(
            r"\dot{S} &= \mu - \mu S - \beta(t) S(I+\varepsilon) \\",
            r"\dot{I} &= \beta(t) S(I+\varepsilon) - \gamma I - \mu I \\",
            r"\dot{R} &= \gamma I - \mu R",
            color=WHITE,
            font_size=40
        )
        stone_equations.move_to(equations)

        self.play(Transform(equations, stone_equations), run_time=2.0)
        self.wait(0.3)

        # 6. Introduce the epidemic vs. skip threshold below the equations
        threshold_title = Text("Epidemic threshold:", font_size=22, color=WHITE)
        threshold_title.next_to(two_season, DOWN, buff=0.35)
        threshold_title.align_to(two_season, LEFT)

        threshold_eq = MathTex(
            r"S_0 > S_c \approx \frac{\gamma + \mu}{\beta_0} - \frac{\mu}{2}",
            color=GREEN,
            font_size=26
        )
        threshold_eq.next_to(threshold_title, DOWN, buff=0.15)
        threshold_eq.align_to(threshold_title, LEFT)

        threshold_explain = Text(
            "S₀ > S_c  →  epidemic next year    |    S₀ < S_c  →  skip",
            font_size=18,
            color=GRAY
        )
        threshold_explain.next_to(threshold_eq, DOWN, buff=0.15)
        threshold_explain.align_to(threshold_eq, LEFT)

        self.play(Write(threshold_title), run_time=0.8)
        self.play(Write(threshold_eq), run_time=1.0)
        self.play(Write(threshold_explain), run_time=1.0)
        self.wait(0.3)

        # 7. Update parameters panel
        self.play(FadeOut(params), FadeOut(params_title), run_time=0.5)

        new_params_title = Text("Parameters", font_size=36, color=WHITE)
        new_params_title.to_edge(RIGHT, buff=0.8)
        new_params_title.align_to(equations, UP)
        new_params_title.shift(UP * 0.3)

        new_params = VGroup(
            MathTex(r"\mu", r"\text{ — birth / mortality rate}", color=WHITE, font_size=28),
            MathTex(r"\beta_0", r"\text{ — mean contact rate}", color=WHITE, font_size=28),
            MathTex(r"\delta", r"\text{ — seasonality strength}", color=WHITE, font_size=28),
            MathTex(r"\gamma", r"\text{ — recovery rate}", color=WHITE, font_size=28),
            MathTex(r"\varepsilon = 10^{-12}", r"\text{ — immigration}", color=WHITE, font_size=28),
            MathTex(r"R_0 = \beta_0/\gamma", r"\text{ — reproduction ratio}", color=WHITE, font_size=28),
        )
        new_params.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        new_params.next_to(new_params_title, DOWN, buff=0.3)
        new_params.to_edge(RIGHT, buff=0.8)

        new_params[0][0].set_color(BLUE)
        new_params[1][0].set_color(YELLOW)
        new_params[2][0].set_color(YELLOW)
        new_params[3][0].set_color(GREEN)
        new_params[4][0].set_color(GRAY)
        new_params[5][0].set_color(GREEN)

        self.play(Write(new_params_title), run_time=0.8)
        self.play(Write(new_params), run_time=2.0)
        self.wait(0.3)

        # 8. Final highlight: threshold equation and the sinusoidal forcing
        self.play(
            Circumscribe(threshold_eq, color=GREEN, fade_out=True, run_time=1.5),
        )
        self.wait(0.3)
        self.play(
            Indicate(stone_forcing, color=YELLOW, scale_factor=1.15),
            Indicate(wave_group, color=YELLOW, scale_factor=1.15),
            run_time=1.2
        )
        self.wait(2)

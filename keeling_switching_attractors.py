from manim import *

config.background_color = BLACK

class KeelingSwitchingAttractors(Scene):
    def construct(self):
        # ===== START FROM FINAL STATE OF seasonal_forcing_transition.py =====

        title = Text("SIR Model", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)

        equations = MathTex(
            r"\frac{dS}{dt} &= -\beta(t) SI \\",
            r"\frac{dI}{dt} &= \beta(t) SI - \gamma I \\",
            r"\frac{dR}{dt} &= \gamma I",
            color=WHITE,
            font_size=40
        )
        equations.to_edge(LEFT, buff=0.7)
        equations.shift(UP * 0.3)

        arrow = Arrow(
            equations.get_bottom() + DOWN * 0.15,
            equations.get_bottom() + DOWN * 1.0,
            color=YELLOW,
            buff=0.1
        )
        transition_label = MathTex(r"\beta \rightarrow \beta(t)", color=YELLOW, font_size=32)
        transition_label.next_to(arrow, RIGHT, buff=0.3)

        forcing_eq = MathTex(
            r"\beta(t) = \beta_0 + \beta_1 \cos(\omega t)",
            color=YELLOW,
            font_size=34
        )
        forcing_eq.next_to(arrow, DOWN, buff=0.25)
        forcing_eq.align_to(equations, LEFT)

        axes = Axes(
            x_range=[0, 4*PI, PI],
            y_range=[-1.5, 1.5, 1],
            x_length=3,
            y_length=1.2,
            axis_config={"color": GRAY, "stroke_width": 1},
            tips=False,
        )
        cosine_curve = axes.plot(
            lambda x: 0.8 * np.cos(x),
            color=YELLOW,
            stroke_width=2
        )
        cosine_group = VGroup(axes, cosine_curve)
        cosine_group.next_to(forcing_eq, RIGHT, buff=0.5)
        cosine_group.scale(0.8)

        params_title = Text("Parameters", font_size=36, color=WHITE)
        params_title.to_edge(RIGHT, buff=1.0)
        params_title.align_to(equations, UP)
        params_title.shift(UP * 0.5)

        params = VGroup(
            MathTex(r"\beta_0", r"\text{ — mean contact rate}", color=WHITE, font_size=30),
            MathTex(r"\beta_1", r"\text{ — seasonal amplitude}", color=WHITE, font_size=30),
            MathTex(r"\omega", r"\text{ — angular frequency}", color=WHITE, font_size=30),
            MathTex(r"\gamma", r"\text{ — recovery rate}", color=WHITE, font_size=30),
            MathTex(r"S(t), I(t), R(t)", r"\text{ — compartment sizes}", color=WHITE, font_size=30),
            MathTex(r"N = S + I + R", r"\text{ — total population}", color=WHITE, font_size=30),
        )
        params.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        params.next_to(params_title, DOWN, buff=0.3)
        params.to_edge(RIGHT, buff=1.0)

        params[0][0].set_color(YELLOW)
        params[1][0].set_color(YELLOW)
        params[2][0].set_color(YELLOW)
        params[3][0].set_color(GREEN)
        params[4][0].set_color(WHITE)
        params[5][0].set_color(WHITE)

        self.camera.frame_width *= 1.25
        self.camera.frame_height *= 1.25
        self.camera.max_allowable_norm = self.camera.frame_width
        self.add(title, equations, arrow, transition_label, forcing_eq, cosine_group, params_title, params)
        self.wait(0.5)

        # ===== TRANSITION TO KEELING ET AL. SWITCHING MODEL =====

        # Highlight the continuous forcing
        self.play(
            Indicate(forcing_eq, color=YELLOW, scale_factor=1.1),
            Indicate(cosine_group, color=YELLOW, scale_factor=1.1),
            run_time=1.2
        )
        self.wait(0.3)

        # Fade out the old arrow and transition label
        self.play(FadeOut(arrow), FadeOut(transition_label), run_time=0.5)

        # Replace cosine with square wave showing binary forcing
        square_wave = axes.plot(
            lambda x: 0.8 if (x % (2*PI)) < PI else -0.8,
            color=YELLOW,
            stroke_width=2,
            discontinuities=[PI, 3*PI],
            dt=0.01,
        )

        self.play(
            Transform(cosine_curve, square_wave),
            run_time=1.5
        )
        self.wait(0.3)

        # Replace forcing equation with Keeling binary forcing
        new_forcing = MathTex(
            r"\beta(t) = \beta_0 \, (1 + \beta_1)^{\text{Term}(t)}",
            color=YELLOW,
            font_size=32
        )
        new_forcing.move_to(forcing_eq)
        new_forcing.align_to(forcing_eq, LEFT)

        term_label = Text(
            "Term(t) = +1 (school terms),  −1 (holidays)",
            font_size=20,
            color=GRAY
        )
        term_label.next_to(new_forcing, DOWN, buff=0.15)
        term_label.align_to(new_forcing, LEFT)

        self.play(Transform(forcing_eq, new_forcing), run_time=1.5)
        self.play(Write(term_label), run_time=1)
        self.wait(0.3)

        # Add the "two spiral sinks" concept below
        sinks_title = Text("Two spiral sinks:", font_size=24, color=WHITE)
        sinks_title.next_to(term_label, DOWN, buff=0.3)
        sinks_title.align_to(new_forcing, LEFT)

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

        self.play(Write(sinks_title), run_time=0.8)
        self.play(Write(sink_term), run_time=0.8)
        self.play(Write(sink_hol), run_time=0.8)
        self.wait(0.5)

        # Transform equations to Keeling form with demography
        keeling_equations = MathTex(
            r"\frac{dS}{dt} &= B - \beta(t) SI \\",
            r"\frac{dI}{dt} &= \beta(t) SI - \gamma I \\",
            r"\frac{dR}{dt} &= \gamma I - B",
            color=WHITE,
            font_size=40
        )
        keeling_equations.move_to(equations)

        self.play(Transform(equations, keeling_equations), run_time=2)
        self.wait(0.3)

        # Update parameters panel
        self.play(FadeOut(params), FadeOut(params_title), run_time=0.5)

        new_params_title = Text("Parameters", font_size=36, color=WHITE)
        new_params_title.to_edge(RIGHT, buff=0.8)
        new_params_title.align_to(equations, UP)
        new_params_title.shift(UP * 0.3)

        new_params = VGroup(
            MathTex(r"B", r"\text{ — birth / death rate}", color=WHITE, font_size=28),
            MathTex(r"\beta_0", r"\text{ — mean contact rate}", color=WHITE, font_size=28),
            MathTex(r"\beta_1", r"\text{ — seasonality strength}", color=WHITE, font_size=28),
            MathTex(r"\gamma", r"\text{ — recovery rate}", color=WHITE, font_size=28),
            MathTex(r"R_0 = \beta_0/\gamma", r"\text{ — basic reproduction ratio}", color=WHITE, font_size=28),
            MathTex(r"S + I + R = 1", r"\text{ — normalized population}", color=WHITE, font_size=28),
        )
        new_params.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        new_params.next_to(new_params_title, DOWN, buff=0.3)
        new_params.to_edge(RIGHT, buff=0.8)

        new_params[0][0].set_color(BLUE)
        new_params[1][0].set_color(YELLOW)
        new_params[2][0].set_color(YELLOW)
        new_params[3][0].set_color(GREEN)
        new_params[4][0].set_color(GREEN)
        new_params[5][0].set_color(WHITE)

        self.play(Write(new_params_title), run_time=0.8)
        self.play(Write(new_params), run_time=2)
        self.wait(0.5)

        # Final highlight: show switching concept
        self.play(
            Circumscribe(sink_term, color=BLUE, fade_out=True, run_time=1.2),
            Circumscribe(sink_hol, color=RED, fade_out=True, run_time=1.2),
        )
        self.wait(2)

from manim import *

config.background_color = BLACK

class SeasonalForcingTransition(Scene):
    def construct(self):
        # ===== START FROM FINAL STATE OF PREVIOUS ANIMATION =====
        
        # Title
        title = Text("SIR Model", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)
        
        # SIR Equations (left side)
        equations = MathTex(
            r"\frac{dS}{dt} &= -\beta SI \\",
            r"\frac{dI}{dt} &= \beta SI - \gamma I \\",
            r"\frac{dR}{dt} &= \gamma I",
            color=WHITE,
            font_size=40
        )
        equations.to_edge(LEFT, buff=1.0)
        equations.shift(DOWN * 0.3)

        # Color-coded labels
        eq_labels = VGroup(
            Text("Susceptible", font_size=28, color=BLUE).next_to(equations[0], RIGHT, buff=0.5),
            Text("Infected", font_size=28, color=RED).next_to(equations[1], RIGHT, buff=0.5),
            Text("Recovered", font_size=28, color=GREEN).next_to(equations[2], RIGHT, buff=0.5),
        )

        # Parameters panel (right side)
        params_title = Text("Parameters", font_size=36, color=WHITE)
        params_title.to_edge(RIGHT, buff=1.2)
        params_title.align_to(equations, UP)

        params = VGroup(
            MathTex(r"\beta", r"\text{ — infection rate}", color=WHITE, font_size=32),
            MathTex(r"\gamma", r"\text{ — recovery rate}", color=WHITE, font_size=32),
            MathTex(r"S(t)", r"\text{ — susceptible individuals}", color=WHITE, font_size=32),
            MathTex(r"I(t)", r"\text{ — infected individuals}", color=WHITE, font_size=32),
            MathTex(r"R(t)", r"\text{ — recovered individuals}", color=WHITE, font_size=32),
            MathTex(r"N = S + I + R", r"\text{ — total population}", color=WHITE, font_size=32),
        )
        params.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        params.next_to(params_title, DOWN, buff=0.4)
        params.to_edge(RIGHT, buff=1.0)

        # Color the parameter symbols
        params[0][0].set_color(YELLOW)
        params[1][0].set_color(YELLOW)
        params[2][0].set_color(BLUE)
        params[3][0].set_color(RED)
        params[4][0].set_color(GREEN)
        params[5][0].set_color(WHITE)

        # Add everything instantly to simulate "final state of last animation"
        self.camera.frame_width *= 1.25
        self.camera.frame_height *= 1.25
        self.camera.max_allowable_norm = self.camera.frame_width
        self.add(title, equations, eq_labels, params_title, params)
        self.wait(0.5)

        # ===== TRANSITION TO SEASONAL FORCING =====

        # Highlight β in both equations
        beta_s = equations[0][7]   # β in dS/dt
        beta_i = equations[1][6]   # β in dI/dt
        
        self.play(
            Indicate(beta_s, color=YELLOW, scale_factor=1.5),
            Indicate(beta_i, color=YELLOW, scale_factor=1.5),
            run_time=1.2
        )
        self.wait(0.3)

        # Fade out the old parameter panel and labels to make room
        self.play(
            FadeOut(params_title),
            FadeOut(params),
            FadeOut(eq_labels),
            run_time=0.8
        )
        self.wait(0.2)

        # Transition arrow
        arrow = Arrow(
            equations.get_bottom() + DOWN * 0.15,
            equations.get_bottom() + DOWN * 1.0,
            color=YELLOW,
            buff=0.1
        )
        transition_label = MathTex(r"\beta \rightarrow \beta(t)", color=YELLOW, font_size=32)
        transition_label.next_to(arrow, RIGHT, buff=0.3)
        
        self.play(GrowArrow(arrow), Write(transition_label), run_time=1)
        self.wait(0.3)

        # Seasonal forcing equation
        forcing_eq = MathTex(
            r"\beta(t) = \beta_0 + \beta_1 \cos(\omega t)",
            color=YELLOW,
            font_size=34
        )
        forcing_eq.next_to(arrow, DOWN, buff=0.25)
        forcing_eq.align_to(equations, LEFT)

        # Small cosine wave
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

        self.play(Write(forcing_eq), run_time=1.5)
        self.play(Create(axes), Create(cosine_curve), run_time=1.5)
        
        # Animated dot on cosine
        dot = Dot(color=YELLOW, radius=0.06)
        dot.move_to(axes.c2p(0, 0.8))
        self.play(FadeIn(dot), run_time=0.3)
        self.play(
            MoveAlongPath(dot, cosine_curve),
            rate_func=linear,
            run_time=2
        )
        self.play(FadeOut(dot), run_time=0.3)
        self.wait(0.3)

        # Transform equations to forced version
        forced_equations = MathTex(
            r"\frac{dS}{dt} &= -\beta(t) SI \\",
            r"\frac{dI}{dt} &= \beta(t) SI - \gamma I \\",
            r"\frac{dR}{dt} &= \gamma I",
            color=WHITE,
            font_size=40
        )
        forced_equations.move_to(equations)

        self.play(Transform(equations, forced_equations), run_time=2)
        self.wait(0.3)

        # New parameters panel
        new_params_title = Text("Parameters", font_size=36, color=WHITE)
        new_params_title.to_edge(RIGHT, buff=1.0)
        new_params_title.align_to(equations, UP)
        new_params_title.shift(UP * 0.5)

        new_params = VGroup(
            MathTex(r"\beta_0", r"\text{ — mean contact rate}", color=WHITE, font_size=30),
            MathTex(r"\beta_1", r"\text{ — seasonal amplitude}", color=WHITE, font_size=30),
            MathTex(r"\omega", r"\text{ — angular frequency}", color=WHITE, font_size=30),
            MathTex(r"\gamma", r"\text{ — recovery rate}", color=WHITE, font_size=30),
            MathTex(r"S(t), I(t), R(t)", r"\text{ — compartment sizes}", color=WHITE, font_size=30),
            MathTex(r"N = S + I + R", r"\text{ — total population}", color=WHITE, font_size=30),
        )
        new_params.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        new_params.next_to(new_params_title, DOWN, buff=0.3)
        new_params.to_edge(RIGHT, buff=1.0)

        new_params[0][0].set_color(YELLOW)
        new_params[1][0].set_color(YELLOW)
        new_params[2][0].set_color(YELLOW)
        new_params[3][0].set_color(GREEN)
        new_params[4][0].set_color(WHITE)
        new_params[5][0].set_color(WHITE)

        self.play(Write(new_params_title), run_time=0.8)
        self.play(Write(new_params), run_time=2)
        self.wait(0.5)

        # Final highlight linking forcing to equations
        self.play(
            Circumscribe(forcing_eq, color=YELLOW, fade_out=True, run_time=1.5),
            Circumscribe(equations, color=YELLOW, fade_out=True, run_time=1.5),
        )
        self.wait(2)

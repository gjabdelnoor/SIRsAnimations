from manim import *

config.background_color = BLACK

class SIREquations(Scene):
    def construct(self):
        # Title
        title = Text("SIR Model", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=1.5)
        self.wait(0.3)

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

        # Color-coded braces/labels for each equation
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

        # Widen viewport to 125%
        self.camera.frame_width *= 1.25
        self.camera.frame_height *= 1.25
        self.camera.max_allowable_norm = self.camera.frame_width

        # Animate equations
        self.play(Write(equations), run_time=2.5)
        self.wait(0.2)
        self.play(FadeIn(eq_labels, shift=RIGHT), run_time=1)
        self.wait(0.3)

        # Animate parameters
        self.play(Write(params_title), run_time=1)
        self.wait(0.2)
        self.play(Write(params), run_time=2.5)
        self.wait(0.5)

        # Subtle final highlight
        self.play(
            Indicate(equations, color=WHITE, scale_factor=1.02),
            run_time=1.5
        )
        self.wait(2)

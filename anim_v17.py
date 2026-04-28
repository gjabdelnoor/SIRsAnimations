from manim import *
import numpy as np
from scipy.integrate import solve_ivp

config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 60
config.background_color = BLACK

C_AXES = WHITE
C_TEXT = WHITE
C_TRAJ = BLUE_D
C_TRAJ2 = GREEN_C
C_THRESH = RED
C_S0 = RED
C_NN_HIDDEN = PURPLE
C_NN_NODE = PURPLE_A
C_OUTBREAK = RED_C
C_SKIP = BLUE_C


class WhyForcedSIR(Scene):
    def construct(self):
        self.play_ode_section()
        self.play_nn_section()
        self.play_final_message()

    def play_ode_section(self):
        title = Tex(r"\textbf{Forced SIR}", font_size=40, color=C_TEXT)
        title.to_edge(UP, buff=0.6)

        eqs = MathTex(
            r"S' &= \mu - \mu S - \beta(t) S (I+\varepsilon)",
            r"I' &= \beta(t) S (I+\varepsilon) - (\gamma+\mu) I",
            r"\beta(t) &= \beta_0 \bigl(1 + \delta \sin(2\pi t)\bigr)",
            font_size=32, color=C_TEXT
        )
        eqs.next_to(title, DOWN, buff=0.5)

        self.play(Write(title), run_time=0.8)
        self.play(Write(eqs), run_time=1.5)
        self.wait(0.5)

        # Fade equations, keep title
        self.play(FadeOut(eqs), run_time=0.5)
        self.play(title.animate.scale(0.7).to_edge(UL, buff=0.4), run_time=0.6)

        # Compute trajectories
        mu, gamma = 0.02, 66.0
        beta0, delta = 1600.0, 0.18
        epsilon = 1e-12

        def beta(t):
            return beta0 * (1.0 + delta * np.sin(2 * np.pi * t))

        def rhs(t, y):
            S, I = y
            b = beta(t)
            dS = mu - mu * S - b * S * (I + epsilon)
            dI = b * S * (I + epsilon) - (gamma + mu) * I
            return [dS, dI]

        # Main trajectory (S_0 > S_c, limit cycle)
        t_eval = np.linspace(20, 60, 3000)
        sol = solve_ivp(rhs, (0, 60), [0.03, 0.0001],
                        t_eval=t_eval, method='DOP853', rtol=1e-9, atol=1e-12)
        S_t, I_t = sol.y[0], sol.y[1]
        logI_t = np.log10(I_t + 1e-12)

        # Skip trajectory (S_0 < S_c, dies out)
        sol_skip = solve_ivp(rhs, (0, 60), [0.018, 0.0001],
                             t_eval=t_eval, method='DOP853', rtol=1e-9, atol=1e-12)
        S_skip, I_skip = sol_skip.y[0], sol_skip.y[1]
        logI_skip = np.log10(I_skip + 1e-12)

        pp_axes = Axes(
            x_range=[0, 0.055, 0.01],
            y_range=[-4.5, -1.5, 0.5],
            x_length=12, y_length=6.5,
            axis_config={"color": C_AXES, "include_tip": False, "stroke_width": 1.2},
            tips=False,
        )
        pp_axes.to_edge(DOWN, buff=0.6)
        pp_axes.x_axis.add_numbers(font_size=22, num_decimal_places=2)
        pp_axes.y_axis.add_numbers(font_size=22, num_decimal_places=1)

        x_label = Tex(r"$S$", font_size=30, color=C_TEXT)
        x_label.next_to(pp_axes, DOWN, buff=0.15)
        y_label = Tex(r"$\log_{10} I$", font_size=30, color=C_TEXT)
        y_label.next_to(pp_axes, LEFT, buff=0.15)

        pts = [pp_axes.c2p(s, li) for s, li in zip(S_t, logI_t)]
        trajectory = VMobject()
        trajectory.set_points_as_corners(pts)
        trajectory.set_stroke(C_TRAJ, width=2.5)

        pts_skip = [pp_axes.c2p(s, li) for s, li in zip(S_skip, logI_skip)]
        traj_skip = VMobject()
        traj_skip.set_points_as_corners(pts_skip)
        traj_skip.set_stroke(C_TRAJ2, width=2.5)
        traj_skip.set_opacity(0.7)

        self.play(
            Create(pp_axes), Write(x_label), Write(y_label),
            run_time=1.0
        )
        self.play(Create(trajectory), run_time=4.5)

        # Threshold and rules
        sc = (gamma + mu) / beta0 - mu / 2.0
        sc_line = DashedLine(
            pp_axes.c2p(sc, -4.5), pp_axes.c2p(sc, -1.5),
            color=C_THRESH, dash_length=0.08, stroke_width=2.5
        )
        sc_label = Tex(r"$S_c$", font_size=28, color=C_THRESH)
        sc_label.next_to(sc_line, UP, buff=0.15)

        s0_idx = np.argmin(np.abs(S_t - 0.022))
        s0_dot = Dot(pp_axes.c2p(S_t[s0_idx], logI_t[s0_idx]),
                     color=C_S0, radius=0.09)
        s0_label = Tex(r"$S_0$", font_size=26, color=C_S0)
        s0_label.next_to(s0_dot, DOWN, buff=0.15)

        self.play(
            Create(sc_line), Write(sc_label),
            FadeIn(s0_dot), Write(s0_label),
            run_time=0.8
        )

        # Show skip trajectory to demonstrate rule
        rule_skip = Tex(r"$S_0 < S_c \;\rightarrow\;$ skip", font_size=26, color=GRAY_B)
        rule_outbreak = Tex(r"$S_0 > S_c \;\rightarrow\;$ outbreak", font_size=26, color=C_THRESH)
        rules = VGroup(rule_skip, rule_outbreak).arrange(DOWN, buff=0.3)
        rules.to_edge(UR, buff=1.0)

        self.play(Write(rule_outbreak), run_time=0.5)
        self.play(Create(traj_skip), Write(rule_skip), run_time=2.5)

        geo_text = Tex(r"\textbf{The model has a geometry.}", font_size=32, color=C_TEXT)
        geo_text.to_edge(UP, buff=0.3)

        self.play(Write(geo_text), run_time=0.6)
        self.wait(1.5)

        self.ode_group = VGroup(
            title, pp_axes, trajectory, traj_skip, sc_line, sc_label,
            s0_dot, s0_label, rules, geo_text, x_label, y_label
        )
        self.play(FadeOut(self.ode_group), run_time=1.0)

    def play_nn_section(self):
        nn_title = Tex(r"\textbf{Neural Network (SFNN)}", font_size=38, color=C_TEXT)
        nn_title.to_edge(UP, buff=0.6)
        subtitle = Tex(r"Madden et al. 2024", font_size=24, color=GRAY_B)
        subtitle.next_to(nn_title, DOWN, buff=0.2)

        self.play(Write(nn_title), Write(subtitle), run_time=0.8)

        # Architecture: 7 inputs matching the paper
        layer_dims = [7, 8, 10, 8, 1]
        layer_x = np.linspace(-3.5, 3.5, len(layer_dims))
        node_r = 0.10
        all_nodes = VGroup()
        all_edges = VGroup()
        layer_nodes_list = []

        for li, (n, x) in enumerate(zip(layer_dims, layer_x)):
            y_positions = np.linspace(-(n - 1) * 0.30, (n - 1) * 0.30, n)
            layer = []
            for y in y_positions:
                node = Circle(radius=node_r, color=C_NN_NODE,
                              fill_opacity=0.3, stroke_width=1.5)
                node.move_to([x, y, 0])
                layer.append(node)
                all_nodes.add(node)
            layer_nodes_list.append(layer)

        for li in range(len(layer_nodes_list) - 1):
            for n1 in layer_nodes_list[li]:
                for n2 in layer_nodes_list[li + 1]:
                    edge = Line(n1.get_center(), n2.get_center(),
                               stroke_width=0.5, color=C_NN_HIDDEN,
                               stroke_opacity=0.2)
                    all_edges.add(edge)

        arch_group = VGroup(all_edges, all_nodes)
        arch_group.move_to(ORIGIN + DOWN * 0.3)

        # Input feature labels matching the paper
        feat_labels = [
            "Near City\\\\Lags", "Near City\\\\Dist", "Population",
            "Births", "Incidence\\\\Lags", "Large City\\\\Lags", "Large City\\\\Dist"
        ]
        feat_tex = VGroup()
        for lbl, node in zip(feat_labels, layer_nodes_list[0]):
            t = Tex(lbl, font_size=11, color=GRAY_C)
            t.next_to(node, LEFT, buff=0.15)
            feat_tex.add(t)

        out_label = Tex(r"Incidence\\Forecast", font_size=14, color=C_TEXT)
        out_label.next_to(layer_nodes_list[-1][0], RIGHT, buff=0.3)

        dim_text = Tex(r"max hidden dim: 1201", font_size=20, color=C_NN_HIDDEN)
        dim_text.move_to([0, -2.8, 0])

        self.play(
            FadeIn(all_edges, lag_ratio=0.005),
            FadeIn(all_nodes, lag_ratio=0.02),
            run_time=1.5
        )
        self.play(
            Write(feat_tex), Write(out_label), Write(dim_text),
            run_time=0.8
        )
        self.wait(0.4)

        # PERFORMANCE MICRO-BEAT
        perf_title = Tex(r"\textbf{SFNN outperforms TSIR}", font_size=28, color=C_TEXT)
        perf_title.move_to([0, 2.0, 0])

        # Simple bar comparison
        tsir_bar = Rectangle(width=3.0, height=0.35, color=GRAY_C, fill_opacity=0.3)
        tsir_bar.set_stroke(GRAY_C, width=1.5)
        tsir_bar.move_to([-1.0, 0.8, 0])
        sfnn_bar = Rectangle(width=2.0, height=0.35, color=C_NN_HIDDEN, fill_opacity=0.4)
        sfnn_bar.set_stroke(C_NN_HIDDEN, width=1.5)
        sfnn_bar.move_to([-1.5, 0.2, 0])

        tsir_label = Tex(r"TSIR RMSE", font_size=20, color=GRAY_C)
        tsir_label.next_to(tsir_bar, RIGHT, buff=0.3)
        sfnn_label = Tex(r"SFNN RMSE", font_size=20, color=C_NN_HIDDEN)
        sfnn_label.next_to(sfnn_bar, RIGHT, buff=0.3)

        perf_note = Tex(r"(especially for large populations, long horizons)",
                        font_size=18, color=GRAY_D)
        perf_note.move_to([0, -0.5, 0])

        perf_group = VGroup(perf_title, tsir_bar, sfnn_bar,
                           tsir_label, sfnn_label, perf_note)

        self.play(
            FadeOut(arch_group), FadeOut(feat_tex), FadeOut(out_label),
            FadeOut(dim_text),
            run_time=0.5
        )
        self.play(
            Write(perf_title),
            FadeIn(tsir_bar), FadeIn(sfnn_bar),
            Write(tsir_label), Write(sfnn_label),
            run_time=1.0
        )
        self.play(Write(perf_note), run_time=0.5)
        self.wait(1.0)

        # Transition to embedding critique
        but_text = Tex(r"\textbf{But what does it learn?}", font_size=30, color=C_TEXT)
        but_text.move_to(ORIGIN)

        self.play(
            FadeOut(perf_group),
            run_time=0.5
        )
        self.play(Write(but_text), run_time=0.8)
        self.wait(0.5)
        self.play(FadeOut(but_text), run_time=0.5)

        # HIDDEN-STATE PROJECTION
        embed_title = Tex(r"\textbf{Hidden-state projection}", font_size=28, color=C_TEXT)
        embed_title.move_to([0, 2.2, 0])

        proj_label = Tex(r"(2D projection of $h \in \mathbb{R}^{1201}$)",
                         font_size=18, color=GRAY_C)
        proj_label.next_to(embed_title, DOWN, buff=0.12)

        illust_label = Tex(r"(illustrative)", font_size=16, color=GRAY_D)
        illust_label.move_to([0, -2.6, 0])

        frame = Rectangle(width=6.5, height=4.5, color=GRAY_D, stroke_width=1.5)
        frame.move_to([0, -0.1, 0])

        # Axis labels
        pc1 = Tex(r"PC$_1$", font_size=18, color=GRAY_C)
        pc1.next_to(frame, DOWN, buff=0.1)
        pc2 = Tex(r"PC$_2$", font_size=18, color=GRAY_C)
        pc2.next_to(frame, LEFT, buff=0.1)

        # Generate embeddings
        np.random.seed(42)
        n_outbreak = 55
        n_skip = 55
        n_mixed = 25

        out_pts = np.random.multivariate_normal(
            [1.2, 0.5], [[0.2, 0.08], [0.08, 0.15]], n_outbreak)
        skip_pts = np.random.multivariate_normal(
            [-0.2, -0.4], [[0.18, -0.05], [-0.05, 0.14]], n_skip)
        mixed_pts = np.random.multivariate_normal(
            [0.6, 0.0], [[0.1, 0.02], [0.02, 0.08]], n_mixed)

        scale = 1.6
        center = np.array([0, -0.1, 0])

        outbreak_dots = VGroup()
        for p in out_pts:
            pos = center + scale * np.array([p[0], p[1], 0])
            d = Dot(pos, color=C_OUTBREAK, radius=0.05)
            d.set_opacity(0.85)
            outbreak_dots.add(d)

        skip_dots = VGroup()
        for p in skip_pts:
            pos = center + scale * np.array([p[0], p[1], 0])
            d = Dot(pos, color=C_SKIP, radius=0.05)
            d.set_opacity(0.85)
            skip_dots.add(d)

        mixed_dots = VGroup()
        for p in mixed_pts:
            pos = center + scale * np.array([p[0], p[1], 0])
            d = Dot(pos, color=GRAY_C, radius=0.04)
            d.set_opacity(0.65)
            mixed_dots.add(d)

        # Legend
        leg_out = Dot(color=C_OUTBREAK, radius=0.07)
        leg_out_label = Tex(r"outbreak", font_size=18, color=C_OUTBREAK)
        leg_out_label.next_to(leg_out, RIGHT, buff=0.15)
        leg_skip = Dot(color=C_SKIP, radius=0.07)
        leg_skip_label = Tex(r"skip", font_size=18, color=C_SKIP)
        leg_skip_label.next_to(leg_skip, RIGHT, buff=0.15)
        legend = VGroup(
            VGroup(leg_out, leg_out_label).arrange(RIGHT, buff=0.1),
            VGroup(leg_skip, leg_skip_label).arrange(RIGHT, buff=0.1)
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        legend.to_edge(RIGHT, buff=0.7)
        legend.shift(UP * 1.5)

        self.play(
            Write(embed_title), Write(proj_label),
            Create(frame), Write(pc1), Write(pc2),
            run_time=0.8
        )
        self.play(
            FadeIn(outbreak_dots, lag_ratio=0.02),
            FadeIn(skip_dots, lag_ratio=0.02),
            FadeIn(mixed_dots, lag_ratio=0.02),
            run_time=1.5
        )
        self.play(Write(legend), Write(illust_label), run_time=0.5)
        self.wait(0.3)

        # Wiggly boundary
        boundary_x = np.linspace(-0.8, 2.2, 100)
        boundary_y = (0.35 * np.sin(3.5 * np.pi * boundary_x) +
                      0.18 * np.cos(5.5 * np.pi * boundary_x) + 0.15)
        b_pts = [center + scale * np.array([x, y, 0])
                 for x, y in zip(boundary_x, boundary_y)]

        boundary = VMobject()
        boundary.set_points_as_corners(b_pts)
        boundary.set_stroke(YELLOW_C, width=2.5)
        boundary.set_opacity(0.7)

        boundary_label = Tex(r"learned boundary", font_size=18, color=YELLOW_C)
        boundary_label.move_to([3.8, 1.4, 0])

        self.play(Create(boundary), Write(boundary_label), run_time=1.5)

        # Highlight misclassifications
        mis_out = outbreak_dots[7]
        mis_skip = skip_dots[12]
        circ_out = Circle(radius=0.14, color=C_OUTBREAK, stroke_width=2.5)
        circ_out.move_to(mis_out.get_center())
        circ_skip = Circle(radius=0.14, color=C_SKIP, stroke_width=2.5)
        circ_skip.move_to(mis_skip.get_center())

        self.play(Create(circ_out), Create(circ_skip), run_time=0.6)
        self.wait(0.5)

        # Negations — slow, keep circles visible
        neg1 = Tex(r"No natural $S$–$I$ phase plane", font_size=26, color=GRAY_B)
        neg2 = Tex(r"No direct $S_0$ threshold", font_size=26, color=GRAY_B)
        neg3 = Tex(r"No simple outbreak/skip geometry", font_size=26, color=GRAY_B)
        negs = VGroup(neg1, neg2, neg3).arrange(DOWN, buff=0.4)
        negs.to_edge(LEFT, buff=1.0)
        negs.shift(DOWN * 0.3)

        self.play(FadeOut(boundary), FadeOut(boundary_label), run_time=0.5)
        self.play(Write(neg1), run_time=0.8)
        self.wait(0.3)
        self.play(Write(neg2), run_time=0.8)
        self.wait(0.3)
        self.play(Write(neg3), run_time=0.8)
        self.wait(1.0)

        self.nn_group = VGroup(
            nn_title, subtitle, embed_title, proj_label, frame,
            pc1, pc2, outbreak_dots, skip_dots, mixed_dots,
            legend, illust_label, circ_out, circ_skip, negs
        )
        self.play(FadeOut(self.nn_group), run_time=1.0)

    def play_final_message(self):
        final_text = Tex(
            r"\textbf{Forced SIR: small enough to draw, complex enough to explain.}",
            font_size=36, color=C_TEXT
        )
        final_text.move_to(ORIGIN)

        self.play(Write(final_text), run_time=1.2)
        self.wait(4.0)
        self.play(FadeOut(final_text), run_time=1.0)

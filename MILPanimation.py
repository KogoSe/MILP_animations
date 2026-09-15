from manim import *

class koko(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
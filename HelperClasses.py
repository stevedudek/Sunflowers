from HelperFunctions import*

#
# Fader class and its collection: the Faders class
#
class Faders(object):
    def __init__(self, sunflower_model, max_faders=1000):
        self.sunflower = sunflower_model
        self.fader_array = []
        self.max_faders = max_faders

    def add_fader(self, color, pos, change=0.1, intense=1.0, growing=False):
        new_fader = Fader(self.sunflower, color, pos, change, intense, growing)
        self.add_fader_obj(new_fader)

    def add_fader_obj(self, new_fader):
        if self.num_faders() < self.max_faders:
            self.fader_array.append(new_fader)

    def cycle_faders(self, refresh=True):
        if refresh:
            self.sunflower.black_cells()

        # Draw, update, and kill all the faders
        for f in self.fader_array:
            if f.is_alive() == True:
                f.draw_fader()
                f.fade_fader()
            else:
                f.black_cell()
                self.fader_array.remove(f)

    def num_faders(self):
        return len(self.fader_array)

    def fade_all(self):
        for f in self.fader_array:
            f.black_cell()
            self.fader_array.remove(f)

class Fader(object):
    def __init__(self, sunflower_model, color, pos, change=0.25, intense=1.0, growing=False):
        self.sunflower = sunflower_model
        self.pos = pos
        self.color = color
        self.intense = intense
        self.growing = growing
        self.decrease = change

    def draw_fader(self):
        self.sunflower.set_cell(self.pos, gradient_wheel(self.color, self.intense))

    def fade_fader(self):
        if self.growing == True:
            self.intense += self.decrease
            if self.intense > 1.0:
                self.intense = 1.0
                self.growing = False
        else:
            self.intense -= self.decrease
            if self.intense < 0:
                self.intense = 0

    def is_alive(self):
        return self.intense > 0

    def black_cell(self):
        self.sunflower.black_cell(self.pos)


class Arc(object):
    def __init__(self, sunflower_model, color, s, p, direct, fade=0.1, death=1.0):
        self.sunflower = sunflower_model
        self.color = color
        self.s = s
        self.p = p
        self.d = self.sunflower.max_dist - 1
        self.direct = direct
        self.fade = fade
        self.death = death

    def draw(self):
        new_fader = Fader(self.sunflower, self.color, meld(self.s, (self.p, self.d)), self.fade, self.death)
        return new_fader

    def move(self):
        self.d += self.direct
        return self.d > -1 and self.d <= self.sunflower.max_dist - 2

    def get_petal(self):
        return self.p

    def get_color(self):
        return self.color


class Fan(object):
    def __init__(self, sunflower_model, color, s, p, fade=0.1, death=1.0):
        self.sunflower = sunflower_model
        self.color = color
        self.s = s
        self.p = p
        self.d = 0
        self.direct = 1
        self.fade = fade
        self.death = death

    def draw(self):
        faders = [Fader(self.sunflower, changeColor(self.color, i * -5), meld(self.s, cell), self.fade, self.death)
                  for i, cell in enumerate(self.sunflower.get_fan_band(self.d, self.p))]
        return faders

    def move(self):
        self.d += self.direct
        return self.d <= self.sunflower.max_dist

    def get_fan_tips(self):
        cells = self.sunflower.get_fan_band(self.sunflower.max_dist - 1, self.p)
        (p0, d0) = cells[0]
        (px, dx) = cells[-1]
        return [p0, px]

    def get_color(self):
        return self.color

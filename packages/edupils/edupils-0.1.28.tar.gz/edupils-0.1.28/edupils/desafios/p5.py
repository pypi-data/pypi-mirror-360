from js import p5

def setup():
    canvas = p5.createCanvas(400, 200)
    canvas.parent("canvas-container")  # Set the parent of the canvas
    p5.background(100)

def draw():
    p5.fill(255, 0, 0)
    p5.ellipse(p5.mouseX, p5.mouseY, 50, 50)

p5.setup = setup
p5.draw = draw
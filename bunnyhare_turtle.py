import turtle
import random
import time
import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "_tmp_turtle_imgs")
os.makedirs(TMP_DIR, exist_ok=True)

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

def extract_frames_from_gif(src_filename, dest_prefix, size=None):
    src_path = os.path.join(BASE_DIR, src_filename)
    if not os.path.exists(src_path):
        return []
    frames = []
    with Image.open(src_path) as img:
        try:
            i = 0
            while True:
                img.seek(i)
                frame = img.convert("RGBA")
                if size:
                    frame.thumbnail(size, resample=RESAMPLE)
                canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                canvas.paste(frame, (0, 0), frame)
                pal = canvas.convert("P", palette=Image.ADAPTIVE, colors=255)
                alpha = canvas.split()[-1]
                mask = Image.eval(alpha, lambda a: 255 if a <= 0 else 0)
                pal.paste(255, box=None, mask=mask)
                save_path = os.path.join(TMP_DIR, f"{dest_prefix}_{i}.gif")
                pal.save(save_path, format="GIF", transparency=255, save_all=False, optimize=True)
                frames.append(save_path)
                i += 1
        except EOFError:
            pass
    return frames

def convert_png_to_transparent_gif(src_filename, dest_name, size=None):
    src_path = os.path.join(BASE_DIR, src_filename)
    if not os.path.exists(src_path):
        return None
    with Image.open(src_path) as img:
        img = img.convert("RGBA")
        if size:
            img.thumbnail(size, resample=RESAMPLE)
        canvas = Image.new("RGBA", img.size, (0,0,0,0))
        canvas.paste(img, (0,0), img)
        pal = canvas.convert("P", palette=Image.ADAPTIVE, colors=255)
        alpha = canvas.split()[-1]
        mask = Image.eval(alpha, lambda a: 255 if a <= 0 else 0)
        pal.paste(255, box=None, mask=mask)
        dest = os.path.join(TMP_DIR, dest_name + ".gif")
        pal.save(dest, format="GIF", transparency=255, optimize=True)
    return dest

bg_path = os.path.join(BASE_DIR, "Background.png")
if os.path.exists(bg_path):
    bg_img = Image.open(bg_path)
    bg_img = bg_img.resize((700, 400), resample=RESAMPLE)
    bg_img.save(os.path.join(TMP_DIR, "Background_resized.gif"), "GIF")
    bg_pic_path = os.path.join(TMP_DIR, "Background_resized.gif")
else:
    bg_pic_path = None

turtle_frames = extract_frames_from_gif("Turtle.gif", "Turtle", (80, 80))
bunny_frames = extract_frames_from_gif("Bunny.gif", "Bunny", (80, 80))
zzz_gif = convert_png_to_transparent_gif("zzz.png", "zzz", (50, 30))

screen = turtle.Screen()
screen.title("Turtle 🐢 vs Bunny 🐇 Race")
screen.setup(width=700, height=400)
screen.tracer(0)
if bg_pic_path:
    screen.bgpic(bg_pic_path)

def register_frames(frames, prefix):
    registered = []
    for i, fpath in enumerate(frames):
        name = f"{prefix}_frame_{i}"
        try:
            screen.register_shape(name, turtle.Shape("image", fpath))
            registered.append(name)
        except:
            try:
                screen.register_shape(fpath)
                registered.append(fpath)
            except:
                pass
    return registered

turtle_shape_names = register_frames(turtle_frames, "turtle")
bunny_shape_names = register_frames(bunny_frames, "bunny")
zzz_shape_name = None
if zzz_gif and os.path.exists(zzz_gif):
    try:
        screen.register_shape("zzz_shape", turtle.Shape("image", zzz_gif))
        zzz_shape_name = "zzz_shape"
    except:
        try:
            screen.register_shape(zzz_gif)
            zzz_shape_name = zzz_gif
        except:
            pass

turtle_racer = turtle.Turtle()
bunny = turtle.Turtle()
zzz_turtle = turtle.Turtle()
result = turtle.Turtle()

for t in [turtle_racer, bunny, zzz_turtle, result]:
    t.hideturtle()
    t.penup()

finish_line = 700 // 2 - 100

line = turtle.Turtle()
line.hideturtle()
line.penup()
line.goto(finish_line, -400 // 2 + 50)
line.setheading(90)
line.pendown()
line.pensize(3)
line.color("white")
line.forward(400 - 100)

BASELINE_Y = -400 // 2 + 70
anim_state = {"turtle_idx": 0, "bunny_idx": 0, "running": False, "bunny_sleeping": False}

def setup_race():
    screen.tracer(0)
    turtle_racer.reset()
    turtle_racer.penup()
    turtle_racer.goto(-700 // 2 + 100, BASELINE_Y)
    if turtle_shape_names:
        turtle_racer.shape(turtle_shape_names[0])
    turtle_racer.showturtle()
    bunny.reset()
    bunny.penup()
    bunny.goto(-700 // 2 + 95, BASELINE_Y)
    if bunny_shape_names:
        bunny.shape(bunny_shape_names[0])
    bunny.showturtle()
    zzz_turtle.reset()
    zzz_turtle.penup()
    zzz_turtle.hideturtle()
    if zzz_shape_name:
        zzz_turtle.shape(zzz_shape_name)
    result.clear()
    result.hideturtle()
    result.penup()
    result.goto(0, 0)
    screen.update()
    screen.tracer(1)

def start_race():
    setup_race()
    anim_state["running"] = True
    anim_state["bunny_sleeping"] = False

    countdown = turtle.Turtle()
    countdown.hideturtle()
    countdown.penup()
    countdown.color("white")
    countdown.goto(0, 40)
    for i in range(3, 0, -1):
        countdown.clear()
        countdown.write(str(i), align="center", font=("Arial", 36, "bold"))
        screen.update()
        time.sleep(1)
    countdown.clear()
    countdown.write("Go!", align="center", font=("Arial", 36, "bold"))
    screen.update()
    time.sleep(0.8)
    countdown.clear()

    bunny_stopped = False
    bunny_sleep_start = None
    bunny_sleep_duration = random.uniform(8.5, 9.5)
    winner = None

    while True:
        anim_state["turtle_idx"] = (anim_state["turtle_idx"] + 1) % len(turtle_shape_names)
        turtle_racer.shape(turtle_shape_names[anim_state["turtle_idx"]])

        if not anim_state["bunny_sleeping"]:
            anim_state["bunny_idx"] = (anim_state["bunny_idx"] + 1) % len(bunny_shape_names)
            bunny.shape(bunny_shape_names[anim_state["bunny_idx"]])

        turtle_racer.forward(random.uniform(2.2, 2.7))

        if not bunny_stopped and bunny.xcor() > 100:
            bunny_stopped = True
            anim_state["bunny_sleeping"] = True
            bunny_sleep_start = time.time()
            if zzz_shape_name:
                x, y = bunny.position()
                zzz_turtle.goto(x + 15, y + 30)
                zzz_turtle.showturtle()
        elif bunny_stopped:
            if time.time() - bunny_sleep_start >= bunny_sleep_duration:
                bunny_stopped = "done"
                anim_state["bunny_sleeping"] = False
                zzz_turtle.hideturtle()
        else:
            if not anim_state["bunny_sleeping"]:
                bunny.forward(random.uniform(3.7, 4.2))

        if bunny_stopped == "done" and not anim_state["bunny_sleeping"]:
            bunny.forward(random.uniform(3.9, 4.4))

        screen.update()

        if turtle_racer.xcor() >= finish_line:
            winner = "turtle"
            turtle_racer.setx(finish_line)
            break
        elif bunny.xcor() >= finish_line:
            winner = "bunny"
            bunny.setx(finish_line)
            break

        time.sleep(0.06)

    anim_state["running"] = False
    zzz_turtle.hideturtle()
    result.color("white")
    result.clear()
    if winner == "turtle":
        result.write("The Turtle 🐢 wins!", align="center", font=("Arial", 24, "bold"))
    elif winner == "bunny":
        result.write("The Bunny 🐇 wins!", align="center", font=("Arial", 24, "bold"))
    else:
        result.write("It's a tie!", align="center", font=("Arial", 24, "bold"))
    screen.update()

def reset_race():
    result.clear()
    start_race()

start_race()
screen.listen()
screen.onkey(reset_race, "space")
screen.mainloop()

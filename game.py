import time
import random
import winsound
from turtle import Turtle, Screen


def start_game():
    class Bullet(Turtle):
        def __init__(self, direction):
            super().__init__()
            self.color("white")
            self.shape("bullet")
            self.shapesize(stretch_wid=0.5, stretch_len=1)  # Adjust the size of the bullet
            self.penup()
            self.setheading(90 if direction == 1 else 270)  # Ensure the bullet is oriented correctly
            self.y_move = 20 * direction  # Increase bullet speed
            self.state = "ready"

        def fire(self, x, y):
            if self.state == "ready":
                self.state = "fire"
                self.goto(x, y)
                self.showturtle()
                winsound.PlaySound("shoot.wav", winsound.SND_ASYNC)
                print(f"Bullet fired from ({x}, {y})")

        def move(self):
            if self.state == "fire":
                new_y = self.ycor() + self.y_move
                self.goto(self.xcor(), new_y)
                if self.ycor() > 380 or self.ycor() < -380:
                    self.destroy()
                for barrier in barriers:
                    for part in barrier.parts:
                        if part.is_collision(self):
                            self.destroy()
                            part.hit()

        def destroy(self):                
            self.hideturtle()
            self.state = "ready"
            self.goto(-250, -400)
            bullets.remove(self)
            del self
            print("Bullet destroyed")

    class Player(Turtle):
        def __init__(self, start_x, start_y, shoot_direction, lives_label, health_bar_x, health_bar_y):
            super().__init__()
            self.shape("triangle")
            self.color("white")
            self.penup()
            self.shapesize(stretch_wid=1, stretch_len=2)
            self.goto(start_x, start_y)
            self.shoot_delay = 0.2  # Decrease shoot delay for faster shooting
            self.last_shot_time = time.time()
            self.moving_left = False
            self.moving_right = False
            self.shoot_direction = shoot_direction
            self.lives = 3
            self.lives_label = lives_label
            self.health_bar = Turtle()
            self.health_bar.color("green")
            self.health_bar.shape("square")
            self.health_bar.shapesize(stretch_wid=1, stretch_len=6)  # Initial health bar size
            self.health_bar.penup()
            self.health_bar.goto(health_bar_x, health_bar_y)
            self.health_bar.showturtle()
            self.protected = False  # Protection state
            if shoot_direction == -1:
                self.setheading(270)  # Point the triangle downwards
            else:
                self.setheading(90)  # Point the triangle upwards
            self.update_lives_label()

        def update_health_bar(self):
            if self.lives > 0:
                self.health_bar.shapesize(stretch_wid=1, stretch_len=2 * self.lives)
            else:
                self.health_bar.hideturtle()

        def update_lives_label(self):
            self.lives_label.clear()
            self.lives_label.write(f"Player {'One' if self.shoot_direction == 1 else 'Two'} lives:", align="center", font=("Arial", 16, "normal"))

        def move_right(self):
            new_x = self.xcor() + 5  # Move 5 units per interval
            if new_x < 300:  # Adjusted right boundary to avoid hearts
                self.goto(new_x, self.ycor())

        def move_left(self):
            new_x = self.xcor() - 5  # Move 5 units per interval
            if new_x > -300:  # Adjusted left boundary to avoid hearts
                self.goto(new_x, self.ycor())

        def start_moving_right(self):
            self.moving_right = True
            self.move_right()

        def stop_moving_right(self):
            self.moving_right = False

        def start_moving_left(self):
            self.moving_left = True
            self.move_left()

        def stop_moving_left(self):
            self.moving_left = False

        def shoot_bullet(self):
            current_time = time.time()
            if current_time - self.last_shot_time > self.shoot_delay:
                bullet = Bullet(self.shoot_direction)
                bullet.fire(self.xcor(), self.ycor() + 20 * self.shoot_direction)
                bullets.append(bullet)
                self.last_shot_time = current_time
                print(f"Bullet created at ({self.xcor()}, {self.ycor()})")

        def hit(self):
            if not self.protected:
                self.lives -= 1
                self.update_health_bar()
                self.update_lives_label()
                if self.lives <= 0:
                    self.destroy()
                    if self.shoot_direction == 1:
                        show_winner("Player Two")
                    else:
                        show_winner("Player One")
                else:
                    self.activate_protection()
                print(f"{self} has {self.lives} lives left")

        def activate_protection(self):
            self.protected = True
            self.blink()
            screen.ontimer(self.deactivate_protection, 2000)  # Deactivate protection after 2 seconds

        def deactivate_protection(self):
            self.protected = False
            self.showturtle()  # Ensure the player is visible after protection ends

        def blink(self):
            if self.protected:
                if self.isvisible():
                    self.hideturtle()
                else:
                    self.showturtle()
                screen.ontimer(self.blink, 100)  # Blink every 100ms

        def destroy(self):
            self.hideturtle()
            self.goto(-250, -400)
            self.health_bar.hideturtle()

    class BarrierPart(Turtle):
        def __init__(self, x, y):
            super().__init__()
            self.shape("square")
            self.color("green")
            self.shapesize(stretch_wid=0.5, stretch_len=5)  # Make the barrier parts thinner
            self.penup()
            self.goto(x, y)
            self.health = 1

        def is_collision(self, bullet):
            return abs(self.xcor() - bullet.xcor()) < 50 and abs(self.ycor() - bullet.ycor()) < 10  # Adjusted hitbox

        def hit(self):
            self.health -= 1
            if self.health <= 0:
                self.destroy()
            print(f"Barrier part at ({self.xcor()}, {self.ycor()}) hit, health: {self.health}")

        def destroy(self):
            self.hideturtle()
            for barrier in barriers:
                if self in barrier.parts:
                    barrier.parts.remove(self)
                    break
            del self
            print("Barrier part destroyed")

    class Barrier:
        def __init__(self, x, y):
            self.parts = [
                BarrierPart(x, y + 25),
                BarrierPart(x, y),
                BarrierPart(x, y - 25)
            ]

    def shooting(player):
        player.shoot_bullet()

    def create_heart_shape():
        screen.register_shape("heart", (
            (0, 0), (10, 10), (20, 0), (10, -10), (0, 0),
            (0, -10), (-10, -10), (-20, 0), (-10, 10), (0, 0)
        ))

    def create_bullet_shape():
        screen.register_shape("bullet", (
            (0, 0), (2, 10), (0, 20), (-2, 10), (0, 0)
        ))

    def show_winner(winner):
        screen.clearscreen()  # Clear the screen
        screen.bgcolor("black")  # Set background to black
        message = Turtle()
        message.color("green")  # Set text color to green
        message.penup()
        message.hideturtle()
        message.goto(0, 0)
        message.write(f"{winner} Won the Game!", align="center", font=("Arial", 36, "normal"))
        global game_is_on
        game_is_on = False

    def move_barriers():
        global barrier_direction
        for barrier in barriers:
            for part in barrier.parts:
                new_x = part.xcor() + barrier_direction
                part.goto(new_x, part.ycor())
        # Reverse direction if any part hits the boundary
        if any(part.xcor() > 280 or part.xcor() < -280 for barrier in barriers for part in barrier.parts):
            barrier_direction *= -1

    screen = Screen()
    screen.setup(width=1.0, height=1.0)  # Set the screen to fullscreen
    screen.bgcolor("black")
    screen.title("Space Invaders")
    screen.tracer(0)

    # Make the window fullscreen
    screen.cv._rootwindow.attributes('-fullscreen', True)

    # Register shapes
    create_heart_shape()
    create_bullet_shape()

    # Create labels for player lives
    player_one_lives_label = Turtle()
    player_one_lives_label.color("white")
    player_one_lives_label.penup()
    player_one_lives_label.hideturtle()
    player_one_lives_label.goto(300, -350)

    player_two_lives_label = Turtle()
    player_two_lives_label.color("white")
    player_two_lives_label.penup()
    player_two_lives_label.hideturtle()
    player_two_lives_label.goto(-300, -350)

    player1 = Player(0, -300, 1, player_one_lives_label, 300, -370)
    player2 = Player(0, 300, -1, player_two_lives_label, -300, -370)
    bullets = []

    # Create barriers closer to players
    barriers = [
        Barrier(-200, -200), Barrier(0, -200), Barrier(200, -200),  # Player 1 barriers
        Barrier(-200, 200), Barrier(0, 200), Barrier(200, 200)  # Player 2 barriers
    ]

    global barrier_direction
    barrier_direction = 2  # Initial direction and speed of barrier movement

    screen.listen()
    screen.onkeypress(player1.start_moving_right, "d")
    screen.onkeyrelease(player1.stop_moving_right, "d")
    screen.onkeypress(player1.start_moving_left, "a")
    screen.onkeyrelease(player1.stop_moving_left, "a")
    screen.onkey(lambda: shooting(player1), "space")

    screen.onkeypress(player2.start_moving_right, "Right")
    screen.onkeyrelease(player2.stop_moving_right, "Right")
    screen.onkeypress(player2.start_moving_left, "Left")
    screen.onkeyrelease(player2.stop_moving_left, "Left")
    screen.onkey(lambda: shooting(player2), "Return")

    game_is_on = True

    while game_is_on:
        time.sleep(0.01)  # Decrease the sleep time for faster updates
        screen.update()

        if player1.moving_right:
            player1.move_right()
        if player1.moving_left:
            player1.move_left()
        if player2.moving_right:
            player2.move_right()
        if player2.moving_left:
            player2.move_left()

        for bullet in bullets:
            bullet.move()

            if bullet.state == "fire":
                if bullet.y_move > 0 and bullet.distance(player2) < 20:
                    if not player2.protected:
                        bullet.destroy()
                        player2.hit()
                        winsound.PlaySound("hit.wav", winsound.SND_ASYNC)
                        print("Player 1 hits Player 2!")
                elif bullet.y_move < 0 and bullet.distance(player1) < 20:
                    if not player1.protected:
                        bullet.destroy()
                        player1.hit()
                        winsound.PlaySound("hit.wav", winsound.SND_ASYNC)
                        print("Player 2 hits Player 1!")

        move_barriers()  

    screen.mainloop()


start_game()

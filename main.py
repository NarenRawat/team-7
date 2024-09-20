import pygame
import cv2
from pathlib import Path
from random import randint, choice

pygame.init()

ROOT_DIR = Path(__file__).parent
ASSETS_DIR = ROOT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
VIDEOS_DIR = ASSETS_DIR / "videos"
AUDIO_DIR = ASSETS_DIR / "audio"

# Window
WIN_WIDTH = 0
WIN_HEIGHT = 0
WIN_SIZE = None
screen = None

# Game Variables
GAME_FPS = 15
VIDEO_FPS = 30
clock = pygame.time.Clock()
running = True

comic_font = pygame.font.SysFont("Comic Sans MS", 22)
comic_font_30 = pygame.font.SysFont("Comic Sans MS", 30)
intro_skip_label = comic_font.render(
    "Press SPACE to skip...", True, (180, 180, 180)
)
scroll_speed = 15
score = 0

# Intro
intro_playing = True
intro_video = cv2.VideoCapture(VIDEOS_DIR / "intro.mp4")

# Background
bg_img = None


# Bheem
n_bheem_frames = 8
bheem_frames = []
bheem_current_frame = 0
bheem_x = 200
bheem_y = 0
bheem_max_y = 0
bheem_width = 0
bheem_height = 0
jump_height = 250
bheem_jumping = False
fall_speed = 10
collided = False

# Ground
ground_img = None
n_grounds = 0
ground_width = 0
ground_height = 0
ground_x = 0
ground_y = 0

# Obstacles
rock_img = None
cactus_img = None
obstacles = []
ROCK = 0
CACTUS = 1
spawn_timer = 0

pygame.mixer.music.load(AUDIO_DIR / "bg_music.ogg")
jump_sound = pygame.mixer.Sound(AUDIO_DIR / "jump.ogg")



def load_bheem():
    global bheem_y, bheem_max_y, bheem_width, bheem_height

    for i in range(n_bheem_frames):
        bheem_frames.append(
            pygame.image.load(
                IMAGES_DIR / f"bheem_{i}.png"
            ).convert_alpha()
        )

    first_frame = bheem_frames[0]
    bheem_width = first_frame.get_width()
    bheem_height = first_frame.get_height()

    bheem_y = WIN_HEIGHT - first_frame.get_height() - ground_height + 10
    bheem_max_y = bheem_y


def load_background():
    global bg_img
    bg_img = pygame.image.load(IMAGES_DIR / "bg.jpeg").convert()
    bg_img = pygame.transform.scale(bg_img, (WIN_WIDTH, WIN_HEIGHT))


def load_ground():
    global ground_img, ground_width, ground_height, n_grounds, ground_y
    ground_img = pygame.image.load(
        IMAGES_DIR / "ground0.jpg"
    ).convert_alpha()
    ground_width, ground_height = ground_img.get_size()
    n_grounds = WIN_WIDTH // ground_width + 2
    ground_y = WIN_HEIGHT - ground_height


def load_obstacles():
    global rock_img, cactus_img

    rock_img = pygame.image.load(
        IMAGES_DIR / "rock1.png"
    ).convert_alpha()

    cactus_img = pygame.image.load(
        IMAGES_DIR / "cactus1.png"
    ).convert_alpha()


def game_intro():
    success, img = intro_video.read()
    img = cv2.resize(img, (WIN_WIDTH, WIN_HEIGHT))
    shape = img.shape[1::-1]

    while intro_playing and success:
        screen.blit(
            pygame.image.frombuffer(img.tobytes(), shape, "BGR"), (0, 0)
        )

        screen.blit(
            intro_skip_label,
            (
                WIN_WIDTH - intro_skip_label.get_width(),
                WIN_HEIGHT - intro_skip_label.get_height(),
            ),
        )
        dt = clock.tick(VIDEO_FPS) / 1000.0
        pygame.display.update()
        check_events()

        success, img = intro_video.read()
        if success:
            img = cv2.resize(img, (WIN_WIDTH, WIN_HEIGHT))


def check_events():
    global running, intro_playing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                running = False
                intro_playing = False
            if event.key == pygame.K_SPACE:
                if intro_playing:
                    intro_playing = False
                else:
                    bheem_jump()
            if event.key == pygame.K_RETURN and collided:
                reset()


def draw_bheem():
    screen.blit(bheem_frames[bheem_current_frame], (bheem_x, bheem_y))


def draw_ground():
    for i in range(n_grounds):
        screen.blit(ground_img, (ground_x + ground_width * i, ground_y))


def draw_score():
    score_label = comic_font.render(
        f"Score: {int(score)}", True, (255, 255, 255)
    )
    screen.blit(
        score_label,
        ((WIN_WIDTH - score_label.get_width()) // 2, 0),
    )


def update_ground():
    global ground_x
    ground_x -= scroll_speed
    if ground_x <= -ground_width:
        ground_x = 0


def update_bheem():
    global bheem_current_frame, bheem_y, bheem_jumping

    bheem_current_frame += 1
    if bheem_current_frame >= n_bheem_frames:
        bheem_current_frame = 0

    if bheem_jumping:
        bheem_current_frame = 0
        bheem_y += fall_speed
        if bheem_y >= bheem_max_y:
            bheem_y = bheem_max_y
            bheem_jumping = False


def bheem_jump():
    global bheem_y, bheem_jumping
    if not bheem_jumping:
        bheem_y -= jump_height
        bheem_jumping = True
        pygame.mixer.Sound.play(jump_sound)



def draw_obstacles():
    for obst, rect in obstacles:
        if obst == ROCK:
            screen.blit(rock_img, rect)
        elif obst == CACTUS:
            screen.blit(cactus_img, rect)


def spawn_obstacle():
    obst = choice([ROCK, CACTUS])
    rect = cactus_img.get_rect()
    rect.x = WIN_WIDTH + randint(10, 100)
    rect.y = WIN_HEIGHT - rect.height - ground_height + 10

    obstacles.append((obst, rect))


def update_obstacles():
    for obst in obstacles:
        rect = obst[1]
        rect.x -= scroll_speed

        if rect.right <= 0:
            obstacles.remove(obst)


def check_collision():
    global collided
    for obst in obstacles:
        obst_rect = obst[1]
        bheem_rect = pygame.Rect(
            bheem_x, bheem_y, bheem_width, bheem_height
        )
        if obst_rect.colliderect(bheem_rect):
            collided = True


def reset():
    global score, spawn_timer, GAME_FPS, collided, bheem_y
    score = 0
    spawn_timer = 0
    GAME_FPS = 15
    obstacles.clear()
    collided = False
    bheem_y = bheem_max_y


def main():
    global screen, WIN_HEIGHT, WIN_WIDTH, WIN_SIZE, intro_playing, score, GAME_FPS, spawn_timer
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    pygame.display.set_caption("Kirmada Ka Keher")
    WIN_SIZE = screen.get_size()
    WIN_WIDTH = screen.get_width()
    WIN_HEIGHT = screen.get_height()

    retry_label = comic_font_30.render("Press ENTER to retry", True, (255, 255, 255), (0, 0, 0))

    load_ground()
    load_bheem()
    load_background()
    load_obstacles()

    game_intro()
    intro_playing = False

    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

    while running:
        check_events()

        dt = clock.tick(GAME_FPS) / 1000.0

        if not collided:
            screen.blit(bg_img, (0, 0))

            # Update sprites
            update_ground()
            update_bheem()
            update_obstacles()

            spawn_timer += 1

            if spawn_timer >= randint(30, 70):
                spawn_obstacle()
                spawn_timer = 0

            # Draw sprites
            draw_ground()
            draw_bheem()
            draw_obstacles()
            draw_score()

            check_collision()

            score += 0.5

            if score % 30 == 0:
                GAME_FPS += 1

            if GAME_FPS >= 30:
                GAME_FPS = 30

        else:
            screen.blit(
                retry_label,
                (
                    (WIN_WIDTH - retry_label.get_width()) // 2,
                    (WIN_HEIGHT - retry_label.get_height()) // 2,
                ),
            )

        pygame.display.update()


if __name__ == "__main__":
    main()

#import modules
import pygame  
import random

# Initialize Pygame >.<
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Creates the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Load and scale images (Placeholder) I am just bored to add images 
def load_image(name, size):
    image = pygame.Surface(size)
    image.fill(WHITE)  # Create a white rectangle as a placeholder >.<
    return image

#Well if you wanna add img then feel free to make the changes 
'''
def load_image(name, size=None):
    # Load the image from the 'images' folder
    image = pygame.image.load(f"images/{name}.png").convert_alpha()
    
    if size:
        image = pygame.transform.scale(image, size)
    
    return image
'''

# Create game objects 
# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("player", (50, 40))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.lives = 3
        self.shoot_delay = 250  # Milliseconds
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        # Move the player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Keep player on screen
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return Bullet(self.rect.centerx, self.rect.top, -10)
        return None

#Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("enemy", (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 4)
        self.speed_x = random.randrange(-2, 3)
    
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()
        
        # Bounce off screen edges
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x = -self.speed_x
    
    def shoot(self):
        if random.random() < 0.01:  # 1% chance to shoot each frame
            return Bullet(self.rect.centerx, self.rect.bottom, 7)
        return None

#Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = load_image("bullet", (5, 10))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = speed
    #bullet movement
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

#Game Class (Handles Everything)
class Game:
    def __init__(self):
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Initialize score
        self.score = 0
        self.font = pygame.font.Font(None, 36)

    #Spawns enemies (you can lower it if you want)
    def spawn_enemy(self):
        if len(self.enemies) < 8 and random.random() < 0.03:
            enemy = Enemy()
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    #Collision handling 
    def handle_collisions(self):
        # Check if player bullets hit enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
        for hit in hits:
            self.score += 100

        # Check if enemy bullets hit player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits:
            self.player.lives -= 1

        # Check if enemies collide with player
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        if hits:
            self.player.lives -= 1

    def draw_ui(self):
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        lives_text = self.font.render(f'Lives: {self.player.lives}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))

    #Game loop
    def run(self):
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        bullet = self.player.shoot()
                        if bullet:
                            self.all_sprites.add(bullet)
                            self.player_bullets.add(bullet)

            # Game over check
            if self.player.lives <= 0:
                self.show_final_score()
                self.__init__()

            # Spawn enemies
            self.spawn_enemy()

            # Enemy shooting
            for enemy in self.enemies:
                bullet = enemy.shoot()
                if bullet:
                    self.all_sprites.add(bullet)
                    self.enemy_bullets.add(bullet)

            # Update
            self.all_sprites.update()
            self.handle_collisions()

            # Draw
            screen.fill(BLACK)
            self.all_sprites.draw(screen)
            self.draw_ui()
            pygame.display.flip()

            # Control game speed
            clock.tick(FPS)

        pygame.quit()

    #Shows your final score
    def show_final_score(self):
        screen.fill(BLACK)  
        final_text = self.font.render(f"Game Over! Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press SPACEBAR to restart", True, WHITE)
    
        screen.blit(final_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # Wait for SPACEBAR
                        waiting = False


# Start the game
if __name__ == '__main__':
    game = Game()
    game.run()
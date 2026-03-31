import pygame
import sys
import numpy as np

# ====================== PARAMETERS ======================
WIDTH, HEIGHT = 700, 700                  # ← Smaller window size
N_PARTICLES = 10
DT = 0.032
DOMAIN_SIZE = 10.0
SCALE = WIDTH / DOMAIN_SIZE               # Automatically scales to new window size

# ====================== INITIALIZATION ======================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DustCluster Fluid Simulator - Phase 1 (10 Particles)")
clock = pygame.time.Clock()

# Initial value for position (x, y) and velocity (v_x, v_y)
np.random.seed(42)
pos = np.random.uniform(1.5, 8.5, (N_PARTICLES, 2))
vel = np.random.uniform(-1.5, 2.5, (N_PARTICLES, 2)) * 0.8

# ====================== MAIN SIMULATION LOOP ======================
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    # Physics update for each particle
    for i in range(N_PARTICLES):
        
        # 1. Gravity (only affects Y velocity)
        vel[i, 1] += -9.81 * DT * 0.9

        # 2. Update position
        pos[i] += vel[i] * DT

        # 3. Bouncing on walls
        if pos[i, 0] <= 0.5 or pos[i, 0] >= DOMAIN_SIZE - 0.5:
            vel[i, 0] *= -0.88
            pos[i, 0] = max(0.5, min(DOMAIN_SIZE - 0.5, pos[i, 0]))

        if pos[i, 1] <= 0.5 or pos[i, 1] >= DOMAIN_SIZE - 0.5:
            vel[i, 1] *= -0.88
            pos[i, 1] = max(0.5, min(DOMAIN_SIZE - 0.5, pos[i, 1]))

        # Draw particle (smaller size for small window)
        px = int(pos[i, 0] * SCALE)
        py = int((DOMAIN_SIZE - pos[i, 1]) * SCALE)
        pygame.draw.circle(screen, (210, 140, 70), (px, py), 8)   # smaller radius

    # Draw visible red boundary box #(0, 0): (left, top)
    box_x = int(0.5 * SCALE) #initial left
    box_y = int(0.5 * SCALE) #initial top
    box_w = int((DOMAIN_SIZE - 1) * SCALE) #width 
    box_h = int((DOMAIN_SIZE - 1) * SCALE) #height
    pygame.draw.rect(screen, (255, 0, 0), (box_x, box_y, box_w, box_h), 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
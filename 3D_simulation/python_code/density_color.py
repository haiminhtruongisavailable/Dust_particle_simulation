import pygame
import sys
import numpy as np

# ====================== PARAMETERS ======================
WIDTH, HEIGHT = 700, 700
N_PARTICLES = 50
DT = 0.032
DOMAIN_SIZE = 10.0
SCALE = WIDTH / DOMAIN_SIZE
H = 1.2                     # invisable influence circle (used for SPH)| maximum length that one particle can feel another(woa:))
MASS = 1.0                  # Mass of each dust cluster

# ====================== INITIALIZATION ======================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DustCluster Fluid Simulator - Phase 1 + Density")
clock = pygame.time.Clock()

np.random.seed(42)
pos = np.random.uniform(1.5, 8.5, (N_PARTICLES, 2))
vel = np.random.uniform(-1.5, 2.5, (N_PARTICLES, 2)) * 0.8

# New: Density for each particle (will be calculated every frame)
density = np.zeros(N_PARTICLES)

# ====================== Poly6 Kernel Function ======================

def poly6(r, h):
    """Poly6 smoothing kernel --> density"""
    q = r / h
    if q >= 1.0:
        return 0.0
    return (315.0 / (64.0 * np.pi * h**9)) * (h**2 - r**2)**3

# ====================== MAIN LOOP ======================
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    # ====================== 1. CALCULATE DENSITY ======================
    density.fill(0.0)                                 # reset density every frame

    for i in range(N_PARTICLES):
        for j in range(i + 1, N_PARTICLES):           # avoid double counting
            r_vec = pos[i] - pos[j]
            r = np.linalg.norm(r_vec)
            if r < H and r > 1e-8:
                influence = poly6(r, H) #inherit above
                density[i] += influence * MASS
                density[j] += influence * MASS

    # Add self-density (each particle contributes to itself)
    density += MASS * poly6(0.0, H)

    # ====================== 2. PHYSICS (Gravity + Bounce) ======================
    for i in range(N_PARTICLES):
        vel[i, 1] += -9.81 * DT * 0.9
        pos[i] += vel[i] * DT

        # Bounce
        if pos[i, 0] <= 0.5 or pos[i, 0] >= DOMAIN_SIZE - 0.5:
            vel[i, 0] *= -0.88
            pos[i, 0] = max(0.5, min(DOMAIN_SIZE - 0.5, pos[i, 0]))
        if pos[i, 1] <= 0.5 or pos[i, 1] >= DOMAIN_SIZE - 0.5:
            vel[i, 1] *= -0.88
            pos[i, 1] = max(0.5, min(DOMAIN_SIZE - 0.5, pos[i, 1]))

        # Draw particle with color based on density (yellow = dense, orange = less)
        color_intensity = int(255 - density[i] * 40)   # higher density = more yellow
        color_intensity = max(100, min(255, color_intensity))
        px = int(pos[i, 0] * SCALE)
        py = int((DOMAIN_SIZE - pos[i, 1]) * SCALE)
        pygame.draw.circle(screen, (255, color_intensity, 60), (px, py), 8)

    # Draw visible red boundary
    box_x = int(0.5 * SCALE)
    box_y = int(0.5 * SCALE)
    box_w = int((DOMAIN_SIZE - 1) * SCALE)
    box_h = int((DOMAIN_SIZE - 1) * SCALE)
    pygame.draw.rect(screen, (255, 0, 0), (box_x, box_y, box_w, box_h), 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

import pygame
import sys
import numpy as np

# ====================== PARAMETERS ======================
WIDTH, HEIGHT = 700, 700
N_PARTICLES = 2                     # Increased a bit so effects are visible
DT = 0.032
DOMAIN_SIZE = 10.0
SCALE = WIDTH / DOMAIN_SIZE
H = 1.6
MASS = 1.0
STIFFNESS = 100.0                   # Pressure strength
VISCOSITY = 0.08                    # New: Viscosity strength (friction between particles)

# ====================== INITIALIZATION ======================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DustCluster Fluid Simulator - With Viscosity")
clock = pygame.time.Clock()

np.random.seed(42)
pos = np.random.uniform(1.5, 8.5, (N_PARTICLES, 2))
vel = np.random.uniform(-1.5, 2.5, (N_PARTICLES, 2)) * 0.8

density = np.zeros(N_PARTICLES)
pressure = np.zeros(N_PARTICLES)

# ====================== KERNELS ======================
def poly6(r, h):
    q = r / h
    if q >= 1.0:
        return 0.0
    return (315.0 / (64.0 * np.pi * h**9)) * (h**2 - r**2)**3

def spiky_grad(r_vec, r, h):
    q = r / h
    if r < 1e-8 or q >= 1.0:
        return np.zeros(2)
    factor = -45.0 / (np.pi * h**6) * (1 - q**2)**2
    return factor * r_vec / r

# ====================== VISCOSITY KERNEL ======================
def viscosity_laplacian(r, h):
    q = r / h
    if q >= 1.0:
        return 0.0
    return 45.0 / (np.pi * h**6) * (1 - q)

# ====================== MAIN LOOP ======================
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    # 1. Calculate Density
    density.fill(0.0)
    for i in range(N_PARTICLES):
        for j in range(i + 1, N_PARTICLES):
            r_vec = pos[i] - pos[j]
            r = np.linalg.norm(r_vec)
            if r < H and r > 1e-8:
                influence = poly6(r, H)
                density[i] += influence * MASS
                density[j] += influence * MASS
    density += MASS * poly6(0.0, H)

    # 2. Calculate Pressure
    for i in range(N_PARTICLES):
        pressure[i] = STIFFNESS * (density[i] - 1.0)

    # 3. Physics + Pressure Force + Viscosity
    for i in range(N_PARTICLES):
        # Gravity
        vel[i, 1] += -9.81 * DT * 0.9

        # Pressure Force
        pressure_force = np.zeros(2)
        for j in range(N_PARTICLES):
            if i == j: continue
            r_vec = pos[i] - pos[j]
            r = np.linalg.norm(r_vec)
            if r < H and r > 1e-8:
                p_term = -MASS * (pressure[i] / (density[i]**2) + pressure[j] / (density[j]**2))
                pressure_force += p_term * spiky_grad(r_vec, r, H)

        # Viscosity (new part) - makes motion smoother
        viscosity_force = np.zeros(2)
        for j in range(N_PARTICLES):
            if i == j: continue
            r_vec = pos[i] - pos[j]
            r = np.linalg.norm(r_vec)
            if r < H and r > 1e-8:
                v_diff = vel[j] - vel[i]
                visc = VISCOSITY * MASS * v_diff * viscosity_laplacian(r, H) / density[j]
                viscosity_force += visc

        # Apply forces
        vel[i] += pressure_force * DT
        vel[i] += viscosity_force * DT

        # Update position
        pos[i] += vel[i] * DT

        # Bounce
        if pos[i, 0] <= 0.5 or pos[i, 0] >= DOMAIN_SIZE - 0.5:
            vel[i, 0] *= -0.88
            pos[i, 0] = max(0.5, min(DOMAIN_SIZE - 0.5, pos[i, 0]))
        if pos[i, 1] <= 0.5 or pos[i, 1] >= DOMAIN_SIZE - 0.5:
            vel[i, 1] *= -0.88
            pos[i, 1] = max(0.5, min(DOMAIN_SIZE - 0.5, pos[i, 1]))

        # Draw: Higher density = Brighter yellow
        brightness = int(180 + density[i] * 35)
        brightness = max(80, min(255, brightness))
        px = int(pos[i, 0] * SCALE)
        py = int((DOMAIN_SIZE - pos[i, 1]) * SCALE)
        pygame.draw.circle(screen, (255, brightness, 50), (px, py), 8)

    # Red boundary
    box_x = int(0.5 * SCALE)
    box_y = int(0.5 * SCALE)
    box_w = int((DOMAIN_SIZE - 1) * SCALE)
    box_h = int((DOMAIN_SIZE - 1) * SCALE)
    pygame.draw.rect(screen, (255, 0, 0), (box_x, box_y, box_w, box_h), 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
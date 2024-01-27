import sys
import pygame
import random
import math

# CellActivity class
class CellActivity:
    def __init__(self, initial_nutrients=100):
        self.nutrients = initial_nutrients
        self.secondary_metabolites = 0
        self.iterations_without_nutrients = 0

    def update_activity(self, cell):
        # Consume nutrients
        nutrient_consumption = 0.1
        if self.nutrients >= nutrient_consumption:
            self.nutrients -= nutrient_consumption
            # Process consumed nutrients (you can customize this part)
            cell.energy += nutrient_consumption

            # Check for the production of secondary metabolites
            if (cell.cell_activity.nutrients - self.nutrients) % 1 == 0:
                self.secondary_metabolites += 0.05

            # Reset the count for iterations without nutrients
            self.iterations_without_nutrients = 0
        else:
            # Increment the count for iterations without nutrients
            self.iterations_without_nutrients += 1

            # If nutrients are exhausted for a certain number of iterations, the cell dies
            if self.iterations_without_nutrients >= 5:
                cell.die()

# Cell class
class Cell:
    cell_animation = []
    for i in range(6):
        image_path = f"media/cell_1/image_{i}.png"
        cell_animation.append(pygame.image.load(image_path))

    def __init__(self, screen, animation_speed=1.0, initial_x=0, initial_y=0):
        self.screen = screen
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.image = self.cell_animation[self.current_frame]
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        self.rect.x = initial_x
        self.rect.y = initial_y

        # Initialize cell activity
        self.cell_activity = CellActivity()

        # Additional attributes for cell energy and secondary metabolites
        self.energy = 0
        self.secondary_metabolites = 0
        self.iterations_since_birth = 0
        self.dead = False
        self.max_iterations = random.randint(1, 72)  # Set a random maximum iteration limit

    def update_image(self):
        self.current_frame = (self.current_frame + 1) % len(self.cell_animation)
        self.image = self.cell_animation[self.current_frame]

    def output(self):
        self.screen.blit(self.image, self.rect)

    def update_animation(self):
        for _ in range(int(self.animation_speed)):
            self.update_image()

    def update_activity(self):
        self.cell_activity.update_activity(self)
        self.iterations_since_birth += 1

        # Check for cell division
        if self.iterations_since_birth % 20 == 0 and self.iterations_since_birth != 0:
            self.divide()

        # Check if the cell has reached its maximum iterations
        if self.iterations_since_birth >= self.max_iterations:
            self.die()

    def die(self):
        self.dead = True

    def divide(self):
        # Check if there is enough space around the cell to divide
        available_space = self.check_available_space()

        if available_space:
            # Create a new cell with the same attributes as the parent cell
            new_cell = Cell(self.screen, self.animation_speed, self.rect.x, self.rect.y)
            # Reset some attributes for the new cell
            new_cell.iterations_since_birth = 0
            new_cell.dead = False

            # Add the new cell to the list of cells
            cells.append(new_cell)

    def check_available_space(self):
        # Check if there is enough space around the cell for division
        required_space = 50  # Adjust this value based on your preference
        for other_cell in cells:
            if other_cell != self:
                dx = other_cell.rect.x - self.rect.x
                dy = other_cell.rect.y - self.rect.y
                distance_squared = dx ** 2 + dy ** 2
                combined_radius = self.rect.width / 2 + other_cell.rect.width / 2

                if distance_squared < (combined_radius + required_space) ** 2:
                    # Not enough space for division
                    return False

        # Enough space for division
        return True

# Pygame initialization
pygame.init()
screen_size = (907, 838)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Under microscope - light version')

icon = pygame.image.load("./media/nucleus.png")
bg = pygame.image.load('./media/bg_game.png')

# Background music
bg_sound_paths = ["media/bg_music/track_1.mp3", "media/bg_music/track_2.mp3"]
current_bg_sound_index = 0
bg_sound = pygame.mixer.Sound(bg_sound_paths[current_bg_sound_index])
bg_sound.play()

# Create cells with different animation speed
num_cells = 10
cells = [Cell(screen, animation_speed=random.uniform(0.5, 2.0),
              initial_x=random.uniform(0, screen_size[0]),
              initial_y=random.uniform(0, screen_size[1]))
         for _ in range(num_cells)]

# Counters
iteration_counter = 0
newborn_counter = 0
dead_counter = 0

# Control panel dimensions
panel_height = 200
panel_color = (0, 0, 0)
panel_rect = pygame.Rect(0, screen_size[1] - panel_height, screen_size[0], panel_height)

# Button dimensions and color
button_width = 100
button_height = 50
button_color = (255, 255, 255)
button_rect = pygame.Rect(screen_size[0] - button_width - 10, screen_size[1] - panel_height + 10, button_width, button_height)

# Statistics display coordinates
stats_x = 20
stats_y = 640

font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()
running = True

# Inside the main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if button_rect.collidepoint(event.pos):
                current_bg_sound_index = (current_bg_sound_index + 1) % len(bg_sound_paths)
                bg_sound.stop()
                if current_bg_sound_index < len(bg_sound_paths):
                    bg_sound = pygame.mixer.Sound(bg_sound_paths[current_bg_sound_index])
                    bg_sound.play()
            else:
                # Add a new cell at the mouse click position
                new_cell = Cell(screen, animation_speed=random.uniform(0.5, 2.0),
                                initial_x=event.pos[0], initial_y=event.pos[1])
                cells.append(new_cell)

    bg_screen = screen.blit(bg, (0, 0))
    # Check for collisions and adjust cell positions
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            dx = cells[i].rect.x - cells[j].rect.x
            dy = cells[i].rect.y - cells[j].rect.y
            distance_squared = dx ** 2 + dy ** 2
            combined_radius = cells[i].rect.width / 2 + cells[j].rect.width / 2

            if distance_squared < combined_radius ** 2:
                # Collision detected, adjust cell positions
                distance = math.sqrt(distance_squared)

                # Check for zero distance to avoid division by zero
                if distance != 0:
                    overlap = combined_radius - distance
                    # Calculate the displacement for both cells
                    dx *= overlap / distance
                    dy *= overlap / distance
                    # Move cell[i]
                    cells[i].rect.x += int(dx)
                    cells[i].rect.y += int(dy)
                    # Move cell[j]
                    cells[j].rect.x -= int(dx)
                    cells[j].rect.y -= int(dy)

    # Remove dead cells from the list
    cells = [cell for cell in cells if not cell.dead]

    for cell in cells:
        cell.update_image()

        # Update cell activity
        cell.update_activity()

        # Update cell position within screen boundaries
        cell.rect.x += random.randint(-10, 10)
        cell.rect.y += random.randint(-10, 10)

        # Ensure cells stay within screen boundaries
        cell.rect.x = max(0, min(cell.rect.x, screen_size[0] - cell.rect.width))
        cell.rect.y = max(0, min(cell.rect.y, screen_size[1] - cell.rect.height))

        cell.output()

    # Draw the control panel
    pygame.draw.rect(screen, panel_color, panel_rect)

    # Draw the button
    pygame.draw.rect(screen, button_color, button_rect)
    button_text = font.render("Music", True, (0, 0, 0))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

    # Draw statistics
    total_cells_text = font.render(f"Total Cells: {len(cells)}", True, (255, 255, 255))
    screen.blit(total_cells_text, (stats_x, stats_y))

    # Draw nutritional substance and secondary metabolites
    if cells:
        nutrient_text = font.render(f"Nutrients: {cells[0].cell_activity.nutrients:.2f}", True, (255, 255, 255))
        metabolite_text = font.render(f"Secondary Metabolites: {cells[0].cell_activity.secondary_metabolites:.2f}", True, (255, 255, 255))
        screen.blit(nutrient_text, (stats_x, stats_y + 40))
        screen.blit(metabolite_text, (stats_x, stats_y + 80))

    # Draw newborn and dead cell counters
    newborn_counter_text = font.render(f"Newborn Cells: {newborn_counter}", True, (0, 255, 0))
    dead_counter_text = font.render(f"Dead Cells: {dead_counter}", True, (255, 0, 0))
    screen.blit(newborn_counter_text, (stats_x, stats_y + 160))
    screen.blit(dead_counter_text, (stats_x + 230, stats_y + 160))

    # Draw iteration counter
    iteration_counter_text = font.render(f"Iteration: {iteration_counter}", True, (255, 255, 255))
    screen.blit(iteration_counter_text, (stats_x, stats_y + 120))

    pygame.display.flip()
    clock.tick(5)

    # Update counters
    iteration_counter += 1
    newborn_counter += sum(cell.iterations_since_birth == 1 for cell in cells)
    dead_counter += sum(cell.dead for cell in cells)  # Update dead cell counter
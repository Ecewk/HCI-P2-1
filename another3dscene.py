import pygame
import sys
import os

"""
This is pygame
This is mostly for games and is not that good for what we are trying to do.
"""
# Initialize Pygame
pygame.init()

# Set up display
display = (800, 600)
screen = pygame.display.set_mode(display)
pygame.display.set_caption("2D Parallax Example")

# Load background images
try:
    background_far_path = 'layers/background_far.png'
    background_near_path = 'layers/background_near.png'

    # Check if files exist
    if not os.path.exists(background_far_path):
        print(f"Error: {background_far_path} does not exist.")
        pygame.quit()
        sys.exit()
    if not os.path.exists(background_near_path):
        print(f"Error: {background_near_path} does not exist.")
        pygame.quit()
        sys.exit()

    background_far = pygame.image.load(background_far_path).convert()
    background_near = pygame.image.load(background_near_path).convert()
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    sys.exit()

# Print image sizes to verify they are loaded correctly
print(f"Far background size: {background_far.get_size()}")
print(f"Near background size: {background_near.get_size()}")

# Define the speed of the backgrounds
far_speed = 1
near_speed = 2

# Main loop
x_far = 0
x_near = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move the backgrounds
    x_far -= far_speed
    x_near -= near_speed

    # Reset the background positions to create a looping effect
    if x_far <= -background_far.get_width():
        x_far = 0
    if x_near <= -background_near.get_width():
        x_near = 0

    # Clear the screen
    #screen.fill((0, 0, 0))  # Fill with black to clear previous frames

    # Draw the far background
    screen.blit(background_far, (x_far, 0))
    screen.blit(background_far, (x_far + background_far.get_width(), 0))

    # Draw the near background
    screen.blit(background_near, (x_near, 0))
    screen.blit(background_near, (x_near + background_near.get_width(), 0))

    # Print positions to verify they are being updated
    print(f"x_far: {x_far}, x_near: {x_near}")

    # Update the display
    pygame.display.flip()

    # Delay to control frame rate
    pygame.time.delay(10)
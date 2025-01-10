from PIL import Image, ImageDraw

def create_image() -> Image.Image:
    # Create a blank image with a transparent background
    width = 64
    height = 64
    image = Image.new('RGBA', (width, height), (255, 0, 0, 0))  # RGBA: Red, Green, Blue, Alpha (transparency)
    draw = ImageDraw.Draw(image)

    # Define the arrow (downward) shape points
    arrow_width = 20
    arrow_height = 30

    # Triangle part of the arrow
    arrow_head = [
        (width // 2, height // 2 + arrow_height // 2),  # Arrow tip
        (width // 2 - arrow_width // 2, height // 2),   # Left point of the arrow
        (width // 2 + arrow_width // 2, height // 2)    # Right point of the arrow
    ]

    # Rectangle part of the arrow
    arrow_shaft = [
        (width // 2 - arrow_width // 6, height // 2 - arrow_height // 2),
        (width // 2 + arrow_width // 6, height // 2)
    ]

    draw.rectangle(arrow_shaft, fill="white")
    draw.polygon(arrow_head, fill="white")

    return image

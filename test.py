from threading import Condition
from sortedcontainers import SortedList


def get_fake_screen_size():
    # Example: screen 1920x1080 for testing
    return 1920, 1080

def load_screen_positions(width, height, screen_width=None, screen_height=None):
    """
    Divide the screen into blocks of size width x height.
    Returns a sorted list of (x, y) positions for browser windows.
    """
    if screen_width is None or screen_height is None:
        screen_width, screen_height = get_fake_screen_size()

    cols = screen_width // width
    rows = screen_height // height
    extra_col = extra_row = False

    if screen_width % width > width / 3:
        cols += 1
        extra_col = True
    if screen_height % height > height / 3:
        rows += 1
        extra_row = True

    print(f"[INFO] Screen: {screen_width}x{screen_height} | cols: {cols}, rows: {rows}")
    
    col_space = (screen_width - width * cols) / (cols - 1) if cols > 1 and not extra_col else 0
    row_space = (screen_height - height * rows) / (rows - 1) if rows > 1 and not extra_row else 0

    positions = []
    for row in range(rows):
        for col in range(cols):
            x = (screen_height - height) if (row == rows - 1 and extra_row) else int(row * (height + row_space))
            y = (screen_width - width) if (col == cols - 1 and extra_col) else int(col * (width + col_space))
            positions.append((x, y))
    return SortedList(positions)

# Thread-safe queue for window positions
locations = []
condition = Condition()

def get_browser_location():
    with condition:
        while not locations:
            condition.wait()
        return locations.pop(0)

def add_browser_location(value):
    with condition:
        locations.append(value)
        condition.notify_all()

if __name__ == "__main__":
    # Fake browser window size
    browser_size = (500, 400)  # width, height

    # Fake screen size, or set to None to use get_fake_screen_size
    screen_w, screen_h = 1366, 768

    # Load window positions
    positions = load_screen_positions(
        int(browser_size[0]),
        int(browser_size[1]),
        screen_width=screen_w,
        screen_height=screen_h
    )

    print("Window positions to open browsers at:")
    for i, pos in enumerate(positions, 1):
        print(f"{i:2}: x={pos[1]:4}, y={pos[0]:4}")

    # Thread-safe add/get test
    for pos in positions:
        add_browser_location(pos)
    print("\nPopping locations for browsers (simulated threads):")
    for _ in range(len(positions)):
        print(get_browser_location())

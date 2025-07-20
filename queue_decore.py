import threading
import time
import random
from queue import Queue

browser_size = (400, 300)  # width, height (int luôn cho đơn giản)
screen_width = 1920
screen_height = 1080
MAX_THREADS = 10

def load_screen_pos(width, height, screen_width, screen_height):
    col = screen_width // width
    row = screen_height // height
    flag_col = screen_width % width > width / 3
    flag_row = screen_height % height > height / 3
    if flag_col:
        col += 1
    if flag_row:
        row += 1
    col_space = (screen_width - width * col) / (col - 1) if col > 1 and not flag_col else 0
    row_space = (screen_height - height * row) / (row - 1) if row > 1 and not flag_row else 0
    positions = []
    for r in range(row):
        for c in range(col):
            x = screen_height - height if r == row-1 and flag_row else int(r * (height + row_space))
            y = screen_width - width if c == col-1 and flag_col else int(c * (width + col_space))
            positions.append((x, y))
    return positions

def worker(thread_id, q):
    pos = q.get()
    print(f"[Thread {thread_id}] Got position {pos}, processing...")
    hold_time = random.uniform(5, 10)
    time.sleep(hold_time)
    print(f"[Thread {thread_id}] Releasing position {pos} after {hold_time:.2f}s")
    q.put(pos)
    q.task_done()

if __name__ == "__main__":
    width, height = browser_size
    positions = load_screen_pos(width, height, screen_width, screen_height)
    q = Queue()
    for pos in positions:
        q.put(pos)
    
    threads = []
    n_threads = min(MAX_THREADS, len(positions))
    for i in range(n_threads):
        t = threading.Thread(target=worker, args=(i, q))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    print("All threads done!")

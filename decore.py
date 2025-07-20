import threading
import time
import random
from sortedcontainers import SortedList

browser_size = ('400', '300')  # width, height của mỗi browser (giả lập)
screen_width = 1920
screen_height = 1080
MAX_THREADS = 10

def load_screen_pos(width, height, screen_width, screen_height):
    col = screen_width // width
    row = screen_height // height
    flag_col = False
    flag_row = False
    if screen_width % width > width/3:
        col = int(col) + 1
        flag_col = True 
    if screen_height % height > height/3:
        row = int(row) + 1
        flag_row = True

    if col > 1 and not flag_col:
        col_space = (screen_width - width * col) / (col - 1)
    else:
        col_space = 0
    
    if row > 1 and not flag_row:
        row_space = (screen_height - height * row) / (row - 1)
    else:
        row_space = 0
    rs = SortedList()
    for r in range(row):
        for c in range(col):
            if r == row-1 and flag_row:
                x = screen_height - height
            else:
                x = r * (height + row_space)  
            if c == col - 1 and flag_col:
                y = screen_width - width
            else:
                y = c * (width + col_space)
            rs.add((x, y))
    return rs

condition = threading.Condition()
locations = None  # sẽ khởi tạo ở main


def get_location_browser():
    with condition:
        while not locations:
            condition.wait()
        pos = locations[0]
        locations.remove(pos)
        return pos

def add_location_browser(value):
    with condition:
        locations.add(value)
        condition.notify_all() 

def worker(thread_id):
    while True:
        pos = get_location_browser()
        print(f"[Thread {thread_id}] Got position {pos}, processing...")
        hold_time = random.uniform(5, 10)
        time.sleep(hold_time)  # giả lập xử lý
        print(f"[Thread {thread_id}] Releasing position {pos} after {hold_time:.2f}s")
        add_location_browser(pos)
        break  # remove break nếu muốn lặp lại liên tục


if __name__ == "__main__":
    width = int(browser_size[0].strip())
    height = int(browser_size[1].strip())
    locations = load_screen_pos(width, height, screen_width, screen_height)

    threads = []
    for i in range(min(MAX_THREADS, len(locations))):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("All threads done!")

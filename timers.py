#!/usr/bin/env python3
import curses
import time
from dataclasses import dataclass

@dataclass
class Timer:
    elapsed: float = 0.0
    running: bool = False
    t0: float = 0.0  # момент последнего старта

    def toggle(self):
        if self.running:
            # пауза: фиксируем наработанное время
            self.elapsed += time.monotonic() - self.t0
            self.running = False
        else:
            # старт
            self.t0 = time.monotonic()
            self.running = True

    def reset(self):
        self.elapsed = 0.0
        if self.running:
            self.t0 = time.monotonic()

    def value(self) -> float:
        # текущее значение без мутаций (однопоточный подсчёт)
        return self.elapsed + (time.monotonic() - self.t0) if self.running else self.elapsed


def fmt(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)  # сотые
    return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)   # не блокироваться на вводе
    stdscr.timeout(0)

    timers = [Timer(), Timer(), Timer()]
    last_draw = 0.0

    while True:
        ch = stdscr.getch()
        if ch != -1:
            if ch in (ord('q'), 27):  # q или ESC — выход
                break
            elif ch == ord('1'):
                timers[0].toggle()
            elif ch == ord('2'):
                timers[1].toggle()
            elif ch == ord('3'):
                timers[2].toggle()
            elif ch == ord('z'):
                timers[0].reset()
            elif ch == ord('x'):
                timers[1].reset()
            elif ch == ord('c'):
                timers[2].reset()
            elif ch == ord('r'):
                for t in timers:
                    t.reset()

        now = time.monotonic()
        if now - last_draw >= 0.05:  # ~20 FPS
            stdscr.erase()
            stdscr.addstr(0, 2, "3 таймера (однопоточно, curses)")
            stdscr.addstr(1, 2, "q/ESC — выход")
            stdscr.addstr(2, 2, "1/2/3 — старт/пауза   z/x/c — сброс   r — сброс всех")

            for i, t in enumerate(timers, 1):
                status = "RUN " if t.running else "PAUSE"
                stdscr.addstr(3 + i, 4, f"Таймер {i}: {fmt(t.value())}   [{status}]")

            stdscr.refresh()
            last_draw = now

        time.sleep(0.01)  # разгрузим CPU

if __name__ == "__main__":
    curses.wrapper(main)

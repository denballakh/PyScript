import app

from settings import *

def main():
    app.App()

if __name__ == "__main__":
    # Профилирование/Profiling
    if profile:
        import cProfile
        import pstats
        import io
        from pstats import SortKey
        pr = cProfile.Profile()
        pr.enable()

    main()

    # Профилирование/profiling
    if profile:
        # Вывод в лог профилирование времени выполнения/ output to profiling log worktime
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.FILENAME
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        file = open('logs/time_profiling.log', 'wt')
        file.write(s.getvalue())
        file.close()

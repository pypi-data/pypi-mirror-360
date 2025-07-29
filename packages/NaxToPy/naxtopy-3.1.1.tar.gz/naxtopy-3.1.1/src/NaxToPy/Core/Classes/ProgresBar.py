from abc import ABC


class ProgresBar(ABC):
    """Class with method_progress_bar(progress, total)"""

    @staticmethod
    def progres_bar(progress: float, total: float) -> None:
        """ Method that prints in the console the progress bar of the calculation.
            Input:
                progress: float | int
                total: int
            ----------
            Output:
                print()
        """
        n = 2
        percent = progress/float(total)*100
        bar = "█"*int(percent/n) + "-"*(int(100//n)-int(percent/n))
        print(f"\r|{bar}|{percent:.2f}%", end = "\r")

        if progress == total:
            print(f"|{bar}|{percent:.2f}%")

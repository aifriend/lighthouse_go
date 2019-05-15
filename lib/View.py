class View:
    """
    This class specifies the base Screen class. To define your own view, subclass
    this class and implement the functions below. This works when the game is
    two-player, adversarial and turn-based.
    """

    def initView(self, board):
        """
        Input:
            board: initialize current board
        """
        pass

    def display(self, board):
        """
        Input:
            board: current board

        Returns:
            visualization type on screen, console or streaming of text

        """
        pass

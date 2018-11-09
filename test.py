import pathlib
import os

game_folder = os.path.expanduser(r'~\Documents\Jungle Climb')


def save_score(user_score, path=game_folder + r'\high scores.txt'):
    try:
        with open(path) as f:
            scores = f.readlines()
        placement = None
        for i, score in enumerate(scores):
            if user_score > int(score[:-1]):
                placement = i
                break
        if placement is not None:
            scores.insert(placement, str(user_score)+'\n')
            with open(path, 'w') as f:
                f.writelines(scores[:-1])

    except FileNotFoundError:
        pathlib.Path(game_folder).mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.writelines([str(user_score) + '\n'] + ['0\n'] * 9)


save_score(3000)

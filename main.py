import os
import yaml
from git import Repo
from termcolor import colored


class GameData:
    def __init__(self):
        if not os.path.exists("game-data.yml"):
            open("game-data.yml", 'w').close()
            self.data = {}
        else:
            with open("game-data.yml", 'r') as file:
                self.data = yaml.safe_load(file)
        if "wins" not in self.data:
            self.data["wins"] = {"Genevieve": 0, "Alexander": 0, "Tied": 0}
        self.current_game = 1
        while "game-" + str(self.current_game) in self.data:
            self.current_game += 1
        self.game = "game-" + str(self.current_game)
        self.data[self.game] = {}
        self.create_default_holes()

    def create_new_game(self):
        self.current_game += 1
        self.game = "game-" + str(self.current_game)
        self.data[self.game] = {}
        self.create_default_holes()

    def add_score(self, h, score):
        hole = "hole-" + str(h)
        if h == 1:
            self.data[self.game][hole]["Genevieve"] = score[0]
            self.data[self.game][hole]["Alexander"] = score[1]
        else:
            previous_hole = "hole-" + str(h - 1)
            g_score = self.data[self.game][previous_hole]["Genevieve"]
            a_score = self.data[self.game][previous_hole]["Alexander"]
            self.data[self.game][hole]["Genevieve"] = g_score + score[0]
            self.data[self.game][hole]["Alexander"] = a_score + score[1]
        self.update()

    def get_score(self, h):
        hole = "hole-" + str(h)
        return self.data[self.game][hole]["Genevieve"], self.data[self.game][hole]["Alexander"]

    def update(self):
        with open("game-data.yml", 'w') as file:
            file.write(yaml.safe_dump(self.data))
        with open("game-data.yml", 'r') as file:
            self.data = yaml.safe_load(file)

    def get_winner(self):
        score = self.data[self.game]["hole-9"]
        g_score = score["Genevieve"]
        a_score = score["Alexander"]
        if g_score < a_score:
            winner = colored("Genevieve", "magenta")
        elif a_score < g_score:
            winner = colored("Alexander", "blue")
        else:
            winner = "Tied"
        self.data["wins"][winner] += 1
        self.update()
        return winner

    def get_wins(self):
        wins = self.data["wins"]
        return wins["Genevieve"], wins["Alexander"], wins["Tied"]

    def create_default_holes(self):
        for h in range(1, 10):
            self.data[self.game]["hole-" + str(h)] = {"Genevieve": 0, "Alexander": 0}
        self.update()

    def abort(self):
        del self.data[self.game]
        self.update()


def get_score():
    g_score = a_score = None
    while g_score is None:
        try:
            g_score = input(colored("\tGenevieve's", "magenta"), "Score: ").upper()
            if g_score == "EXIT" or g_score == "QUIT":
                return None
            g_score = int(g_score)
        except ValueError:
            g_score = None
            print(colored("Enter a number", "red"))
    while a_score is None:
        try:
            a_score = input(colored("\tAlexander's", "blue"), "Score: ").upper()
            if a_score == "EXIT" or a_score == "QUIT":
                return None
            a_score = int(a_score)
        except ValueError:
            a_score = None
            print(colored("Enter a number", "red"))
    return g_score, a_score


def game_over(data, h):
    winner = data.get_winner()
    g_wins, a_wins, ties = data.get_wins()
    print("No One" if winner == "Tied" else winner, "Wins!")
    print("Game Over")
    print()
    print(colored("Genevieve", "magenta"), "Has Won", g_wins, "Times")
    print(colored("Alexander", "blue"), "Has Won", a_wins, "Times")
    print("There Have Been", ties, "Ties")
    print()
    again = input("Play Again? (Y/N) ").upper()
    if again == "Y":
        data.create_new_game()
        h = 1
    return h


def git_push(repo):
    repo.git.add(update=True)
    repo.index.commit("Commit From Python")
    origin = repo.remote(name="origin")
    origin.push()


def play(data, h):
    print("Hole", h)
    score = get_score()
    if score is None:
        print("Exiting")
        data.abort()
        return 11
    data.add_score(h, score)
    score = data.get_score(h)
    print("\tThe Score Is:")
    print(colored("\t\tGenevieve", "magenta"), "-", score[0])
    print(colored("\t\tAlexander", "blue"), "-", score[1])
    return h + 1


def start():
    repo = Repo(".git")
    repo.git.pull()
    return GameData(), 1, repo


def main():
    data, h, repo = start()
    try:
        while h < 10:
            h = play(data, h)
            if h == 10:
                h = game_over(data, h)
    except Exception as e:
        print(e)
        data.abort()
    git_push(repo)


if __name__ == "__main__":
    main()

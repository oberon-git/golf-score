import os
import yaml
from git import Repo


class GameData:
    def __init__(self):
        if not os.path.exists("../game-data.yml"):
            open("../game-data.yml", 'w').close()
            self.data = {}
        else:
            with open("../game-data.yml", 'r') as file:
                self.data = yaml.safe_load(file)
        if "wins" not in self.data:
            self.data["wins"] = {"Genevieve": 0, "Alexander": 0, "Tied": 0}
        self.current_game = 1
        while "game-" + str(self.current_game) in self.data:
            self.current_game += 1
        game = "game-" + str(self.current_game)
        self.data[game] = {}
        self.create_default_holes()

    def create_new_game(self):
        self.current_game += 1
        game = "game-" + str(self.current_game)
        self.data[game] = {}
        self.create_default_holes()

    def add_score(self, h, score):
        game = "game-" + str(self.current_game)
        hole = "hole-" + str(h)
        if h == 1:
            self.data[game][hole]["Genevieve"] = score[0]
            self.data[game][hole]["Alexander"] = score[1]
        else:
            previous_hole = "hole-" + str(h - 1)
            g_score = self.data[game][previous_hole]["Genevieve"]
            a_score = self.data[game][previous_hole]["Alexander"]
            self.data[game][hole]["Genevieve"] = g_score + score[0]
            self.data[game][hole]["Alexander"] = a_score + score[1]
        self.update()

    def get_score(self, h):
        game = "game-" + str(self.current_game)
        hole = "hole-" + str(h)
        return self.data[game][hole]["Genevieve"], self.data[game][hole]["Alexander"]

    def update(self):
        with open("../game-data.yml", 'w') as file:
            file.write(yaml.safe_dump(self.data))
        with open("../game-data.yml", 'r') as file:
            self.data = yaml.safe_load(file)

    def get_winner(self):
        game = "game-" + str(self.current_game)
        score = self.data[game]["hole-9"]
        g_score = score["Genevieve"]
        a_score = score["Alexander"]
        if g_score < a_score:
            winner = "Genevieve"
        elif a_score < g_score:
            winner = "Alexander"
        else:
            winner = "Tied"
        self.data["wins"][winner] += 1
        self.update()
        return winner

    def get_wins(self):
        wins = self.data["wins"]
        return wins["Genevieve"], wins["Alexander"], wins["Tied"]

    def create_default_holes(self):
        game = "game-" + str(self.current_game)
        for h in range(1, 10):
            self.data[game]["hole-" + str(h)] = {"Genevieve": 0, "Alexander": 0}
        self.update()


def get_score():
    g_score = a_score = None
    while g_score is None:
        try:
            g_score = int(input("\tGenevieve's Score: "))
        except ValueError:
            g_score = None
            print("Enter a number")
    while a_score is None:
        try:
            a_score = int(input("\tAlexander's Score: "))
        except ValueError:
            a_score = None
            print("Enter a number")
    return g_score, a_score


def game_over(data, h, repo):
    winner = data.get_winner()
    g_wins, a_wins, ties = data.get_wins()
    print("No One" if winner == "Tied" else winner, "Wins!")
    print("Game Over")
    print()
    print("Genevieve Has Won", g_wins, "Times")
    print("Alexander Has Won", a_wins, "Times")
    print("There Have Been", ties, "Ties")
    print()
    again = input("Play Again? (Y/N) ").upper()
    if again == "Y":
        data.create_new_game()
        h = 1
    git_push(repo)
    return h


def git_push(repo):
    repo.git.add(update=True)
    repo.index.commit("Commit From Python")
    origin = repo.remote(name="origin")
    origin.push()


def play(data, h):
    print("Hole", h)
    data.add_score(h, get_score())
    score = data.get_score(h)
    print("\tThe Score Is:")
    print("\t\tGenevieve -", score[0])
    print("\t\tAlexander -", score[1])
    return h + 1


def start():
    return GameData(), 1, Repo("/Local Files/Repos/golf-score/.git")


def main():
    data, h, repo = start()
    while h < 10:
        h = play(data, h)
        if h == 10:
            h = game_over(data, h, repo)


if __name__ == "__main__":
    main()


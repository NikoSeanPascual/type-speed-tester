import time

player = {
    "name": "",
    "hp": 20,
    "attack": 5,
    "defence": 2,
    "inventory": [],
    "max_hp": 20
}

goblin_enemy = {
    "name": "Goblin",
    "hp": 15,
    "attack": 4,
    "defence": 1,
    "rewards": {
        "hp": 5,
        "attack": 1,
        "defence": 1
    },
    "death_text": "\nThe goblin stole the little you have while you slowly bleed out"
}


def slow_print(text, delay=0.02):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def battle(player, goblin_enemy):
    slow_print(f"\nA {goblin_enemy['name']} appears!")

    while player['hp'] > 0 and goblin_enemy['hp'] > 0:
        slow_print(f"\n{player['name']} HP: {player['hp']} | {goblin_enemy['name']} HP: {goblin_enemy['hp']}")
        action = input("Choose: [1] Attack [2] Heal [3] Guard [4] Flee: ").strip()

        if action == "1":
            damage = max(player['attack'] - goblin_enemy['defence'], 0)
            goblin_enemy['hp'] -= damage
            slow_print(f"You deal {damage} damage.")

        elif action == "2":
            heal = 5
            player['hp'] += heal
            slow_print(f"You heal {heal} HP.")

        elif action == "3":
            slow_print("You guard yourself, reducing incoming damage.")

        elif action == "4":
            slow_print("You fled the battle!")
            return False

        else:
            slow_print("Invalid action.")

        if goblin_enemy['hp'] <= 0:
            if "rewards" in goblin_enemy:
                r = goblin_enemy["rewards"]
                player["max_hp"] += r["hp"]
                player["hp"] = player["max_hp"]
                player["attack"] += r["attack"]
                player["defence"] += r["defence"]

            slow_print(f"You defeated {goblin_enemy['name']}!")
            return True

        damage = max(goblin_enemy['attack'] - player['defence'], 0)
        player['hp'] -= damage
        slow_print(f"{goblin_enemy['name']} hits you for {damage} damage.")

    if "death_text" in goblin_enemy:
        slow_print(goblin_enemy["death_text"])
    else:
        print("YOU DIED")

    return False


def left_route():
    slow_print("YOU FIND THE TREASURES LOL")
    slow_print("You have gained a magical sword!")


def right_route():
    slow_print("YOU FELL INTO A TRAP AND DIED")
    slow_print("You were ambushed by more goblins and you couldn't escape.")
    return "Game Over"


def game_end(ending):
    if ending == "Game Over":
        slow_print("\nGAME OVER!")
    elif ending == "neutral_ending":
        slow_print("\nYou walk away with a sense of unease...")
    else:
        slow_print(f"\nThe adventure ends with: {ending}")

    play_again = input("Do you want to play again? (yes/no): ").strip().lower()
    if play_again == "yes":
        start_game()
    else:
        slow_print("Thanks for playing! Goodbye!")


def story_branch():
    slow_print(
        "\nAfter the Goblin encounter you walk for a bit and stumble upon two pathways leading into the unknown.")
    choice = input("Do you go [1] Left or [2] Right? ").strip()

    if choice == "1":
        return left_route()
    elif choice == "2":
        return right_route()
    else:
        slow_print("Invalid choice. You stand there, unsure of which path to take.")
        return "neutral_ending"


def start_game():
    slow_print("WELCOME TO MINI RPG!\n")
    player['name'] = input("Enter your character's name: ").title().strip()

    won = battle(player, goblin_enemy)
    if not won:
        game_end("Game Over")
    else:
        ending = story_branch()
        game_end(ending)

start_game()

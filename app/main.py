from app.config.injection_dependency import get_gameplay_controller


def resister():
    print('Resistering...')
    # run flask app with register player and define strategy
    # close flask app


def game_loop():
    print('Game loop...')
    # run waiting mode showing register logging and start option
    # run game mode showing planets and civilizations
    # run rounds mode showing skirmishes and results
    # run end mode showing final results
    gameplay = get_gameplay_controller()
    gameplay.run()


if __name__ == '__main__':
    print('Starting app...')
    resister()
    game_loop()

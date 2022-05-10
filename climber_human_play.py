from climber_game import ClimberGame

cg = ClimberGame(max_gaps=1)
ClimberGame.main(cg)

while True:
    ClimberGame.render(cg)
    if ClimberGame.run_logic(cg, -1) >= 0:
        break



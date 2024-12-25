from random import choice

async def chooseGame():
    games = ["Deep Rock Galactic", "Control: Ultimate Edition",
    "Portal Reloaded", "Portal 2", "Team Fortress 2", "Risk of Rain 2", "Hitman 2",
    "Borderlands 2", "Borderlands: The Pre-Sequel",
    "Mini Motorways", "Alan Wake",
    "Dishonored 2", "Metro Exodus", "Blender", "Wolfenstein: The New Colossus", "Doom", "Doom Eternal",
    "Subnautica", "Subnautica: Below Zero", "Bioshock: Infinite",
    "Kerbal Space Program", "Nier Automata", "Guardians of the Galaxy", "Hades", "Bugsnax", "Kena: Bridge of Spirits",
    "Rise of the Tomb Raider", "Tomb Raider", "Mass Effect: Legendary Editon", "Elden Ring", "Dark Souls 3", "Dark Souls Remastered", 
    "Resident Evil II", "Horizon Zero Dawn", "Black Mesa", "Wallpaper Engine", "Risk of Rain",
    "Cyberpunk 2077", "Sea of Thieves", "The Witcher 3",
    "A Plague Tale: Requiem", "A Plague Tale: Innocence", "Black Mesa", "Metro Exodus",
    "Hitman", "Spiderman Remastered", "NieR Automata", "Borderlands GOTY", "Bloodborne",
    "Hogwarts Legacy", "Atomic Heart", "Don't Starve Together", "Bloodborne PC", "Risk of Rain Returns", "The Stanley Parable: Ultra Deluxe",
    "Slime Rancher 2", "Baldur's Gate 3", "A Plague Tale: Reqiuem", "Stray Gods: The Roleplaying Musical", "Powerwash Simulator",
    ]

    game_status = choice(games)
    return game_status
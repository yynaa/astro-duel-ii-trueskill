import dearpygui.dearpygui as dpg

from db import Player, Match, get_player, add_player, add_match, get_players_ranked, get_players, recalculate_all_ratings

def create_player_callback(sender, app_data):
    add_player(dpg.get_value("player_creator_name"))

def query_player_callback(sender, app_data):
    player = get_player(dpg.get_value("player_query_name"))
    if player:
        dpg.set_value("player_query_rating", "Rating: " + str(player.rating))
        dpg.set_value("player_query_deviation", "Deviation: " + str(player.deviation))
    else:
        dpg.set_value("player_query_rating", "Rating: ...")
        dpg.set_value("player_query_deviation", "Deviation: ...")

def match_add_callback(sender, app_data):
    if not dpg.get_value("match_creator_player1") or not dpg.get_value("match_creator_player2"):
        return

    add_match(dpg.get_value("match_creator_map"), dpg.get_value("match_creator_teams"),
            [dpg.get_value("match_creator_player1"), dpg.get_value("match_creator_player2"), dpg.get_value("match_creator_player3"), dpg.get_value("match_creator_player4")],
            [dpg.get_value("match_creator_rank1"), dpg.get_value("match_creator_rank2"), dpg.get_value("match_creator_rank3"), dpg.get_value("match_creator_rank4")])

def match_teams_callback(sender, app_data):
    if dpg.get_value("match_creator_teams"):
        dpg.configure_item("match_creator_rank3", enabled=False)
        dpg.configure_item("match_creator_rank4", enabled=False)
    else:
        dpg.configure_item("match_creator_rank3", enabled=True)
        dpg.configure_item("match_creator_rank4", enabled=True)

def refresh_leaderboard_callback(sender, app_data):
    players = get_players_ranked()
    for i in range(10):
        if i < len(players):
            player = get_player(players[i])
            dpg.set_value(f"player_leaderboard_{i+1}", f"{i+1}. {player.name} - {player.rating:.1f} ~ {player.deviation:.1f}")
        else:
            dpg.set_value(f"player_leaderboard_{i+1}", f"{i+1}. ...")

dpg.create_context()
dpg.create_viewport(title="Rating System", width=800, height=600)

with dpg.window(label="Astro Duel II - Trueskill", width=800, height=600, tag="main_window"):

    dpg.add_button(label="Regenerate Ratings", callback=recalculate_all_ratings)
    
    with dpg.collapsing_header(label="Player Management"):
        dpg.add_input_text(hint="Enter name here", tag="player_creator_name")
        dpg.add_button(label="Add", callback=create_player_callback)
    
    with dpg.collapsing_header(label="Player Query"):
        dpg.add_input_text(hint="Enter name here", tag="player_query_name")
        dpg.add_button(label="Query", callback=query_player_callback)

        dpg.add_text("Rating: ...", tag="player_query_rating")
        dpg.add_text("Deviation: ...", tag="player_query_deviation")
    
    with dpg.collapsing_header(label="Player Leaderboard"):
        dpg.add_text("1. ...", tag="player_leaderboard_1")
        dpg.add_text("2. ...", tag="player_leaderboard_2")
        dpg.add_text("3. ...", tag="player_leaderboard_3")
        dpg.add_text("4. ...", tag="player_leaderboard_4")
        dpg.add_text("5. ...", tag="player_leaderboard_5")
        dpg.add_text("6. ...", tag="player_leaderboard_6")
        dpg.add_text("7. ...", tag="player_leaderboard_7")
        dpg.add_text("8. ...", tag="player_leaderboard_8")
        dpg.add_text("9. ...", tag="player_leaderboard_9")
        dpg.add_text("10. ...", tag="player_leaderboard_10")

        dpg.add_button(label="Refresh", callback=refresh_leaderboard_callback)
    
    with dpg.collapsing_header(label="Match Management"):
        maps = ["Old Mines", "Highrise", "Frontier", "Dark Lab", "Echo City", "Flare Watch", "Sunken Temple", "Gas Rigs"]
        dpg.add_listbox(label="Players", items=maps, num_items=len(maps), tag="match_creator_map")

        dpg.add_checkbox(label="Teams", default_value=False, tag="match_creator_teams")

        dpg.add_input_text(hint="Enter player 1 / team blu player 1 name", tag="match_creator_player1")
        dpg.add_input_text(hint="Enter player 2 / team blu player 2 name", tag="match_creator_player2")
        dpg.add_input_text(hint="Enter player 3 / team red player 1 name", tag="match_creator_player3")
        dpg.add_input_text(hint="Enter player 4 / team red player 2 name", tag="match_creator_player4")
        dpg.add_slider_int(label="Enter player 1 / team blu rank", tag="match_creator_rank1", min_value=1, max_value=4, default_value=1)
        dpg.add_slider_int(label="Enter player 2 / team red rank", tag="match_creator_rank2", min_value=1, max_value=4, default_value=1)
        dpg.add_slider_int(label="Enter player 3 rank", tag="match_creator_rank3", min_value=1, max_value=4, default_value=1)
        dpg.add_slider_int(label="Enter player 4 rank", tag="match_creator_rank4", min_value=1, max_value=4, default_value=1)

        dpg.add_button(label="Add Match", callback=match_add_callback)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
class TeamGameCalculator:
  def __init__(self, team_game):
    self.team_game = team_game
    if "field_goals_attempted" in self.team_game.keys():
      self._set_variables()

  def prepare_team_game(self):
    if "field_goals_attempted" in self.team_game.keys():
      self._calculate_field_goal_percentages()
      self._estimate_possessions()
      self._calculate_efficiencies()
      self._calculate_assist_rates()
      self._calculate_rebound_rates()
      self._calculate_three_point_proficiencies()

    return self.team_game

  def _set_variables(self):
    self.points                   = float(self.team_game["points"])
    self.points_allowed           = float(self.team_game["points_allowed"])
    self.assists                  = float(self.team_game["assists"])
    self.field_goals_made         = float(self.team_game["field_goals_made"])
    self.field_goals_attempted    = float(self.team_game["field_goals_attempted"])
    self.free_throws_made         = float(self.team_game["free_throws_made"])
    self.free_throws_attempted    = float(self.team_game["free_throws_attempted"])
    self.three_pointers_made      = float(self.team_game["three_pointers_made"])
    self.three_pointers_attempted = float(self.team_game["three_pointers_attempted"])
    self.offensive_rebounds       = float(self.team_game["offensive_rebounds"])
    self.defensive_rebounds       = float(self.team_game["defensive_rebounds"])
    self.turnovers                = float(self.team_game["turnovers"])
    self.opponent_game_present    = False

    if "opponent_game" in self.team_game.keys():
      self.opponent_game_present             = True
      self.opponent_assists                  = float(self.team_game["opponent_game"]["assists"])
      self.opponent_field_goals_made         = float(self.team_game["opponent_game"]["field_goals_made"])
      self.opponent_field_goals_attempted    = float(self.team_game["opponent_game"]["field_goals_attempted"])
      self.opponent_free_throws_made         = float(self.team_game["opponent_game"]["free_throws_made"])
      self.opponent_free_throws_attempted    = float(self.team_game["opponent_game"]["free_throws_attempted"])
      self.opponent_three_pointers_made      = float(self.team_game["opponent_game"]["three_pointers_made"])
      self.opponent_three_pointers_attempted = float(self.team_game["opponent_game"]["three_pointers_attempted"])
      self.opponent_offensive_rebounds       = float(self.team_game["opponent_game"]["offensive_rebounds"])
      self.opponent_defensive_rebounds       = float(self.team_game["opponent_game"]["defensive_rebounds"])
      self.opponent_turnovers                = float(self.team_game["opponent_game"]["turnovers"])

  def _calculate_field_goal_percentages(self):
    self.team_game["field_goal_percentage"] = ( 100.0 *
      self.field_goals_made / self.field_goals_attempted )
    self.team_game["three_point_percentage"] = ( 100.0 *
      self.three_pointers_made / self.three_pointers_attempted )
    self.team_game["free_throw_percentage"] = ( 100.0 *
      self.free_throws_made  / self.free_throws_attempted )

  def _estimate_possessions(self):
    team_possessions = ((self.field_goals_attempted - self.offensive_rebounds)
      + self.turnovers + (0.44 * self.free_throws_attempted))

    if self.opponent_game_present:
      opponent_possessions = ((self.opponent_field_goals_attempted - self.opponent_offensive_rebounds)
        + self.opponent_turnovers + (0.44 * self.opponent_free_throws_attempted))
    else:
      opponent_possessions = team_possessions

    self.possessions = (opponent_possessions + team_possessions) / 2.0
    self.team_game["possessions"] = self.possessions

  def _calculate_efficiencies(self):
    self.team_game["offensive_efficiency"] = 100.0 * (self.points / self.possessions)
    self.team_game["defensive_efficiency"] = 100.0 * (self.points_allowed / self.possessions)

  def _calculate_assist_rates(self):
    self.team_game["assist_rate"] = 100.0 * (self.assists / self.field_goals_made)
    if self.opponent_game_present:
      self.team_game["allowed_assist_rate"] = 100 * (self.opponent_assists / self.opponent_field_goals_made)

  def _calculate_rebound_rates(self):
    if self.opponent_game_present:
      self.team_game["offensive_rebound_rate"] = self.offensive_rebounds / (
        self.offensive_rebounds + self.opponent_defensive_rebounds)
      self.team_game["defensive_rebound_rate"] = self.defensive_rebounds / (
        self.opponent_offensive_rebounds + self.defensive_rebounds)

  # This method uses 3P% and 3PT rate to calculate an overall 3PT Proficiency based on a weight constant
  def _calculate_three_point_proficiencies(self):
    # PERCENTAGE_WEIGHT is amount of weight to give to 3P% vs 3PA/FGA
    PERCENTAGE_WEIGHT = 0.7

    self.team_game["three_point_proficiency"] = ( 100.0 *
      PERCENTAGE_WEIGHT * (self.three_pointers_made / self.three_pointers_attempted)) + (
      (1.0 - PERCENTAGE_WEIGHT) * (self.three_pointers_attempted / self.field_goals_attempted))

    if self.opponent_game_present:
      self.team_game["allowed_three_point_proficiency"] = ( 100.0 *
        PERCENTAGE_WEIGHT * (self.opponent_three_pointers_made / self.opponent_three_pointers_attempted)) + (
        (1.0 - PERCENTAGE_WEIGHT) * (self.opponent_three_pointers_attempted / self.opponent_field_goals_attempted))
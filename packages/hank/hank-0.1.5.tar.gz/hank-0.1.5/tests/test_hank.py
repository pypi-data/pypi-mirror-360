"""Tests for the Hank class functionality."""

import pandas as pd

from hank import Hank


def test_greet():
    """Test that Hank greets correctly with name, age, and favorite toy."""
    h = Hank(name="Buddy", age=5, favorite_toy="Frisbee")
    assert h.greet() == "Hi! I'm Buddy, a 5-year-old good boy who loves Frisbee!"


def test_bark():
    """Test that Hank barks correctly."""
    h = Hank()
    assert h.bark() == "Woof! 🐾"


def test_fetch_with_custom_toy():
    """Test that Hank fetches a specified toy correctly."""
    h = Hank()
    assert h.fetch("stick") == "Hank fetches the stick and brings it back to you!"


def test_sleep():
    """Test that Hank's sleep message is correct."""
    h = Hank(name="Hank")
    assert h.sleep() == "Hank is now sleeping peacefully. Zzz... 💤"


def test_initial_treat_log_is_empty():
    """Test that the initial treat log is empty and returns appropriate message."""
    h = Hank()
    assert h.treat_log.empty
    assert h.get_treat_log() == "No treats have been given yet."


def test_give_hank_treat_adds_row():
    """Test that giving Hank a treat adds a row to the treat log."""
    h = Hank()
    h.give_hank_treat("bacon", 2)

    log = h.get_treat_log()
    assert isinstance(log, pd.DataFrame)
    assert len(log) == 1
    assert log.iloc[0]["treat_name"] == "bacon"
    assert log.iloc[0]["num_treats"] == 2


def test_multiple_treats_logged_correctly():
    """Test that multiple treats are logged correctly in order."""
    h = Hank()
    h.give_hank_treat("bacon", 1)
    h.give_hank_treat("bone", 3)

    log = h.get_treat_log()
    assert len(log) == 2
    assert log["treat_name"].tolist() == ["bacon", "bone"]

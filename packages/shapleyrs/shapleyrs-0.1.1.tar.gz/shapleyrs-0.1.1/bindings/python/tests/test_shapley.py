import pytest
from shapleyrs import Shapley


def test_empty_coalition_handling():
    """Test that empty coalition is automatically added with value 0.0"""
    players = [1]
    coalition_worth = {
        (1,): 5.0,
    }
    shapley = Shapley(players, coalition_worth)
    # The empty coalition should be automatically added
    # We can verify this by checking that the calculation works
    assert shapley.shapley_value(1) == 5.0


def test_missing_data():
    """Test that missing coalition data raises an error"""
    players = [1, 2]
    coalition_worth = {
        (1, 2): 10.0,
    }
    shapley = Shapley(players, coalition_worth)
    # Should raise an error due to missing coalition data
    with pytest.raises(ValueError):
        shapley.shapley_value(1)


def test_simple_shapley_value():
    """Test simple 2-player game"""
    players = [1, 2]
    coalition_worth = {
        (): 0.0,
        (1,): 10.0,
        (2,): 20.0,
        (1, 2): 30.0,
    }
    shapley = Shapley(players, coalition_worth)
    
    assert shapley.shapley_value(1) == 10.0
    assert shapley.shapley_value(2) == 20.0


def test_divide_dollar_game():
    """Test the Divide the Dollar Game from the literature"""
    # https://gtl.csa.iisc.ac.in/gametheory/ln/web-cp5-shapley.pdf
    # 2.1 Example 1: Divide the Dollar Game
    players = [1, 2, 3]
    coalition_worth = {
        (1,): 0.0,
        (2,): 0.0,
        (3,): 0.0,
        (2, 3): 0.0,
        (1, 2): 300.0,
        (1, 3): 300.0,
        (1, 2, 3): 300.0,
    }
    shapley = Shapley(players, coalition_worth)
    
    # Expected values from the literature
    assert shapley.shapley_value(1) == pytest.approx(200.0, rel=1e-10)
    assert shapley.shapley_value(2) == pytest.approx(50.0, rel=1e-10)
    assert shapley.shapley_value(3) == pytest.approx(50.0, rel=1e-10)


def test_logistics_game():
    """Test the Logistics Game from the literature"""
    # https://gtl.csa.iisc.ac.in/gametheory/ln/web-cp5-shapley.pdf
    # 2.4 Example 4: A Logistics Game
    players = [1, 2, 3, 4]
    coalition_worth = {
        (1,): 0.0,
        (2,): 0.0,
        (3,): 0.0,
        (4,): 0.0,
        (1, 2): 0.0,
        (1, 3): 0.0,
        (1, 4): 0.0,
        (2, 3): 0.0,
        (2, 4): 0.0,
        (3, 4): 0.0,
        (1, 2, 3): 0.0,
        (2, 3, 4): 0.0,
        (1, 2, 4): 45.0,
        (1, 3, 4): 40.0,
        (1, 2, 3, 4): 65.0,
    }
    shapley = Shapley(players, coalition_worth)
    
    # Expected values from the literature
    assert shapley.shapley_value(1) == pytest.approx(23.333333333333332, rel=1e-10)
    assert shapley.shapley_value(2) == pytest.approx(10.0, rel=1e-10)
    assert shapley.shapley_value(3) == pytest.approx(8.333333333333332, rel=1e-10)
    assert shapley.shapley_value(4) == pytest.approx(23.333333333333332, rel=1e-10)


def test_symmetric_game():
    """Test a symmetric game where all players contribute equally"""
    players = [1, 2, 3]
    coalition_worth = {
        (): 0.0,
        (1,): 10.0,
        (2,): 10.0,
        (3,): 10.0,
        (1, 2): 20.0,
        (1, 3): 20.0,
        (2, 3): 20.0,
        (1, 2, 3): 30.0,
    }
    shapley = Shapley(players, coalition_worth)
    
    # In a symmetric game, all players should have equal Shapley values
    value1 = shapley.shapley_value(1)
    value2 = shapley.shapley_value(2)
    value3 = shapley.shapley_value(3)
    
    assert value1 == pytest.approx(value2, rel=1e-10)
    assert value2 == pytest.approx(value3, rel=1e-10)
    assert value1 == pytest.approx(value3, rel=1e-10)


def test_zero_sum_game():
    """Test a zero-sum game where total value is always zero"""
    players = [1, 2]
    coalition_worth = {
        (): 0.0,
        (1,): 5.0,
        (2,): -5.0,
        (1, 2): 0.0,
    }
    shapley = Shapley(players, coalition_worth)
    
    value1 = shapley.shapley_value(1)
    value2 = shapley.shapley_value(2)
    
    # Shapley values should sum to the grand coalition value
    assert (value1 + value2) == pytest.approx(0.0, rel=1e-10)


def test_single_player_game():
    """Test edge case with only one player"""
    players = [1]
    coalition_worth = {
        (): 0.0,
        (1,): 100.0,
    }
    shapley = Shapley(players, coalition_worth)
    
    assert shapley.shapley_value(1) == 100.0


def test_invalid_player():
    """Test that requesting Shapley value for non-existent player raises error"""
    players = [1, 2]
    coalition_worth = {
        (): 0.0,
        (1,): 10.0,
        (2,): 20.0,
        (1, 2): 30.0,
    }
    shapley = Shapley(players, coalition_worth)
    
    # This should work fine since player 3 is not in the game
    # The function will return an error due to missing coalition data
    with pytest.raises(ValueError):
        shapley.shapley_value(3)

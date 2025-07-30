"""Defines the Hank class representing a lovable dog."""

import random

import numpy as np
import pandas as pd


class Hank:
    """A class to model a dog named Hank."""

    def __init__(self, name="Hank", age=3, favorite_toy="ball"):
        """
        Initialize the Hank dog with basic attributes.

        Args:
            name (str): The dog's name.
            age (int): The dog's age in years.
            favorite_toy (str): The dog's favorite toy.
        """
        self.name = name
        self.age = age
        self.favorite_toy = favorite_toy
        self.treat_log = pd.DataFrame(columns=["treat_name", "num_treats", "timestamp"])

    def greet(self):
        """
        Generate a greeting string for Hank.

        Returns:
            str: A greeting message including name, age, and favorite toy.
        """
        return f"Hi! I'm {self.name}, a {self.age}-year-old good boy who loves {self.favorite_toy}!"

    def bark(self):
        """
        Make Hank bark.

        Returns:
            str: Barking sound.
        """
        return "Woof! 🐾"

    def random_fact(self):
        """
        Return a random fun fact about Hank.

        Returns:
            str: A fun fact string.
        """
        facts = [
            f"{self.name} loves peanut butter.",
            f"{self.name} knows how to sit, stay, and high five!",
            f"{self.name} is a very good boy.",
            f"{self.name} once chased 3 squirrels in 5 minutes.",
        ]
        return random.choice(facts)

    def fetch(self, toy=None):
        """
        Simulate Hank fetching a toy.

        Args:
            toy (str, optional): The toy to fetch. Defaults to favorite_toy.

        Returns:
            str: Description of fetching behavior.
        """
        if toy is None:
            toy = self.favorite_toy
        return f"{self.name} fetches the {toy} and brings it back to you!"

    def sleep(self):
        """
        Simulate Hank sleeping.

        Returns:
            str: Description of Hank sleeping.
        """
        return f"{self.name} is now sleeping peacefully. Zzz... 💤"

    def give_hank_treat(self, treat="dog biscuit", num_treats=1):
        """
        Give Hank a treat and log it.

        Args:
            treat (str): Name of the treat.
            num_treats (int): Number of treats given.

        Returns:
            str: Confirmation message.
        """
        treat_log = {
            "treat_name": treat,
            "num_treats": num_treats,
            "timestamp": np.datetime64("now", "s"),
        }

        df = pd.DataFrame([treat_log])
        self.treat_log = pd.concat([self.treat_log, df], ignore_index=True)

        return f"{self.name} happily accepts a {treat} and wags his tail! 🐶"

    def get_treat_log(self):
        """
        Retrieve the treat log for Hank.

        Returns:
            pd.DataFrame or str: The treat log DataFrame or a message if empty.
        """
        if self.treat_log.empty:
            return "No treats have been given yet."
        else:
            return self.treat_log

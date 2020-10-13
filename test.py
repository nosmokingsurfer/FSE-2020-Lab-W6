#!/usr/bin/env python3

import covid_simulation as cs
import unittest
from random import randint

def generator_randomized_persons(n_persons, infect_flag=False):
    min_i, max_i = 0, 100
    min_j, max_j = 0, 100

    factory_params = (min_j, max_j, min_i, max_i)

    default_factory = cs.DefaultPersonFactory(*factory_params)
    community_factory = cs.CommunityPersonFactory(*factory_params, community_position=(50, 50))

    n_default_persons = int(n_persons * 0.75)
    n_community_persons = n_persons - n_default_persons

    persons = []
    for i in range(n_default_persons):
        persons.append(default_factory.get_person())

    for i in range(n_community_persons):
        persons.append(community_factory.get_person())

    if infect_flag:
        infected_n_persons = int(0.5 * n_persons)
        for person in persons[:infected_n_persons]:
            person.get_infected(cs.get_infectable(cs.InfectableType(randint(1, 3))))

    return persons


class GettingInfectedTestCase(unittest.TestCase):

    def setUp(self):
        self.persons = []
        self.persons = generator_randomized_persons(2, infect_flag=True)

    def test_healthy_contact(self):

        for _ in range(1):
            self.persons[0].interact(self.persons[1])
            self.persons[1].interact(self.persons[0])

        self.assertIsInstance(self.persons[1].state, cs.AsymptomaticSick)

    def tearDown(self):
        del self.persons


class HealthyContactTestCase(unittest.TestCase):

    def setUp(self):
        self.persons = []
        self.persons = generator_randomized_persons(2)

    def test_healthy_contact(self):

        for _ in range(1):
            self.persons[0].interact(self.persons[1])
            self.persons[1].interact(self.persons[0])

        self.assertIsInstance(self.persons[0].state, cs.Healthy)
        self.assertIsInstance(self.persons[0].state, cs.Healthy)

    def tearDown(self):
        del self.persons


if __name__ == "__main__":
    unittest.main()
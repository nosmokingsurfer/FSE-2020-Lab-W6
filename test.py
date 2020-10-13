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


# 1. Persons should be able to transmit infections when infected (without symptoms or with symptoms), 
# meaning that other Persons shall be able to get infected (change their health state from healthy to 
# infected (without symptoms) when contacted by a person with a virus).
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


# 2. When a healthy person is contacting another healthy person, their health conditions should not change.
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


# 3. When an infected person is contacting a person with antibodies, the latter shall not change health state,
# if his antibodies have the same type as the virus.
class InfectedContactsAntibodies_1(unittest.TestCase):

    def setUp(self):
        self.persons = generator_randomized_persons(3)

        # first person already recovered from SARSCoV2
        self.persons[0].get_infected(cs.get_infectable(cs.InfectableType.SARSCoV2))
        self.persons[0].go_to_normal()

        # second person is infected by SARSCoV2
        self.persons[1].get_infected(cs.get_infectable(cs.InfectableType.SARSCoV2))

        # third person is infected bu SeasonalFlue
        self.persons[2].get_infected(cs.get_infectable(cs.InfectableType.SeasonalFlu))
        
    def tearDown(self):
        del self.persons

    def test(self):
        # first and second person interacting - state should not change
        before = self.persons[0].state
        self.persons[0].interact(self.persons[1])
        self.persons[1].interact(self.persons[0])
        after = self.persons[0].state
        self.assertEqual(before, after)

        # first and third person interacting - state should change
        before = self.persons[0].state
        self.persons[0].interact(self.persons[2])
        self.persons[2].interact(self.persons[0])
        after = self.persons[0].state
        self.assertNotEqual(before, after)


# 4. A person shall change his health state from infected (without symptoms) to infected (with symptoms), 
# after being infected for 2 days.
class DAYS_SICK_TO_FEEL_BAD_test(unittest.TestCase):
    def setUp(self):
        self.person = generator_randomized_persons(1)[0]
        self.person.get_infected(cs.get_infectable(cs.InfectableType.SeasonalFlu))

    def tearDown(self):
        del self.person

    def test(self):
        self.assertIsInstance(self.person.state, cs.AsymptomaticSick)

        self.person.day_actions()
        self.person.night_actions()

        self.person.day_actions()
        self.person.night_actions()

        self.assertIsInstance(self.person.state,cs.SymptomaticSick)


if __name__ == "__main__":
    unittest.main()
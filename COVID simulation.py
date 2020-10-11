from enum import Enum
from random import expovariate
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt

from typing import List
from random import randint

import pandas as pd

import tqdm


min_i, max_i = 0, 100
min_j, max_j = 0, 100

class Person: pass

class Infectable(ABC):
    def __init__(self, strength=1.5, contag=1.0):
        # contag is for contagiousness so we have less typos
        self.strength = strength
        self.contag = contag

    @abstractmethod
    def cause_symptoms(self, person: Person):
        pass

    @abstractmethod
    def get_type(self):
        pass

class SeasonalFluVirus(Infectable):
    def cause_symptoms(self, person: Person):
        person.temperature += 0.3
    
    def get_type(self):
        return InfectableType.SeasonalFlu
    
class SARSCoV2(Infectable):
    def cause_symptoms(self, person: Person):
        person.temperature += 0.5
    
    def get_type(self):
        return InfectableType.SARSCoV2
    
class Cholera(Infectable):
    def cause_symptoms(self, person: Person):
        person.temperature += 0.2
        person.water -= 1.0
    
    def get_type(self):
        return InfectableType.Cholera


class InfectableType(Enum):
    SeasonalFlu = 1
    SARSCoV2 = 2
    Cholera = 3

    
def get_infectable(infectable_type: InfectableType):
    if InfectableType.SeasonalFlu == infectable_type:
        return SeasonalFluVirus(strength=expovariate(10.0), contag=expovariate(10.0))
    
    elif InfectableType.SARSCoV2 == infectable_type:
        return SARSCoV2(strength=expovariate(2.0), contag=expovariate(2.0))
    
    elif InfectableType.Cholera == infectable_type:
        return Cholera(strength=expovariate(2.0), contag=expovariate(2.0))
    
    else:
        raise ValueError()


class Person:
    MAX_TEMPERATURE_TO_SURVIVE = 44.0
    LOWEST_WATER_PCT_TO_SURVIVE = 0.4
    
    LIFE_THREATENING_TEMPERATURE = 40.0
    LIFE_THREATENING_WATER_PCT = 0.5
    
    def __init__(self, home_position=(0, 0), age=30, weight=70):
        self.virus = None
        self.antibody_types = set()
        self.temperature = 36.6
        self.weight = weight
        self.water = 0.6 * self.weight
        self.age = age
        self.home_position = home_position
        self.position = home_position
        self.state = Healthy(self)

        # bools for stats


        self.infected = False
        self.hospitalized = False
        self.dead = False
        self.recovered = False

    
    def day_actions(self):
        self.state.day_actions()

    def night_actions(self):
        self.state.night_actions()

    def interact(self, other):
        self.state.interact(other)

    def attach(self, obs):
        self.observer = obs

    def update(self):
        flags = [self.infected, self.hospitalized, self.dead, self.recovered, len(self.antibody_types) > 0]
        self.observer.update([int(x) for x in flags])

    def get_infected(self, virus):
        self.state.get_infected(virus)
    
    def go_to_hospital(self):
        self.hospitalized = True
    
    def go_to_normal(self):
        self.recovered = True
        self.temperature = 36.6
        self.water = self.weight*0.6

    
    def is_close_to(self, other):
        return self.position == other.position
    
    def fightvirus(self):
        if self.virus:
            self.virus.strength -= (3.0 / self.age)
        
    def progress_disease(self):
        if self.virus:
            self.virus.cause_symptoms(self)

    def set_state(self, state):
        self.state = state
    
    def is_life_threatening_condition(self):
        return self.temperature >= Person.LIFE_THREATENING_TEMPERATURE or \
            self.water / self.weight <= Person.LIFE_THREATENING_WATER_PCT
    
    def is_life_incompatible_condition(self):        
        return self.temperature >= Person.MAX_TEMPERATURE_TO_SURVIVE or \
            self.water / self.weight <= Person.LOWEST_WATER_PCT_TO_SURVIVE


class DefaultPerson(Person):
    def day_actions(self):
        self.position = (randint(min_j, max_j), randint(min_i, max_i))
        self.state.day_actions()


class CommunityPerson(Person):
    def __init__(self, community_position=(0, 0), **kwargs):
        super().__init__(**kwargs)
        self.community_position = community_position
        
    def day_actions(self):
        self.position = self.community_position
        self.state.day_actions()

class AbstractPersonFactory(ABC):
    def __init__(self, *context):
        self.min_age, self.max_age = 1, 90
        self.min_weight, self.max_weight = 30, 120
        self.min_j, self.max_j, self.min_i, self.max_i = context

    @abstractmethod
    def get_person(self) -> Person:
        pass

    
class DefaultPersonFactory(AbstractPersonFactory):
    def __init__(self, *args):
        super().__init__(*args[:4])

    def get_person(self) -> Person:
        return DefaultPerson(
            home_position=(randint(self.min_j, self.max_j), randint(self.min_i, self.max_i)),
            age=randint(self.min_age, self.max_age),
            weight=randint(self.min_weight, self.max_weight),
        )


class CommunityPersonFactory(AbstractPersonFactory):
    def __init__(self, *args, community_position=(0, 0)):
        super().__init__(*args)
        self.community_position = community_position

    def get_person(self) -> Person:
        return CommunityPerson(
            home_position=(randint(self.min_j, self.max_j), randint(self.min_i, self.max_i)),
            age=randint(self.min_age, self.max_age),
            weight=randint(self.min_weight, self.max_weight),
            community_position=self.community_position
        )

class Hospital:
    def __init__(self, capacity, drug_repository):
        self.drug_repository = drug_repository
        self.capacity = capacity
        
    def _treat_patient(self, patient):
        # 1. identify disease
        if patient.virus is not None:
            disease_type = patient.virus.get_type()

        # 2. understand dose
        if patient.temperature >=40:
            antifever_dose = 2.0
            antivirus_dose = 2.0
        else:
            antifever_dose = 0.0
            antivirus_dose = 1.0
        
        if patient.water <= (patient.weight*0.6):
            rehydration_dose = 1.0
        else:
            rehydration_dose = 0.5
        


        
        prescription_method = get_prescription_method(disease_type, self.drug_repository, antifever_dose, antivirus_dose, rehydration_dose)
        
        
        # 3. compose treatment
        prescription_drugs = prescription_method.create_prescription()
        
        # 4. apply treatment
        for drug in prescription_drugs:
            drug.apply(patient)

        if patient.virus.strength <= 0:
            patient.go_to_normal()
            patient.hospitalized = False
            patient.set_state(Healthy(patient))
            patient.antibody_types.add(patient.virus.get_type())
            patient.recovered  =True
            patient.virus=None
            self.capacity += 1

    def treat_patients(self, patients):
        for patient in patients:
            if patient.hospitalized:
                self._treat_patient(patient)


class DepartmentOfHealth:
    def __init__(self, hospitals = 0):
        if hospitals != 0:
            self.hospitals = hospitals

            self.buffer = [0,0,0,0,0]

            self.data = pd.DataFrame(columns = ["Infected", "Hospitalized", "Deaths", "Recoveries", "With antibodies"])
            

    
    def hospitalize(self, person: Person):
        for hosp in self.hospitals:
            if hosp.capacity > 0:
                person.go_to_hospital()
                hosp.capacity -= 1
                break
        
    
    def make_policy(self):
        pass


    def update(self, data):
        self.buffer = [sum(x) for x in zip(self.buffer,data)]

    def end_day(self):
        self.data.loc[len(self.data)] = self.buffer
        
        self.buffer = [0,0,0,0,0]

    
    __instance = None
    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance


class GlobalContext:
    def __init__(self, canvas, persons, health_dept):
        self.canvas = canvas
        self.persons = persons
        self.health_dept = health_dept
        
    __instance = None
    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

def simulate_day(context):
    persons, health_dept, hospitals = context.persons, context.health_dept, context.health_dept.hospitals

    health_dept.make_policy()
    
    for hospital in hospitals:
        #print('Treating patients')
        hospital.treat_patients(persons)
    
    for person in persons:
        #print("Day actions")
        person.day_actions()
    
    for person in persons:
        for other in persons:
            if person is not other and person.is_close_to(other):
                person.interact(other)
                
    for person in persons:
        person.night_actions()

    # sending information to HealthDepartment
    for person in persons:
        person.update()
    
    # department finishes workday and calculates all statistics
    health_dept.end_day()




def create_persons(min_j, max_j, min_i, max_i, n_persons):
    factory_params = (min_j,max_j,min_i,max_i)
    
    default_factory = DefaultPersonFactory(*factory_params)
    community_factory = CommunityPersonFactory(*factory_params, community_position=(50, 50))

    n_default_persons = int(n_persons * 0.75)
    n_community_persons = n_persons - n_default_persons

    persons = []
    for i in range(n_default_persons):
        persons.append(default_factory.get_person())
        
    for i in range(n_community_persons):
        persons.append(community_factory.get_person())

    for person in persons[:40]:
        person.get_infected(Cholera())

    for person in persons[40:80]:
        person.get_infected(SARSCoV2())

    return persons


def create_department_of_health(hospitals):
    return DepartmentOfHealth(hospitals)


def create_hospitals(n_hospitals):
    hospitals = [
        Hospital(capacity=100, drug_repository=CheapDrugRepository())
        for i in range(n_hospitals)
    ]
    return hospitals


def initialize():
    # our little country
    min_i, max_i = 0, 100
    min_j, max_j = 0, 100
    
    # our citizen
    n_persons = 300
    persons = create_persons(min_j, max_j, min_i, max_i, n_persons)
        
    # our healthcare system
    n_hospitals = 4
    hospitals = create_hospitals(n_hospitals)
    
    health_dept = create_department_of_health(hospitals)
    
    #attaching observer to observables
    for p in persons:
        p.attach(health_dept)

    # global context
    context = GlobalContext(
        (min_j, max_j, min_i, max_i),
        persons,
        health_dept
    )

    return context


class Drug(ABC):
    def apply(self, person):
        # somehow reduce person's symptoms
        pass


class AntipyreticDrug(Drug): pass


class Aspirin(AntipyreticDrug):
    '''A cheaper version of the fever/pain killer.'''
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.5
        
    def apply(self, person):
        person.temperature = max(36.6, person.temperature - self.dose * self.efficiency)


class Ibuprofen(AntipyreticDrug):
    '''A more efficient version of the fever/pain killer.'''
    def __init__(self, dose):
        self.dose = dose
        
    def apply(self, person):
        person.temperature = 36.6


class RehydrationDrug(Drug): pass

class Glucose(RehydrationDrug):
    '''A cheaper version of the rehydration drug.'''
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.1
        
    def apply(self, person):
        person.water = min(person.water + self.dose * self.efficiency,
                            0.6 * person.weight)


class Rehydron(RehydrationDrug):
    '''A more efficient version of the rehydration drug.'''
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 1.0
        
    def apply(self, person):
        person._water = 0.6 * person.weight


class AntivirusDrug(Drug): pass

class Placebo(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose

    def apply(self, person): pass


class AntivirusSeasonalFlu(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 1.0
        
    def apply(self, person):
        if isinstance(person.virus, SeasonalFluVirus):
            person.virus.strength -= self.dose * self.efficiency
            
        elif isinstance(person.virus, SARSCoV2):
            person.virus.strength -= self.dose * self.efficiency / 10.0


class AntivirusSARSCoV2(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.1
        
    def apply(self, person):
        if isinstance(person.virus, SARSCoV2):
            person.virus.strength -= self.dose * self.efficiency


class AntivirusCholera(AntivirusDrug):
    def __init__(self, dose):
        self.dose = dose
        self.efficiency = 0.1
        
    def apply(self, person):
        if isinstance(person.virus, Cholera):
            person.virus.strength -= self.dose * self.efficiency



class AbstractPrescriptor(ABC):
    def __init__(self, drug_repository):
        self.drug_repository = drug_repository
        
    @abstractmethod
    def create_prescription(self) -> List[Drug]:
        pass
    

class SeasonalFluPrescriptor(AbstractPrescriptor):
    def __init__(self, drug_repository, antifever_dose, antivirus_dose):
        super().__init__(drug_repository)
        self.antifever_dose = antifever_dose
        self.antivirus_dose = antivirus_dose

    def create_prescription(self) -> List[Drug]:
        return [
            self.drug_repository.get_antifever(self.antifever_dose),
            self.drug_repository.get_seasonal_antivirus(self.antivirus_dose)
        ]

    
class CovidPrescriptor(AbstractPrescriptor):
    def __init__(self, drug_repository, antifever_dose, antivirus_dose):
        super().__init__(drug_repository)
        self.antifever_dose = antifever_dose
        self.antivirus_dose = antivirus_dose

    def create_prescription(self) -> List[Drug]:
        return [
            self.drug_repository.get_antifever(self.antifever_dose),
            self.drug_repository.get_sars_antivirus(self.antivirus_dose)
        ]


class CholeraPrescriptor(AbstractPrescriptor):
    def __init__(self, drug_repository, rehydradation_dose, antivirus_dose):
        super().__init__(drug_repository)
        self.rehydradation_dose = rehydradation_dose
        self.antivirus_dose = antivirus_dose

    def create_prescription(self) -> List[Drug]:
        return [
            self.drug_repository.get_rehydration(self.rehydradation_dose),
            self.drug_repository.get_cholera_antivirus(self.antivirus_dose)
        ]


def get_prescription_method(disease_type, drug_repository, antifever_dose, antivirus_dose,
rehydration_dose):
    if InfectableType.SeasonalFlu == disease_type:
        return SeasonalFluPrescriptor(drug_repository,antifever_dose, antivirus_dose)

    elif InfectableType.SARSCoV2 == disease_type:
        return CovidPrescriptor(drug_repository,antifever_dose,antivirus_dose)

    elif InfectableType.Cholera == disease_type:
        return CholeraPrescriptor(drug_repository, rehydration_dose, antivirus_dose)

    else:
        raise ValueError()



class DrugRepository(ABC):
    def __init__(self):
        self.treatment = []
        
    @abstractmethod
    def get_antifever(self, dose) -> Drug: pass
    
    @abstractmethod
    def get_rehydration(self, dose) -> Drug: pass
    
    @abstractmethod
    def get_seasonal_antivirus(self, dose) -> Drug: pass
    
    @abstractmethod
    def get_sars_antivirus(self, dose) -> Drug: pass
    
    @abstractmethod
    def get_cholera_antivirus(self, dose) -> Drug: pass
    
    def get_treatment(self):
        return self.treatment


class CheapDrugRepository(DrugRepository):
    def get_antifever(self, dose) -> Drug:
        return Aspirin(dose)

    def get_rehydration(self, dose) -> Drug:
        return Glucose(dose)

    def get_seasonal_antivirus(self, dose) -> Drug:
        return Placebo(dose)

    def get_sars_antivirus(self, dose) -> Drug:
        return Placebo(dose)

    def get_cholera_antivirus(self, dose) -> Drug:
        return Placebo(dose)


class ExpensiveDrugRepository(DrugRepository):
    def get_antifever(self, dose) -> Drug:
        return Ibuprofen(dose)

    def get_rehydration(self, dose) -> Drug:
        return Rehydron(dose)

    def get_seasonal_antivirus(self, dose) -> Drug:
        return AntivirusSeasonalFlu(dose)

    def get_sars_antivirus(self, dose) -> Drug:
        return AntivirusSARSCoV2(dose)

    def get_cholera_antivirus(self, dose) -> Drug:
        return AntivirusCholera(dose)

    

class State(ABC):
    def __init__(self, person): 
        self.person = person
        
    @abstractmethod
    def day_actions(self): pass

    @abstractmethod
    def night_actions(self): pass

    @abstractmethod
    def interact(self, other): pass

    @abstractmethod
    def get_infected(self, virus): pass


class Healthy(State):

    def day_actions(self):
        # different for CommunityPerson?!
        self.person.position = (randint(min_j, max_j), randint(min_i, max_i))

    def night_actions(self):
        self.person.position = self.person.home_position

    def interact(self, other: Person): pass

    def get_infected(self, virus):
        if virus.get_type() not in self.person.antibody_types:
            self.person.virus = virus
            self.person.set_state(AsymptomaticSick(self.person))


class AsymptomaticSick(State):
    DAYS_SICK_TO_FEEL_BAD = 2
    
    def __init__(self, person):
        super().__init__(person)
        self.days_sick = 0
        person.infected = True

    def day_actions(self):
        # different for CommunityPerson?!
        self.person.position = (randint(min_j, max_j), randint(min_i, max_i))

    def night_actions(self):
        self.person.position = self.person.home_position
        if self.days_sick == AsymptomaticSick.DAYS_SICK_TO_FEEL_BAD:
            self.person.set_state(SymptomaticSick(self.person))
        self.days_sick += 1

    def interact(self, other):
        other.get_infected(self.person.virus)

    def get_infected(self, virus): pass


class SymptomaticSick(State):
    def day_actions(self):
        self.person.progress_disease()
        
        if self.person.is_life_threatening_condition():
            health_dept = DepartmentOfHealth()
            health_dept.hospitalize(self.person)

        if self.person.is_life_incompatible_condition():
            self.person.set_state(Dead(self.person))
        
    def night_actions(self):
        # try to fight the virus
        self.person.fightvirus()
        if self.person.virus.strength <= 0:
            self.person.set_state(Healthy(self.person))
            self.person.infected = False
            self.person.hospitalized = False
            self.person.recovered = True
            self.person.dead = False
            self.person.antibody_types.add(self.person.virus.get_type())
            self.person.virus = None

    def interact(self, other): pass

    def get_infected(self, virus): pass

    
class Dead(State):
    def __init__(self, person : Person):
        person.dead = True
        person.hospitalized = False
        person.infected = False
        person.recovered = False

    def day_actions(self): pass

    def night_actions(self): pass

    def interact(self, other): pass

    def get_infected(self, virus): pass



context = initialize()

for day in tqdm.tqdm(range(100)):
    simulate_day(context)

context.health_dept.data.plot()
print(context.health_dept.data)
plt.show()
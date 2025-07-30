import datetime
import sys
from typing import Optional
from pydantic import BaseModel
from src.settings_loader.core import SettingsLoader
from tests.settings import AnimalConfig

def test_load_settings():
    def load_txt_key_value(file_path: str) -> dict[str, str]:
        result: dict[str, str] = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ":" not in line:
                    continue  # skip empty lines or malformed lines
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result
    
    settings = (
        SettingsLoader(AnimalConfig, 'settings.yaml')
            .with_custom_source_loaders({
                'txt': load_txt_key_value
            })
            .load()
    )

    assert settings.animal_name == "Leo"
    assert settings.species == "lion"
    assert settings.specs.endangered == True
    assert settings.specs.weight_kg == 190.5
    assert settings.specs.characteristics.habitat == "Savannah and grasslands of sub-Saharan Africa"
    assert settings.specs.characteristics.lifespan_years == "10-14"
    assert settings.medical_history.primary_vet == "John"
    assert settings.medical_history.last_checkup_date == datetime.date(2025, 6, 1)
    assert settings.medical_history.vaccinations_up_to_date == True
    assert settings.medical_history.notes == None
    assert settings.feeding_schedule.food_type == "fish"
    assert settings.feeding_schedule.feeding_times_per_day == 3
    assert settings.caretaker_info.name == "Emma"
    assert settings.caretaker_info.contact_number == "+9988776655"
    assert settings.caretaker_info.preferred_language == "French"
    assert settings.preferences.favorite_toys == ["ball", "scratch post"]
    assert settings.specs_copy.__dict__ == settings.specs.__dict__
    assert settings.specs_copy_with_overwrite.endangered == settings.specs.endangered
    assert settings.specs_copy_with_overwrite.weight_kg != settings.specs.weight_kg
    assert settings.specs_copy_with_overwrite.weight_kg == 200
    assert settings.specs_copy_with_overwrite.characteristics.habitat == settings.specs.characteristics.habitat
    assert settings.specs_copy_with_overwrite.characteristics.lifespan_years != settings.specs.characteristics.lifespan_years
    assert settings.specs_copy_with_overwrite.characteristics.lifespan_years == "15-20"
    
def test_load_args(monkeypatch):
    class ArgsSettings(BaseModel):
        food_type: Optional[str]

    monkeypatch.setattr(sys, "argv", ['program', '--food_type', 'vegan'])
    settings = SettingsLoader(AnimalConfig, 'settings.yaml').with_args(ArgsSettings).load()

    assert settings.feeding_schedule.food_type == "vegan"
    assert settings.caretaker_info.preferred_language == "English"
    assert settings.caretaker_info.contact_number is None

def test_settings_with_general_dynamic_vars(monkeypatch):
    class ArgsSettings(BaseModel):
        food_type: Optional[str]

    monkeypatch.setattr(sys, "argv", ['program', '--food_type', 'meat'])

    settings1 = SettingsLoader(AnimalConfig, 'settings.yaml').with_args(ArgsSettings).load()
    settings2 = SettingsLoader(AnimalConfig, 'animal_settings/settings3.yaml').with_args(ArgsSettings).load()

    assert settings1.__dict__ == settings2.__dict__

def test_settings_json_with_dynamic_vars_in_sources(monkeypatch):
    class ArgsSettings(BaseModel):
        food_type: Optional[str]
        feeding_times_per_day: int
        vaccinations_up_to_date: bool

    monkeypatch.setattr(sys, "argv", ['program', '--food_type', 'fish', '--feeding_times_per_day', '3', '--vaccinations_up_to_date'])

    settings1 = SettingsLoader(AnimalConfig, 'settings.yaml').load()
    settings2 = SettingsLoader(AnimalConfig, 'animal_settings/settings2.json').with_args(ArgsSettings).load()

    assert settings1.__dict__ == settings2.__dict__
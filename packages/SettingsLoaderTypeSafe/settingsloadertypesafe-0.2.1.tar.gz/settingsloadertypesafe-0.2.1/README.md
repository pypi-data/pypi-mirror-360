# SettingsLoader
![Version 0.2.1](https://img.shields.io/badge/version-0.2.1-brightgreen) ![example workflow](https://github.com/aqzi/SettingsLoader/actions/workflows/python-tests.yml/badge.svg) ![License MIT](https://img.shields.io/badge/license-MIT-green])

SettingsLoader is a component to load env, args, secrets and app settings into one type safe object. It's especially valuable if you need to pull settings from multiple sources. By default, it supports YAML, JSON, .env files, and command-line arguments. Additionally, you can extend it with custom source loaders to handle other file formats or configuration mechanisms as needed.

![code2flow logo](https://raw.githubusercontent.com/aqzi/SettingsLoader/master/assets/flow.png)

## Install
Install the package with pip:
```sh
pip install SettingsLoaderTypeSafe
```

Once installed, import it in your project and start using it right away. For example:
```python
from settings_loader.core import SettingsLoader

#Settings: your main settings class
#settings.yml: path to main config file
settings = SettingsLoader(Settings, 'settings.yml').load()
```


## Usage guide
This step-by-step guide demonstrates how to use the library with a playful example featuring a lion to showcase the different features.

1. <b>Define your main settings file</b><br/>
The main settings file must be in either YAML or JSON format. This file should include a `settings_loader` object that specifies the configuration for your sources. The `settings_loader` maps source keys to their corresponding source files. The supported file types for the sources are: json, yaml and env. Don't use 'env', 'args' and 'this' as custom source keys, as these are reserved for loading environment variables, command-line arguments and for making references within the current context, respectively.

    ```yml
    settings_loader:
        animal_info: [animal_settings/animal_specs.json, animal_settings/animal_specs_part2.yml]
        animal_caretaker_info: [animal_settings/caretaker_info.txt] #this requires custom loader as .txt is not supported by default
        secrets: [animal_settings/secret_info.env]
    ```

    The main settings file should contain all the configuration settings for your application. Within this file, you can reference values from other parts of the main settings file itself, from external source files, or from command-line arguments.
    References are defined using the syntax: `{{<source_key>.<field_path>}}`. The reference placeholder is dot seperated!
    - source_key refers to a key defined in your settings_loader.
    - field_path specifies the path to the desired value within the corresponding source file. Fields within field_path are also dot seperated.
    
    Within a reference, you can use the `>` symbol to define a fallback sequence. The settings loader will first attempt to retrieve the value from the first source. If the value is None, it will continue checking the next source in the sequence.

    ```yml
    animal_name: Leo #static value

    #Will be replaced by 'animal_type' value within the animal_info source. The 'animal_info' key is binded to both settings/animal_specs.json and settings/animal_specs_part2.yml
    #If 'animal_info' would be specified in both files, it will be taken from the last source in the list. In this case it would come from animal_specs_part2.yml
    species: "{{animal_info.animal_type}}"

    specs:
        endangered: "{{animal_info.extra_spec.endangered}}" #extra_spec.endangered is a path to a nested field within animal_info source
        weight_kg: "{{animal_info.weight_kg}}"
        characteristics:
            habitat: "{{animal_info.characteristics.habitat}}"
            lifespan_years: "{{animal_info.characteristics.lifespan_years}}"

    feeding_schedule:
        #Will be replaced by food_type value from the given command line arguments. If it's none it will be taken from the environment.
        food_type: "{{args.food_type > env.food_type}}"
        feeding_times_per_day: 3

    medical_history:
        primary_vet: John
        last_checkup_date: "{{secrets.last_vet_visit_date}}"
        vaccinations_up_to_date: "{{secrets.vaccinations_status}}"

    caretaker_info:
        name: Emma
        contact_number: "{{animal_caretaker_info.contact_number}}"
        preferred_language: "{{animal_caretaker_info.primary_language}}"
        #You can add additional text along with 1 or more refs. However this only works for strings!
        area_of_expertise: "All animals living in {{this.specs.characteristics.habitat}}"

    preferences:
        favorite_toys: [ball, "{{animal_info.toy}}"]
    ```

    We also support object references with optional field overwrites. To apply overwrites, use the reserved keyword `__base__` to specify the object to copy from, then define any fields you want to override.

    ```yml
    specs_copy: "{{this.specs}}" #Creates a direct copy of the existing 'specs' object (from main settings) without any modifications.
    specs_copy_with_overwrite:
    __base__: "{{this.specs}}" #Direct copy of specs
    weight_kg: "{{env.weight_kg}}" #After copy, overwrite weight_kg with value from the environment
    characteristics:
        lifespan_years: "15-20" #another overwrite
    ```

    To finalize this first step, consider the following example illustrating settings from one of the source files: animal_settings/secrets_info.env, which is mapped to the source key 'secrets'. In the main settings file, medical_history.last_checkup_date references last_vet_visit_date from the secrets source, resulting in the value '2025-06-01'. References within the same source file are also supported. Typically, source keys used in references correspond to those defined in the settings_loader section of the main settings file. However, there is an exception: the reserved keyword 'this', which allows referencing other fields within the same source file. In the example below, vaccinations_status references status in the same .env file using {{this.status}}. This resolves vaccinations_status to True. In the main settings, medical_history.vaccinations_up_to_date can then refer to vaccinations_status in secrets, and will also resolve to True.
    ```env
    last_vet_visit_date=2025-06-01
    vaccinations_status={{this.status}}

    status=True
    ```

2. <b>Define your data classes</b><br/>
Create data classes to represent the structure of your settings. Each class must inherit from pydantic.BaseModel to ensure type safety and validation. Be sure to assign default values to all optional fields. In this example, the AnimalConfig class models the complete set of information from the main settings file. Note that the `settings_loader` section is excluded from these data classes.

    ```python
    class FeedingSchedule(BaseModel):
        food_type: str = "meat"
        feeding_times_per_day: int = 2

    class MedicalHistory(BaseModel):
        primary_vet: str
        last_checkup_date: Optional[datetime.date] = None #Optional field must have a default value!
        vaccinations_up_to_date: bool = False
        notes: Optional[str] = None

    class CaretakerInfo(BaseModel):
        name: str
        contact_number: Optional[str] = None
        preferred_language: str = "English"
        area_of_expertise: str

    class Characteristics(BaseModel):
        habitat: str
        lifespan_years: str

    class Specs(BaseModel):
        weight_kg: float
        endangered: bool = False
        characteristics: Characteristics

    class Preferences(BaseModel):
        favorite_toys: list[str]

    class AnimalConfig(BaseModel):
        animal_name: str
        species: str
        specs: Specs
        feeding_schedule: FeedingSchedule
        medical_history: MedicalHistory
        caretaker_info: CaretakerInfo
        preferences: Preferences
        specs_copy: Specs
        specs_copy_with_overwrite: Specs
    ```

3. <b>Create the script</b><br/>
You’ll always need to load the main settings file, but how you extend it depends on your configuration. Below are three common patterns:
    1. Load your main settings file and specify the corresponding data class for type safety:
        ```python
        settings = SettingsLoader(AnimalConfig, 'settings.yml').load()
        ```
    2. In addition to the main settings, you can parse command-line arguments. This requires defining an argument class:
        ```python
        class ArgsSettings(BaseModel):
            food_type: Optional[str]

        settings = SettingsLoader(AnimalConfig, 'settings.yml').with_args(ArgsSettings).load()
        ```
    3. If you have a custom file format (ex: .txt), define a loader function and register it with the loader:
        ```python
        def load_txt_key_value(file_path: str) -> dict[str, str]:
            result: dict[str, str] = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    key, value = line.split(":", 1)
                    result[key.strip()] = value.strip()
            return result

        settings = (
            SettingsLoader(AnimalConfig, 'settings.yaml')
                .with_custom_source_loaders({
                    'txt': load_txt_key_value #txt corresponds to file extension name
                })
                .load()
        )
        ```
    More examples can be found inside the unit tests.
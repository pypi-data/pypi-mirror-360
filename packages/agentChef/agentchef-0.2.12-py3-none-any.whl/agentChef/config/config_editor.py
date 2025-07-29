"""
Interactive configuration editor for AgentChef.
"""

import configparser
from pathlib import Path
from typing import Any, Dict

from oarc_utils import singleton # Replace local decorator with oarc-utils
import questionary
from click import clear, echo, style, secho, pause

from agentChef.config.config import Config
from agentChef.config.config_manager import ConfigManager
from agentChef.config.config_validators import NumberValidator
from agentChef.utils.paths import Paths
from agentChef.utils.const import CONFIG_SECTION, DEFAULT_CONFIG_FILENAME, CONFIG_KEY_DATA_DIR, CONFIG_KEY_LOG_LEVEL, DEFAULT_CONFIG


# global class
@singleton
class ConfigEditor:
    """Interactive UI for editing agentChef configuration."""
    
    def __init__(self):
        self._current_config = DEFAULT_CONFIG.copy()
        self._config_details = {
            CONFIG_KEY_DATA_DIR: {
                "description": "Directory to store data",
                "type": "path",
                "help": "Enter a valid directory path"
            },
            CONFIG_KEY_LOG_LEVEL: {
                "description": "Logging verbosity level",
                "type": "select",
                "options": ["DEBUG", "INFO", "WARNING", "ERROR"],
                "help": "Select logging level"
            }
        }

    def main_menu(cls) -> None:
        """Display the main configuration menu."""
        cls._ensure_initialized()
        
        action = questionary.select(
            "Select an action:",
            choices=[
                "Edit configuration settings",
                "Save current configuration",
                "Reset to defaults",
                "Show current configuration",
                questionary.Separator(),
                "Exit"
            ]
        ).ask()
        
        match action:
            case "Edit configuration settings":
                cls.edit_settings()
            case "Save current configuration":
                cls.save_changes()
            case "Reset to defaults":
                if cls.confirm_reset():
                    cls._current_config = DEFAULT_CONFIG.copy()
                cls.main_menu()
            case "Show current configuration":
                cls.show_current_config()
            case "Exit":
                return

    @classmethod
    def _ensure_initialized(cls):
        """Ensure that the class variables are initialized."""
        # low class
        if cls._current_config is None:
            cls._current_config = ConfigManager.get_current_config()
            cls._config_details = ConfigManager.get_config_details()
    

    @classmethod
    def is_config_changed(cls) -> bool:
        """Check if the current config differs from saved/default config."""
        cls._ensure_initialized()
        orig_config = Config()
        for key, value in cls._current_config.items():
            orig_value = orig_config.get(key)
            if str(value) != str(orig_value):
                return True
        return False
    

    @classmethod
    def edit_settings(cls) -> None:
        """Present a menu to select which setting to edit."""
        cls._ensure_initialized()
        choices = [
            f"Data Directory ({cls._current_config.get(CONFIG_KEY_DATA_DIR)})",
            f"Log Level ({cls._current_config.get(CONFIG_KEY_LOG_LEVEL)})",
            f"Model Name ({cls._current_config.get('model_name', 'llama3')})",
            "Back to main menu"
        ]
        
        setting = questionary.select(
            "Select a setting to edit:",
            choices=choices
        ).ask()
        
        if not setting or setting == "Back to main menu":
            cls.main_menu()
            return
            
        cls._edit_setting(setting)
        cls.edit_settings()
    

    @classmethod
    def _edit_setting(cls, setting: str) -> None:
        """Edit a specific setting."""
        if not setting:
            echo(style("No setting selected", fg='red'))
            return

        try:
            key = setting.split(":")[0].strip()
            # Extract the current value and description
            current_value = cls._current_config.get(key)
            
            # Get the description part after the dash if it exists
            description = ""
            if " - " in setting:
                description = setting.split(" - ")[1].strip()
            
            # Handle different setting types
            setting_type = cls._config_details.get(key, {}).get("type", "string")
            message = f"Enter {key}"
            if description:
                message += f" ({description})"
            
            # Convert the current value to string to avoid None issues
            current_value_str = str(current_value) if current_value is not None else ""
            
            if setting_type == "select":
                options = cls._config_details.get(key, {}).get("options", [])
                value = questionary.select(
                    message,
                    choices=options,
                    default=current_value_str
                ).ask()
            elif setting_type == "int":
                value_range = cls._config_details.get(key, {}).get("range", (0, 100))
                
                # Create a safer validator function that properly handles validation results
                def safe_validator(text):
                    try:
                        # Check if the input can be converted to an integer
                        value = int(text)
                        min_val, max_val = value_range
                        
                        # Validate range manually instead of relying on the validator class
                        if value < min_val:
                            return f"Value must be at least {min_val}"
                        if value > max_val:
                            return f"Value must be at most {max_val}"
                            
                        # If we get here, the validation is successful
                        return True
                    except ValueError:
                        return "Please enter a valid number"
                    except Exception as e:
                        return str(e)
                
                value = questionary.text(
                    message,
                    default=current_value_str,
                    validate=safe_validator
                ).ask()
                
                # Handle the case where ask() returns None (e.g., user cancels)
                if value is None:
                    return
                    
                value = int(value)
            elif setting_type == "path":
                value = questionary.path(
                    message,
                    default=current_value_str
                ).ask()
                
                # Handle the case where ask() returns None
                if value is None:
                    return
                    
                path = Path(value).expanduser().resolve()
                if not path.exists():
                    create = questionary.confirm(
                        f"Directory {path} doesn't exist. Create it?",
                        default=True
                    ).ask()
                    
                    # Handle the case where ask() returns None
                    if create is None:
                        return
                        
                    if create:
                        try:
                            path.mkdir(parents=True, exist_ok=True)
                            echo(style(f"Created directory: {path}", fg='green'))
                        except Exception as e:
                            echo(style(f"Error creating directory: {e}", fg='red'))
                value = str(path)
            elif setting_type == "password":
                # Handle password fields just like regular text fields
                # (no special masking)
                value = questionary.text(
                    message,
                    default=current_value_str
                ).ask()
            else:  # string or other
                value = questionary.text(
                    message,
                    default=current_value_str
                ).ask()
            
            # Only update the value if we got a non-None response
            if value is not None:
                cls._current_config[key] = value
        except Exception as e:
            echo(style(f"Error editing setting: {str(e)}", fg='red'))
    

    @staticmethod
    def confirm_reset() -> bool:
        """Confirm if user wants to reset to defaults."""
        return questionary.confirm(
            'Reset all settings to defaults?',
            default=False
        ).ask()
    

    @classmethod
    def reset_to_defaults(cls) -> None:
        """Reset all values to their defaults."""
        cls._ensure_initialized()
        config = Config()
        for key, value in config.DEFAULTS.items():
            if hasattr(value, "__str__"):
                cls._current_config[key] = str(value)
            else:
                cls._current_config[key] = value
    

    @classmethod
    def save_changes(cls, edited_values: Dict[str, Any]) -> bool:
        """Save changes to configuration file."""
        # Find or create config file
        config_file = ConfigManager.find_config_file()
        if not config_file:
            config_file = Paths.ensure_config_dir() / DEFAULT_CONFIG_FILENAME
        
        # Create/update config file
        parser = configparser.ConfigParser()
        if config_file.exists():
            parser.read(config_file)
        
        if CONFIG_SECTION not in parser:
            parser[CONFIG_SECTION] = {}
        
        # Update with edited values 
        for key, value in edited_values.items():
            parser[CONFIG_SECTION][key] = str(value)
            
        # Write to file
        try:
            with open(config_file, 'w') as f:
                parser.write(f)
            
            echo(style("\nConfiguration saved successfully!", fg='green'))
            
            # Ask if user wants to update environment variables
            set_env = questionary.confirm(
                'Do you want to also set these as persistent environment variables?',
                default=False
            ).ask()
            
            if set_env:
                ConfigManager.update_env_vars(edited_values)
            
            return True
        except Exception as e:
            echo(style(f"Error saving config: {e}", fg='red'))
            return False
    

    @classmethod
    def load_config_file(cls, config_file: str = None) -> None:
        """
        Load a specific configuration file.
        
        Args:
            config_file (str, optional): Path to the config file to load
        """
        if config_file:
            # Load the specified config file
            Config.load_from_file(config_file)
            
            # Refresh the current config after loading
            cls._current_config = ConfigManager.get_current_config()
            
            echo(style(f"Loaded configuration from: {config_file}", fg='green'))


    @classmethod
    def show_current_config(cls):
        """Display the current configuration values in a formatted table."""
        config = cls._current_config
        if not config:
            echo("No configuration settings found.")
            return
        
        secho("Current configuration:", fg="cyan")
        secho("──────────────────────────────────────────────────", fg="cyan")
        
        for i, (key, value) in enumerate(config.items()):
            description = cls._config_details.get(key, {}).get("description", "")
            source = cls._config_details.get(key, {}).get("source", "unknown")
            
            # Print key and value on the same line
            secho(f"{key}: ", fg="green", nl=False)
            # No special handling for sensitive values - display all values as is
            echo(f"{value}")
                
            echo(f"  Source: {source}")
            echo(f"  Description: {description}")
            
            # Add a separator line only between items, not after the last one
            if i < len(config) - 1:
                echo("")
        
        # Wait for user to press a key
        echo("\n")
        pause(info=style('Press any key to continue...', fg='yellow'))
        clear()  # Clear the screen before returning to main menu
        cls.main_menu()

    @classmethod
    def load_configuration(cls) -> None:
        """
        Load a configuration file from a user-specified path.
        """
        # Ask for file path
        file_path = questionary.path(
            "Enter path to configuration file:",
            only_directories=False
        ).ask()
        
        # Handle cancellation
        if not file_path:
            return
            
        # Check if file exists
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            echo(style(f"Error: File '{path}' does not exist.", fg='red'))
            return
        
        try:
            # Load the config file
            cls.load_config_file(str(path))
            echo(style(f"Configuration loaded from: {path}", fg='green'))
        except Exception as e:
            echo(style(f"Error loading configuration: {str(e)}", fg='red'))

    @classmethod
    def run(cls, config_file: str = None) -> None:
        """
        Run the interactive configuration editor.
        
        Args:
            config_file (str, optional): Path to a specific config file to edit
        """
        try:
            # Initialize class variables
            cls._ensure_initialized()
            
            # Load specific config file if provided
            if config_file:
                cls.load_config_file(config_file)
                
            clear()
            cls.main_menu()
        except KeyboardInterrupt:
            echo(style("\nOperation cancelled by user.", fg='yellow'))
        finally:
            echo(style("\nExiting configuration editor.", fg='blue'))

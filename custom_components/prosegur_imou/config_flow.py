"""Flujo de configuración visual para Movistar Prosegur IMOU."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .auth import ProsegurAuth

DOMAIN = "prosegur_imou"
_LOGGER = logging.getLogger(__name__)

class ProsegurConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Maneja el formulario interactivo de configuración desde la interfaz."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Paso inicial cuando el usuario pulsa en Añadir Integración."""
        errors = {}

        if user_input is not None:
            # Evita añadir la misma cuenta dos veces
            await self.async_set_unique_id(f"{user_input['contract_id']}")
            self._abort_if_unique_id_configured()

            # Comprueba la validez de las credenciales ingresadas
            auth = ProsegurAuth(
                user_input["username"],
                user_input["password"],
                user_input["contract_id"]
            )
            
            try:
                token = await auth.async_get_token()
                if token:
                    return self.async_create_entry(
                        title=f"Prosegur ({user_input['contract_id']})",
                        data=user_input
                    )
                else:
                    errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.error("Error al autenticar con Prosegur: %s", err)
                errors["base"] = "cannot_connect"

        # Formulario que aparecerá en la ventana emergente de Home Assistant
        data_schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
            vol.Required("contract_id"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
    

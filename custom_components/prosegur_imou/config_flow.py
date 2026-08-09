"""Flujo de configuración visual para Movistar Prosegur Unificado."""
import logging
import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "prosegur_imou"
_LOGGER = logging.getLogger(__name__)


class ProsegurConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Maneja el formulario interactivo de configuración desde la interfaz."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Paso inicial al añadir la integración."""
        errors = {}

        if user_input is not None:
            # Evita añadir el mismo contrato dos veces
            await self.async_set_unique_id(user_input["contract_id"])
            self._abort_if_unique_id_configured()

            # Intentamos importar la autenticación dentro del paso para evitar fallos al cargar el módulo
            try:
                from .auth import ProsegurAuth
                auth = ProsegurAuth(
                    user_input["username"],
                    user_input["password"],
                    user_input["contract_id"],
                )
                token = await auth.async_get_token()
                if not token:
                    errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.warning("No se pudo validar credenciales antes de guardar (o no existe auth.py): %s", err)

            # Si no hay errores críticos de validación, creamos la entrada
            if not errors:
                return self.async_create_entry(
                    title=f"Prosegur ({user_input['contract_id']})",
                    data=user_input,
                )

        # Formulario que aparecerá en la ventana emergente
        data_schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
            vol.Required("contract_id"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

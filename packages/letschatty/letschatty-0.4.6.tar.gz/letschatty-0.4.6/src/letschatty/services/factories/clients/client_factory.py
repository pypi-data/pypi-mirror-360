from letschatty.models.messages.meta_message_model.meta_base_notification_json import Contact
from letschatty.models.chat.client import Client
from letschatty.services.chat.client_service import ClientService
from letschatty.models.company.empresa import EmpresaModel
from letschatty.models.messages.message_templates.filled_data_from_frontend import FilledTemplateData
from datetime import datetime
from zoneinfo import ZoneInfo

class ClientFactory:

    @staticmethod
    def from_json(client_json: dict) -> Client:
        return Client(**client_json)

    @staticmethod
    def from_meta_contact(meta_contact: Contact, empresa: EmpresaModel) -> Client:
        return Client(
            name=meta_contact.get_name(),
            waid=meta_contact.get_wa_id(),
            company_id=empresa.id,
            country=ClientService.find_country_with_phone(meta_contact.get_wa_id()),
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC")),
        )

    @staticmethod
    def from_filled_template_data(filled_template_data: FilledTemplateData) -> Client:
        country = ClientService.find_country_with_phone(filled_template_data.phone_number) #type: ignore
        client : Client = Client(
            waid = filled_template_data.phone_number, #type: ignore
            name = filled_template_data.new_contact_name, #type: ignore
            country = country,
            created_at=datetime.now(ZoneInfo("UTC")),
            updated_at=datetime.now(ZoneInfo("UTC")),
        )
        return client

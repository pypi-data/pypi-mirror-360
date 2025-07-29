import copy
from bagels.managers.persons import get_person_by_id
from bagels.forms.form import Form, FormField


class PersonForm:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------ Blueprints ------------ #

    FORM = Form(
        fields=[
            FormField(
                placeholder="Steve",
                title="Name",
                key="name",
                type="string",
                is_required=True,
            ),
        ]
    )
    # ------------- Builders ------------- #

    def get_filled_form(self, personId: int):
        form = copy.deepcopy(self.FORM)
        person = get_person_by_id(personId)
        for field in form.fields:
            value = getattr(person, field.key)
            field.default_value = str(value) if value is not None else ""
        return form

    def get_form(self):
        return copy.deepcopy(self.FORM)

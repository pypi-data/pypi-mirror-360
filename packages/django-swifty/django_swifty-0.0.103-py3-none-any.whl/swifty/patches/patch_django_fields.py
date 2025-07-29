from django.forms.fields import ChoiceField


# Define the monkey patch
def patched_choice_field():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
        # Replace the problematic 'choices' property
        if not hasattr(ChoiceField, "_set_choices"):
            # Use the public 'choices' setter if available
            setattr(ChoiceField, "_set_choices", ChoiceField.choices)
            print("Monkey patch applied: ChoiceField in django_sorcery.")

    except ImportError as e:
        print(f"Could not apply monkey patch: {e}")


patched_choice_field()

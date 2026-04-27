from .models import ECHS, CGHS, CAPF

def get_panel_model(panel_name):
    """
    Returns the appropriate model and panel title based on the panel name.
    """
    panels = {
        'echs': (ECHS, 'ECHS'),
        'cghs': (CGHS, 'CGHS'),
        'capf': (CAPF, 'CAPF')
    }
    return panels.get(panel_name.lower(), (None, None))

def get_expected_headers(panel_name):
    """
    Returns the expected headers for the given panel, ensuring common fields are standardized.
    """
    common_headers = ['card_number', 'patient_name', 'hospital_name', 'claim_amount']
    
    specific_headers = {
        'echs': [
            'service_number', 'relation', 'admission_date', 'discharge_date', 
            'claim_id', 'io', 'stay', 'ailment'
        ],
        'cghs': [
            'family_id', 'case_id', 'registered_date', 'procedure', 
            'admission_date', 'intimation_raised_date'
        ],
        'capf': [
            'family_id', 'case_id', 'registered_date', 'procedure', 
            'admission_date', 'intimation_raised_date'
        ]
    }

    return common_headers + specific_headers.get(panel_name.lower(), [])

def map_common_fields(field_name):
    """
    Maps various field names across panels to ensure consistency in UI and exports.
    """
    field_mapping = {
        'admit_date': 'admission_date',
        'discharge_date': 'discharge_date',
        'registered_date': 'admission_date',
        'intimation_raised_date': 'claim_processing_date',
        'service_number': 'service_id',
        'family_id': 'family_identifier',
        'case_id': 'case_reference'
    }
    return field_mapping.get(field_name, field_name)

def is_valid_panel(panel_name):
    """
    Checks if the given panel name is valid.
    """
    return panel_name.lower() in ['echs', 'cghs', 'capf']

def get_searchable_fields(panel_name):
    """
    Returns the searchable fields dynamically based on the panel.
    """
    search_fields = {
        'echs': ['card_number', 'service_number', 'patient_name'],
        'cghs': ['card_number', 'family_id', 'case_id', 'patient_name'],
        'capf': ['card_number', 'family_id', 'case_id', 'patient_name']
    }
    return search_fields.get(panel_name.lower(), ['card_number', 'patient_name'])

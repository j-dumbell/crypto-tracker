from datetime import datetime
from app.models import get_all_currencies


def validate_query_string(query_params, validators):
    errors = {}
    for field, dict_req in validators.items():
        fn, required = dict_req
        input = query_params.get(field, None)
        if input==None and required==True:
            errors[field]="Parameter required but not provided."
        elif input==None and required==False:
            pass
        else:
            if fn!=None:
                error = fn(input)
                if error!=None:
                    errors[field]=error
    return errors


def validate_date(date):
    try:
        d = datetime.strptime(date, '%Y-%m-%d').date()
        if d > datetime.today().date():
            return 'Date in future.'
        else:
            return None
    except Exception as e:
        return 'Invalid date.  Please enter in format YYYY-MM-DD.'


def validate_currency(currency):
    if currency in get_all_currencies():
        return None
    else:
        return 'Invalid currency code.'

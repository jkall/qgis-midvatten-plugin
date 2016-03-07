from datetime import datetime

def find_date_format(datestring):
    datestring = str(datestring)
    date_formats_to_try = ['%Y/%m/%d %H:%M:%S']
    found_format = None
    for dateformat in date_formats_to_try:
        try:
            datetime.strptime(datestring, '%Y/%m/%d %H:%M:%S')
        except ValueError:
            continue
        else:
            found_format = dateformat
            break
    return found_format

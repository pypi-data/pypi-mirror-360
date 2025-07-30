from django.forms import ValidationError



def raise_error(message):
    raise ValidationError(
        {
            "message": message,
        })


def validate_item_in_list(
         item, list, message, message_if_empty="", required=False
    ):
        if required and not item:
            raise_error(message_if_empty)

        if item:
            if isinstance(item, list):
                itens = item

                return (
                    itens
                    if all(item in list for item in itens)
                    else raise_error(message)
                )

            return item if item in list else raise_error(message)

        return False



def validate_natural_number(
         number, message, message_if_empty="", required=False
    ):
        if isinstance(number, list):
            number = list(filter(lambda x: x.strip() != "", number))

        elif isinstance(number, str) and number.strip() == "":
            number = None

        if required and not number:
            raise_error(message_if_empty)

        if number:
            if isinstance(number, list):
                numbers = number
                to_int = lambda x: int(x)

                return (
                    list(map(to_int, numbers))
                    if all(number.isnumeric() and number != "0" for number in numbers)
                    else  raise_error(message)
                )

            return (
                number
                if number.isnumeric() and number != "0"
                else raise_error(message)
            )

        return False

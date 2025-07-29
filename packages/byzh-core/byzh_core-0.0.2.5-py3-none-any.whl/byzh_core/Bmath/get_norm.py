from typing import Literal
def b_get_norm(
    lst: list,
    mode: Literal['min-max'] = 'min-max',
    ndigits: int | None = None
) -> tuple[list, float, float]:

    if mode =='min-max':
        minimum = min(lst)
        maximum = max(lst)
        if ndigits is None:
            result = [(x-minimum)/(maximum-minimum) for x in lst]
        else:
            result = [round((x-minimum)/(maximum-minimum), ndigits) for x in lst]
        return (result, minimum, maximum)


if __name__ == '__main__':
    lst = [1, 2, 3, 4, 5]
    result = b_get_norm(lst)
    print(result)
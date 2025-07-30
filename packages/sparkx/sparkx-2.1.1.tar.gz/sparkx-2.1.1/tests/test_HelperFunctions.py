# ===================================================
#
#    Copyright (c) 2023-2024
#      SPARKX Team
#
#    GNU General Public License (GPLv3 or later)
#
# ===================================================

import HelperFunctions as hf
import pytest


def test_convert_str_to_number():
    str_float = "3.14"
    assert isinstance(hf.convert_str_to_number(str_float), float)
    assert hf.convert_str_to_number(str_float) == pytest.approx(
        3.14, abs=hf.small_value
    )

    str_scientific_float = "63e7"
    assert isinstance(hf.convert_str_to_number(str_scientific_float), float)
    assert hf.convert_str_to_number(str_scientific_float) == pytest.approx(
        63e7, abs=hf.small_value
    )

    str_scientific_float_upper = "63E7"
    assert isinstance(
        hf.convert_str_to_number(str_scientific_float_upper), float
    )
    assert hf.convert_str_to_number(
        str_scientific_float_upper
    ) == pytest.approx(63e7, abs=hf.small_value)

    str_int = "42"
    assert isinstance(hf.convert_str_to_number(str_int), int)
    assert hf.convert_str_to_number(str_int) == 42


@pytest.mark.parametrize(
    "invalid_numbers",
    [
        "3.14.15",
        "3.14e",
        "3.14 e",
        "3.14e15.9",
        "3.14 15.9",
        "3.14e15 9",
        "3.14e15e9",
        "abc",
        "3.14a",
        " ",
        "",
    ],
)
def test_convert_str_to_number_invalid_input(invalid_numbers):
    with pytest.raises(ValueError):
        hf.convert_str_to_number(invalid_numbers)


def test_convert_nested_list_to_numerical():
    nested_list = [["3.14", "42", "63e7"], ["1", "2.3", "3"], ["4", "5", "6"]]
    expected = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    converted_list = hf.convert_nested_list_to_numerical(nested_list)

    assert len(converted_list) == len(expected)
    for sublist, expected_sublist in zip(converted_list, expected):
        assert len(sublist) == len(expected_sublist)
        for item, expected_item in zip(sublist, expected_sublist):
            assert item == pytest.approx(expected_item, abs=hf.small_value)


def test_compare_nested_lists():
    list1 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    list2 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    assert hf.compare_nested_lists(list1, list2)

    list3 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    list4 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 7]]
    assert not hf.compare_nested_lists(list3, list4)

    list5 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    list6 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5]]
    assert not hf.compare_nested_lists(list5, list6)

    list7 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    list8 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6, 7]]
    assert not hf.compare_nested_lists(list7, list8)

    list9 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    list10 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6.1]]
    assert hf.compare_nested_lists(list9, list10, tol=0.100001)

    list11 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    list12 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6.1]]
    assert not hf.compare_nested_lists(list11, list12)

    list13 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, 6]]
    list14 = [[3.14, 42, 63e7], [1, 2.3, 3], [4, 5, "6"]]
    assert not hf.compare_nested_lists(list13, list14)

    list15 = [[3.14, "a", 63e7], [1, 2.3, 3], [4, 5, 6]]
    list16 = [[3.14, "a", 63e7], [1, 2.3, 3], [4, 5, 6]]
    assert hf.compare_nested_lists(list15, list16)

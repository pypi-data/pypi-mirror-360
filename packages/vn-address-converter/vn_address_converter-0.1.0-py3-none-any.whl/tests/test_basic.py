"""
Basic functionality tests for vn-address-converter.
"""
from vn_address_converter import convert_to_new_address, Address
import pytest

@pytest.mark.parametrize("address,expected", [
    (
        Address(
            street_address="720A Điện Biên Phủ",
            ward="Phường 22",
            district="Quận Bình Thạnh",
            province="Thành phố Hồ Chí Minh"
        ),
        Address(
            street_address="720A Điện Biên Phủ",
            ward="Phường Thạnh Mỹ Tây",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        Address(
            street_address="1 P. Nhà Thờ",
            ward="Phường Hàng Trống",
            district="Quận Hoàn Kiếm",
            province="Thành phố Hà Nội"
        ),
        Address(
            street_address="1 P. Nhà Thờ",
            ward="Phường Hoàn Kiếm",
            district=None,
            province="Thành phố Hà Nội"
        )
    ),
    (
        # case insensitive ward and district
        Address(
            street_address="07 Công trường Lam Sơn",
            ward="phường bến nghé",
            district="quận 1",
            province="thành phố hồ chí minh"
        ),
        Address(
            street_address="07 Công trường Lam Sơn",
            ward="Phường Sài Gòn",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        # test aliases
        Address(
            street_address="51 Lê Lợi",
            ward="Phú Hội",
            district="Thuận Hóa",
            province="Huế"
        ),
        Address(
            street_address="51 Lê Lợi",
            ward="Phường Thuận Hóa",
            district=None,
            province="Thành phố Huế"
        )
    ),
    (
        # test aliases for Bà Rịa - Vũng Tàu
        Address(
            street_address="31-33-35 Nguyễn Văn Cừ",
            ward="Long Toàn",
            district="Bà Rịa",
            province="Bà Rịa - Vũng Tàu"
        ),
        Address(
            street_address="31-33-35 Nguyễn Văn Cừ",
            ward="Phường Bà Rịa",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
])
def test_convert_address_table(address, expected):
    result = convert_to_new_address(address)
    assert result == expected

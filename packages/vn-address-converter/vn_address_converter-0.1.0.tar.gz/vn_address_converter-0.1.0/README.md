# Vietnam Address Converter

This is the result of my vibe coding experiment to fully use AI to solve a problem.

Vietnam recently merged 63 provinces into 34, creating a need to convert old addresses to the new administrative format. This Python package provides a solution for converting old Vietnamese addresses to the new format.

Most of the code is written with Github Copilot using GPT 4.1 and Claude Sonet 4 model.

The mapping data is sourced from [here](https://github.com/thanhtrungit97/dvhcvn/tree/main). Initially, I tried to parse from this [wiki page](https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_%C4%91%C6%A1n_v%E1%BB%8B_h%C3%A0nh_ch%C3%ADnh_Vi%E1%BB%87t_Nam_trong_%C4%91%E1%BB%A3t_c%E1%BA%A3i_c%C3%A1ch_th%E1%BB%83_ch%E1%BA%BF_2024%E2%80%932025), but the result was so bad that I ended up abandoning the parser.

## Disclaimer

This package is experimental and may not be 100% accurate. Please verify results and contribute improvements!

## Installation

```bash
pip install vn-address-converter
```

## Usage Example

```python
from vn_address_converter import convert_to_new_address, Address

address = Address(
    street_address="720A Điện Biên Phủ",
    ward="Phường 22",
    district="Quận Bình Thạnh",
    province="Thành phố Hồ Chí Minh"
)

new_address = convert_to_new_address(address)
print(new_address)
# Output: {'street_address': '720A Điện Biên Phủ', 'ward': 'Phường Thạnh Mỹ Tây', 'district': None, 'province': 'Thành phố Hồ Chí Minh'}
```

## License

MIT
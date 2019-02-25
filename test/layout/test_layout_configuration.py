from dataclasses import dataclass
from unittest.mock import patch, MagicMock

import pytest

from randovania.bitpacking import bitpacking
from randovania.bitpacking.bitpacking import BitPackDecoder, BitPackValue
from randovania.layout.layout_configuration import LayoutConfiguration, LayoutTrickLevel, LayoutSkyTempleKeyMode, \
    LayoutElevators
from randovania.layout.pickup_quantities import PickupQuantities
from randovania.layout.starting_location import StartingLocation
from randovania.layout.starting_resources import StartingResources


@dataclass(frozen=True)
class DummyValue(BitPackValue):
    def bit_pack_format(self):
        yield from []

    def bit_pack_arguments(self):
        yield from []

    @classmethod
    def bit_pack_unpack(cls, decoder: BitPackDecoder):
        raise cls()


@pytest.fixture(
    params=[
        {"encoded": b'\x16',
         "trick": LayoutTrickLevel.NO_TRICKS,
         "sky_temple": LayoutSkyTempleKeyMode.NINE,
         "elevators": LayoutElevators.VANILLA,
         },
        {"encoded": b'\xa0',
         "trick": LayoutTrickLevel.HYPERMODE,
         "sky_temple": LayoutSkyTempleKeyMode.ALL_BOSSES,
         "elevators": LayoutElevators.VANILLA,
         },
        {"encoded": b'\x89',
         "trick": LayoutTrickLevel.HARD,
         "sky_temple": LayoutSkyTempleKeyMode.TWO,
         "elevators": LayoutElevators.RANDOMIZED,
         },
        {"encoded": b'\xc3',
         "trick": LayoutTrickLevel.MINIMAL_RESTRICTIONS,
         "sky_temple": LayoutSkyTempleKeyMode.ALL_GUARDIANS,
         "elevators": LayoutElevators.RANDOMIZED,
         },
    ],
    name="layout_config_with_data")
def _layout_config_with_data(request):
    starting_location = DummyValue()
    starting_resources = DummyValue()
    pickup_quantities = MagicMock(return_value=DummyValue())

    with patch.multiple(PickupQuantities, from_params=pickup_quantities, bit_pack_unpack=pickup_quantities), \
         patch.multiple(StartingLocation, bit_pack_unpack=MagicMock(return_value=starting_location)), \
         patch.multiple(StartingResources, bit_pack_unpack=MagicMock(return_value=starting_resources)):
        yield request.param["encoded"], LayoutConfiguration.from_params(
            trick_level=request.param["trick"],
            sky_temple_keys=request.param["sky_temple"],
            elevators=request.param["elevators"],
            starting_location=starting_location,
        )


def test_decode(layout_config_with_data):
    # Setup
    data, expected = layout_config_with_data

    # Run
    decoder = BitPackDecoder(data)
    result = LayoutConfiguration.bit_pack_unpack(decoder)

    # Assert
    assert result == expected


def test_encode(layout_config_with_data):
    # Setup
    expected, value = layout_config_with_data

    # Run
    result = bitpacking.pack_value(value)

    # Assert
    assert result == expected

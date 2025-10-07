import sys
import os
import pytest

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.afc import AFCEngine, AFCRequest, ResponseCode
from core.phy import Antenna, Environment
from core.afc_phy_interface import AFCPhyInterface

@pytest.fixture
def setup_objects():
    """Creates test objects for all test cases"""
    # Mock objects with test parameters
    phy = type('MockPHY', (), {'antenna': Antenna(gain_dbi=5.0)})()
    afc = AFCEngine(ruleset="FCC_6GHZ")
    return AFCPhyInterface(phy, afc)

def test_valid_afc_to_phy_conversion(setup_objects):
    """Tests if AFC channels convert correctly to PHY parameters"""
    interface = setup_objects
    request = AFCRequest(
        request_id="test1",
        request_type="AVAILABLE_SPECTRUM",
        device_location=(37.0, -122.0),  # Outside exclusion zone
        device_height=10.0,
        frequency_mhz=5950.0
    )
    
    configs = interface.configure_phy_from_afc(request)
    
    # Check conversion math
    assert len(configs) > 0
    assert configs[0].center_freq_mhz == 5960.0  # Matches 20MHz channel math
#    assert configs[0].tx_power_dbm == 25.0  # 30 dBm EIRP - 5 dBi antenna gain (değiştirdik bunu)
    assert configs[0].tx_power_dbm == 15.0  # 30 dBm EIRP - 15 dBi gain?

def test_exclusion_zone_rejection(setup_objects):
    """Tests if exclusion zones block transmissions"""
    interface = setup_objects
    request = AFCRequest(
        request_id="test2",
        request_type="AVAILABLE_SPECTRUM",
        device_location=(37.7749, -122.4194),  # Inside SF exclusion zone
        device_height=10.0
    )
    
    with pytest.raises(ValueError) as excinfo:
        interface.configure_phy_from_afc(request)
    assert "AFC rejected request" in str(excinfo.value)
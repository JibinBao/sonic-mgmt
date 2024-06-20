import pytest
from tests.common.helpers.assertions import pytest_assert
from tests.common.plugins.allure_wrapper import allure_step_wrapper as allure
from tests.common.platform.interface_utils import get_dpu_npu_ports_from_hwsku

pytestmark = [
    pytest.mark.topology('any')
]


def test_dpu_npu_port(duthosts, rand_one_dut_hostname, dpu_npu_port_list):
    """
    This test case is to verify
    1. The dpu npu ports defined in hwsku.json are same as that in config db
    2. When the role of port is Dpc, the type of port is  DPU-NPU Data Port
    """
    duthost = duthosts[rand_one_dut_hostname]
    intf_status = duthost.show_interface(command="status")["ansible_facts"]['int_status']
    dpu_npu_port_type = 'DPU-NPU Data Port'
    dut_hwsku = duthost.facts["hwsku"]
    dpu_npu_ports = dpu_npu_port_list[duthost.hostname]
    dpu_npu_port_list_in_hwsku = get_dpu_npu_ports_from_hwsku(duthost)

    if dpu_npu_port_list_in_hwsku:
        with allure.step(f"check dpu port in config db are same as the dpu ports in hwsku"):
            pytest_assert(set(dpu_npu_ports) == set(dpu_npu_port_list_in_hwsku),
                          f"For {dut_hwsku}, the dpu npu ports in hwsku.json are:{dpu_npu_port_list_in_hwsku},"
                          f"the dpu npu ports in config db are {dpu_npu_ports}",)
    else:
        pytest.skip("Skip the test due to no dpu npu ports")

    with allure.step("Check interface type for dpu npu port"):
        for intf in dpu_npu_ports:
            pytest_assert(
                intf in intf_status, f"interface {intf} is not in the output of show interface status: {intf_status}")
            pytest_assert(
                intf_status[intf].get('type') == dpu_npu_port_type,
                f"Interface {intf}: The actual type is is {intf_status[intf].get('type')}, "
                f"the expected type is {dpu_npu_port_type}")

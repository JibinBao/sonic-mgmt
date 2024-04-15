import pytest
from tests.common.helpers.assertions import pytest_assert
from tests.common.plugins.allure_wrapper import allure_step_wrapper as allure

pytestmark = [
    pytest.mark.topology('any')
]

sku_dpu_pdu_ports_map = {"Mellanox-SN4700-O28": ["Ethernet224", "Ethernet232", "Ethernet240", "Ethernet248"],
                         "Nvidia-9009d3b600CVAA-C1": ["Ethernet0"]}


def test_dpu_npu_port(duthosts, rand_one_dut_hostname, dpu_npu_port_list):
    """
    This test case is to verify
    1. The relevant sku include the corresponding dpu npu ports
    2. When the role of port is Dpc, the type of port is  DPU-NPU Data Port
    """
    duthost = duthosts[rand_one_dut_hostname]
    intf_status = duthost.show_interface(command="status")["ansible_facts"]['int_status']
    dpu_npu_port_type = 'DPU-NPU Data Port'
    dut_hwsku = duthost.facts["hwsku"]
    dpu_npu_ports = dpu_npu_port_list[duthost.hostname]

    if dut_hwsku in sku_dpu_pdu_ports_map:
        with allure.step(f"check sku {dut_hwsku} include dpu npu ports :{sku_dpu_pdu_ports_map[dut_hwsku]}"):
            pytest_assert(set(dpu_npu_ports) == set(sku_dpu_pdu_ports_map[dut_hwsku]),
                          f"For {dut_hwsku}, the expected ports are:{sku_dpu_pdu_ports_map[dut_hwsku]},"
                          f"the actual dpu npu port are {dpu_npu_ports}",)
    elif not dpu_npu_ports:
        pytest.skip("Skip the test due to no dpu npu ports")

    with allure.step("Check interface type for dpu npu port"):
        for intf in dpu_npu_ports:
            pytest_assert(
                intf in intf_status, f"interface {intf} is not in the output of show interface status: {intf_status}")
            pytest_assert(
                intf_status[intf].get('type') == dpu_npu_port_type,
                f"Interface {intf}: The actual type is is {intf_status[intf].get('type')}, "
                f"the expected type is {dpu_npu_port_type}")

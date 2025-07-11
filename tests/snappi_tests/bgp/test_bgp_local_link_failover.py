from tests.common.snappi_tests.snappi_fixtures import (                           # noqa: F401
    snappi_api, snappi_api_serv_ip, snappi_api_serv_port, tgen_ports)
from tests.snappi_tests.bgp.files.bgp_convergence_helper import run_bgp_local_link_failover_test
from tests.common.fixtures.conn_graph_facts import (                        # noqa: F401
    conn_graph_facts, fanout_graph_facts)
import pytest

pytestmark = [pytest.mark.topology('tgen')]


@pytest.mark.parametrize('multipath', [2])
@pytest.mark.parametrize('convergence_test_iterations', [1])
@pytest.mark.parametrize('number_of_routes', [1000])
@pytest.mark.parametrize('route_type', ['IPv4'])
def test_bgp_convergence_for_local_link_failover(snappi_api,                   # noqa: F811
                                                 duthost,
                                                 tgen_ports,                # noqa: F811
                                                 conn_graph_facts,          # noqa: F811
                                                 fanout_graph_facts,        # noqa: F811
                                                 multipath,
                                                 convergence_test_iterations,
                                                 number_of_routes,
                                                 route_type,):
    """
    Topo:
    TGEN1 --- DUT --- TGEN(2..N)

    Steps:
    1) Create BGP config on DUT and TGEN respectively
    2) Create a flow from TGEN1 to (N-1) TGEN ports
    3) Send Traffic from TGEN1 to (N-1) TGEN ports having the same route range
    4) Simulate link failure by bringing down one of the (N-1) TGEN Ports
    5) Calculate the packet loss duration for convergence time
    6) Clean up the BGP config on the dut

    Verification:
    1) Send traffic without flapping any link
       Result: Should not observe traffic loss
    2) Flap one of the N TGEN link
        Result: The traffic must be routed via rest of the ECMP paths

    Args:
        snappi_api (pytest fixture): Snappi Convergence API
        duthost (pytest fixture): duthost fixture
        tgen_ports (pytest fixture): Ports mapping info of testbed
        conn_graph_facts (pytest fixture): connection graph
        fanout_graph_facts (pytest fixture): fanout graph
        multipath: ECMP value
        convergence_test_iterations: number of iterations the link failure test has to be run for a port
        number_of_routes:  Number of IPv4/IPv6 Routes
        route_type: IPv4 or IPv6 routes
    """
    # convergence_test_iterations, multipath, number_of_routes and
    # route_type parameters can be modified as per user preference
    run_bgp_local_link_failover_test(snappi_api,
                                     duthost,
                                     tgen_ports,
                                     convergence_test_iterations,
                                     multipath,
                                     number_of_routes,
                                     route_type,)

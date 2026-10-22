"""
Health-checker tests (M5).

Use short intervals or a fake clock - never sleep 5 real seconds in a test.

  - N consecutive failures ejects a backend; a single blip does not (flap
    damping - write down why in docs/architecture.md)
  - M consecutive successes re-admits it
  - the check timeout is shorter than the interval, and a timeout counts as a
    failure, not a hang
  - ejections and re-admissions are logged and counted

TODO(M5): write these.
"""
from src.pool import Backend

def test_debug_backend():
    print(dir(Backend))

    backend = Backend("b1", "http://localhost")

    print(dir(backend))

    assert hasattr(backend, "mark_success")
    assert hasattr(backend, "mark_failure")
    

def test_backend_marked_unhealthy_after_three_misses():
    backend = Backend(
        name="backend-1",
        url="http://localhost:8001"
    )

    backend.mark_failure()
    backend.mark_failure()

    assert backend.is_alive is True

    backend.mark_failure()

    assert backend.is_alive is False
    assert backend.consecutive_misses == 3
    
    
def test_failure_resets_wins():
    backend = Backend(
        name="backend-1",
        url="http://localhost:8001"
    )

    backend.mark_success()
    backend.mark_success()

    assert backend.consecutive_wins == 2

    backend.mark_failure()

    assert backend.consecutive_wins == 0
    assert backend.consecutive_misses == 1
    
    
def test_success_resets_misses():
    backend = Backend(
        name="backend-1",
        url="http://localhost:8001"
    )

    backend.mark_failure()
    backend.mark_failure()

    assert backend.consecutive_misses == 2

    backend.mark_success()

    assert backend.consecutive_misses == 0
    assert backend.consecutive_wins == 1
    
def test_backend_recovers_after_two_wins():
    backend = Backend(
        name="backend-1",
        url="http://localhost:8001"
    )

    backend.is_alive = False

    backend.mark_success()

    assert backend.is_alive is False

    backend.mark_success()

    assert backend.is_alive is True
    assert backend.consecutive_wins == 2
    
def test_transition_counters():
    backend = Backend(
        "backend-1",
        "http://localhost:8001"
    )

    assert backend.unhealthy_transitions == 0
    assert backend.healthy_transitions == 0

    # Become unhealthy
    backend.mark_failure()
    backend.mark_failure()
    backend.mark_failure()

    assert backend.is_alive is False
    assert backend.unhealthy_transitions == 1

    # Recover
    backend.mark_success()
    backend.mark_success()

    assert backend.is_alive is True
    assert backend.healthy_transitions == 1
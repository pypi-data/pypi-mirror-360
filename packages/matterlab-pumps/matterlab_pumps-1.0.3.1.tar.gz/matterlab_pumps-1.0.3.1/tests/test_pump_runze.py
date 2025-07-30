import pytest
from pathlib import Path
from matterlab_pumps import RunzePump
import time

COM_PORT = "COM5"
def test_init():
    pump = RunzePump(com_port=COM_PORT, address=0, syringe_volume=1e-3, num_valve_port=12)
    assert isinstance(pump, RunzePump)
    assert pump.initialization_status == True
    assert pump.syringe_volume == 1e-3
    assert pump.address == "1"

def test_port():
    pump = RunzePump(com_port=COM_PORT, address=0, syringe_volume=1e-3, num_valve_port=12)
    pump.port = 12
    assert pump.port == 12
    pump.port = 1
    assert pump.port == 1

def test_volume():
    pump = RunzePump(com_port=COM_PORT, address=0, syringe_volume=1e-3, num_valve_port=12)
    assert pump.volume == 0
    pump.volume = 1.0
    assert pump.volume == 1.0
    pump.volume = 0.0
    assert pump.volume == 0

def test_speed():
    pump = RunzePump(com_port=COM_PORT, address=0, syringe_volume=1e-3, num_valve_port=12)
    pump.top_speed_ml = 0.5
    assert 0.499 <= pump.top_speed_ml <= 0.501

def test_draw_dispense():
    pump = RunzePump(com_port=COM_PORT, address=0, syringe_volume=1e-3, num_valve_port=12)
    pump.draw(1.0, 1, speed=0.5)
    assert pump.volume == 1.0
    assert pump.port == 1
    assert 0.499 <= pump.top_speed_ml <= 0.501
    pump.dispense(1.0, 1)
    assert pump.volume == 0.0
    assert pump.port == 1
    assert 0.149 <= pump.top_speed_ml <= 0.151

def test_draw_full_dispense_all():
    pump = RunzePump(com_port=COM_PORT, address=0, syringe_volume=1e-3, num_valve_port=12)
    pump.port = 1
    pump.draw_full()
    assert pump.volume == 1.0
    pump.dispense_all()
    assert pump.volume == 0

def test_draw_and_dispense():
    pump = RunzePump(com_port=COM_PORT, address=0, syringe_volume=1e-3, num_valve_port=12)
    pump.draw_and_dispense(volume=1, draw_valve_port=12, dispense_valve_port=1, speed = 0.5, wait = 10)
    assert pump.port == 1
    assert pump.volume == 0


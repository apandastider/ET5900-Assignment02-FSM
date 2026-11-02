from pathlib import Path
import yaml

def test_station_names():
    f=Path(__file__).resolve().parents[1]/'config'/'stations.yaml'
    data=yaml.safe_load(f.read_text())['stations']
    assert list(data)==['R1','R2','G1','G2','C1']

def test_skeleton_contains_student_work():
    source=(Path(__file__).resolve().parents[1]/'tb4_fsm_assignment'/'student_fsm.py').read_text()
    assert source.count('TODO-STUDENT')>=7

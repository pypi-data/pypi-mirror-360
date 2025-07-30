

from humac_tools.tools import (
    
    correlation,
    analyzeSeasonality,
    getDowntimeCategorizationPareto,
    decodeJwt,
    colorClassification,
    anomaliesDetect,
    paretoAnalysis,
    analyzeGraph,
    optimizedGcode
)


def test_correlation():
    json_data = [
        {"machineid": 1, "feature1": 10, "feature2": 20, "target": 1},
        {"machineid": 1, "feature1": 15, "feature2": 25, "target": 2},
        {"machineid": 2, "feature1": 100, "feature2": 200, "target": 3},
    ]
    result = correlation(json_data, "target")
    assert isinstance(result, list)
    assert "machine id" in result[0]

def test_analyzeSeasonality():
    json_data = [
        {"timestamp": 1633072800000, "target": 10},
        {"timestamp": 1633076400000, "target": 20},
        {"timestamp": 1633080000000, "target": 15},
    ]
    result = analyzeSeasonality(json_data, "target", "H")
    assert isinstance(result, dict)
    assert "trend" in result
    assert "seasonality" in result
    assert "pattern" in result

def test_getDowntimeCategorizationPareto():
    json_data = [
        {"downtime_subtype": "A", "breakdown_time": 50},
        {"downtime_subtype": "B", "breakdown_time": 30},
        {"downtime_subtype": "C", "breakdown_time": 20},
    ]
    result = getDowntimeCategorizationPareto(json_data)
    assert isinstance(result, dict)
    assert len(result) > 0

def test_decodeJwt():
    token = jwt.encode({"https://hasura.io/jwt/claims": {"x-hasura-user-id": "123", "x-hasura-tenant-id": "456", "x-hasura-default-role": "admin"}}, "secret", algorithm="HS256")
    result = decodeJwt(token)
    assert isinstance(result, dict)
    assert result["user_id"] == "123"
    assert result["V2tenant"] == "456"
    assert result["role"] == "admin"

def test_colorClassification():
    assert colorClassification(70, 100, "maximize") == "Green"
    assert colorClassification(50, 100, "maximize") == "Amber"
    assert colorClassification(20, 100, "maximize") == "Red"
    assert colorClassification(20, 100, "minimize") == "Green"

def test_anomaliesDetect():
    json_data = [
        {"machineid": 1, "feature1": 10, "target": 1},
        {"machineid": 1, "feature1": 15, "target": 2},
        {"machineid": 2, "feature1": 100, "target": 3},
    ]
    result = anomaliesDetect(json_data, "target")
    assert isinstance(result, list)
    assert "machine id" in result[0]

def test_paretoAnalysis():
    json_data = [
        {"category": "A", "feature": 50},
        {"category": "B", "feature": 30},
        {"category": "C", "feature": 20},
    ]
    result = paretoAnalysis(json_data, "category", "feature")
    assert isinstance(result, list)
    assert len(result) > 0

def test_analyzeGraph():
    json_data = [
        {"timestamp": 1633072800000, "value": 10},
        {"timestamp": 1633076400000, "value": 20},
        {"timestamp": 1633080000000, "value": 15},
    ]
    result = analyzeGraph(json_data)
    assert isinstance(result, str)
    assert "Peaks" in result or "Lows" in result

def test_optimizedGcode():
    raw_gcode = """
    G0 X0 Y0 Z0
    G1 X10 Y0 Z0
    G1 X10 Y10 Z0
    G1 X0 Y10 Z0
    G1 X0 Y0 Z0
    """
    result = optimizedGcode(raw_gcode)
    assert isinstance(result, dict)
    assert "updated_gcode" in result
    assert "original_distance" in result
    assert "optimized_distance" in result
    assert "distance_reduction" in result
import requests

BASE_URL = "http://localhost:8000"

def test_generate_endpoint():
    url = f"{BASE_URL}/generate"
    params = {
        "temp": 0.7,
        "timsig_n": 4,
        "timsig_d": 4,
        "num_bars": 8,
        "val": "0",
        "den": "med",
        "modl": "transformer"
    }
    response = requests.get(url, params=params)
    assert response.status_code == 200
    data = response.json()
    assert "midi_file" in data
    assert "xml_file" in data
    print("Generate endpoint test passed!")

def test_midi_endpoint():
    url = f"{BASE_URL}/midi"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/midi"
    with open("test_music.mid", "wb") as f:
        f.write(response.content)
    print("MIDI endpoint test passed!")

def test_xml_endpoint():
    url = f"{BASE_URL}/xml"
    response = requests.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    with open("test_sheet.xml", "wb") as f:
        f.write(response.content)
    print("XML endpoint test passed!")


if __name__ == "__main__":
    test_generate_endpoint()
    test_midi_endpoint()
    test_xml_endpoint()
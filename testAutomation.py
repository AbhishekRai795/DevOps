import pytest
import requests

# Define test cases
testcases = [
    ("http://127.0.0.1:8000/add/10/5", 15, "Addition of 10 and 5"),
    ("http://127.0.0.1:8000/subtract/10/5", 5, "Subtraction of 10 and 5"),
    ("http://127.0.0.1:8000/multiply/10/5", 50, "Multiplication of 10 and 5"),
    ("http://127.0.0.1:8000/add/-3/3", 0, "Addition of -3 and 3"),
    ("http://127.0.0.1:8000/multiply/0/5", 0, "Multiplication by zero"),
]

@pytest.mark.parametrize("url, expected, description", testcases)
def test_api(url, expected, description):
    response = requests.get(url)
    result = response.json()["result"]
    assert result == expected, f"{description} FAILED! Expected {expected}, got {result}"
    print(f"{description} PASSED")

if __name__ == "__main__":
    pytest.main()

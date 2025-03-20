from fastapi import FastAPI, HTTPException
import httpx
from collections import deque
import asyncio

app = FastAPI()


WINDOW_SIZE = 10


window_data = {
    "p": deque(maxlen=WINDOW_SIZE),  # Prime
    "f": deque(maxlen=WINDOW_SIZE),  # Fibonacci
    "e": deque(maxlen=WINDOW_SIZE),  # Even
    "r": deque(maxlen=WINDOW_SIZE)   # Random
}


API_URLS = {
    "p": "http://20.244.56.144/test/primes",
    "f": "http://20.244.56.144/test/fibonacci",
    "e": "http://20.244.56.144/test/even",
    "r": "http://20.244.56.144/test/random"
}

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQyNDc1ODE1LCJpYXQiOjE3NDI0NzU1MTUsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjY5MzkwMGFlLWNjYWQtNDAwMC1iZDM1LTEwY2MzOTg3ODVkZCIsInN1YiI6Im1zMjc5MUBzcm1pc3QuZWR1LmluIn0sImNvbXBhbnlOYW1lIjoiU1JNIFVuaXZlcnNpdHkiLCJjbGllbnRJRCI6IjY5MzkwMGFlLWNjYWQtNDAwMC1iZDM1LTEwY2MzOTg3ODVkZCIsImNsaWVudFNlY3JldCI6IlVLWFVpQm5KaHhTTUNmT2MiLCJvd25lck5hbWUiOiJNZWxiYSBTIiwib3duZXJFbWFpbCI6Im1zMjc5MUBzcm1pc3QuZWR1LmluIiwicm9sbE5vIjoiUkEyMjExMDA4MDIwMDM5In0.z3JfvCIXRLkY7JdqZLHZDoxUHo7vd_I3Huu14ahymGw"  # Replace with your actual API key

async def fetch_numbers(category: str):
    """Fetch numbers from third-party API with authorization and a timeout of 500ms"""
    url = API_URLS.get(category)
    if not url:
        return []

    headers = {"Authorization": f"Bearer {API_KEY}"}  

    try:
        async with httpx.AsyncClient(timeout=0.5) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("numbers", [])
            else:
                print(f"API Error: {response.status_code} - {response.text}")
    except (httpx.RequestError, httpx.TimeoutException) as e:
        print(f"Request Error: {str(e)}")
    return []

@app.get("/numbers/{numberid}")
async def get_numbers(numberid: str):
    """Fetch, store unique numbers, maintain window size, and return avg"""
    if numberid not in window_data:
        raise HTTPException(status_code=400, detail="Invalid number ID. Use 'p', 'f', 'e', or 'r'.")

    prev_state = list(window_data[numberid])  
    new_numbers = await fetch_numbers(numberid) 
    
    if new_numbers:
        for num in new_numbers:
            if num not in window_data[numberid]:
                window_data[numberid].append(num)
    
    curr_state = list(window_data[numberid])
    avg_value = round(sum(curr_state) / len(curr_state), 2) if curr_state else 0.0

    return {
        "windowPrevState": prev_state,
        "windowCurrState": curr_state,
        "numbers": new_numbers,
        "avg": avg_value
    }
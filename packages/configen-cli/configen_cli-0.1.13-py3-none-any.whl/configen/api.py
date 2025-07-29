import httpx
import backoff

from configen import system, property, decoder


@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
async def start_session(app_version: str):
    try:
        auth = {"Authorization": f"Bearer {property.CONFIGEN_API_KEY}"}
        data = {
            "app_version": app_version,
            "host_id": property.HOST_ID,
            "system_info": system.get_system_info()
        }
        body = {"data": decoder.compress_and_encode(data)}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{property.CONFIGEN_API_URL}/sessions", headers=auth, json=body, timeout=100.0)
        return response.status_code, decoder.decode_and_decompress(response.json().get("data"))
        if response.status_code == 200:
            return response.status_code, decoder.decode_and_decompress(response.json().get("data"))
        else:
            return response.status_code, {"error": response.text}
    except httpx.RequestError as e:
        print(e)
        return 503, {"error": str(e)}


@backoff.on_exception(backoff.expo, httpx.RequestError, max_tries=3)
async def add_conversation(session_id: str, cli_input: str, cli_input_type: str):
    try:
        auth = {"Authorization": f"Bearer {property.CONFIGEN_API_KEY}"}
        data = {"cli_input": cli_input, "cli_input_type": cli_input_type}
        body = {"data": decoder.compress_and_encode(data)}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{property.CONFIGEN_API_URL}/sessions/{session_id}/conversations", headers=auth, json=body, timeout=100.0)
        if response.status_code == 200:
            return response.status_code, decoder.decode_and_decompress(response.json().get("data"))
        else:
            return response.status_code, {"error": response.text}
    except httpx.RequestError as e:
        print(e)
        return 503, {"error": str(e)}

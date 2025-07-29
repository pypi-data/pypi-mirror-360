import requests
import json
import sys

class MCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def invoke(self, input_text):
        url = f"{self.base_url}/mcp/invoke"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "input": input_text
        }

        try:
            with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as response:
                response.raise_for_status()  # 检查 HTTP 错误

                if "text/event-stream" not in response.headers.get("Content-Type") :
                    print("Unexpected content type:", response.headers.get("Content-Type"))
                    return

                print("Streaming response:")
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data = decoded_line[6:]  # 去除 "data: " 前缀
                            if data.startswith("[ERROR]"):
                                print(f"[ERROR] {data}")
                            else:
                                print(f"Received: {data}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return

def main():
    client = MCPClient(base_url="http://localhost:8000")
    input_text = "Hello, agent!"
    print(f"Sending input: {input_text}")
    client.invoke(input_text)

if __name__ == "__main__":
    main()

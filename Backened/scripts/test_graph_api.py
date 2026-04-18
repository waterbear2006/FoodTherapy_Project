import requests
import json

def test_graph_api(node_name):
    url = f"http://127.0.0.1:8001/api/graph/detail?name={node_name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"--- Graph for {node_name} ---")
            print(f"Nodes count: {len(data['nodes'])}")
            print(f"Links count: {len(data['links'])}")
            if data['nodes']:
                print("First node:", data['nodes'][0])
            if data['links']:
                print("First link:", data['links'][0])
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_graph_api("黄芪")
    test_graph_api("黄芪炖鸡")

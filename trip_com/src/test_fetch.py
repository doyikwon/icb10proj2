import requests
import json

url = "https://kr.trip.com/restapi/soa2/34308/getHotelCommentInfo"

headers = {
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "w-payload-source": "1.0.9@102!Nudtz1KLhCAbOX4SO6An9PKnG2KLOSqZOlbn+6FaG6OaKSbpKET2OSVbOrK2+ET5+rApbbbpOSknKr42+rG2KlqIbEVbKtb5+rbSOEb2KE4p+rKpOr4nKrq/K5bpOSqL+rk/OSKZKrVpQlVROShDKFO3GVd3hbb=",
    "x-ctx-country": "KR",
    "x-ctx-currency": "KRW",
    "x-ctx-locale": "ko-KR",
    "x-ctx-ubt-pageid": "10320668147",
    "x-ctx-ubt-pvid": "7",
    "x-ctx-ubt-sid": "9",
    "x-ctx-ubt-vid": "1754985737191.9877n1SlbHlt",
    "x-ctx-user-recognize": "NON_EU",
    "x-ctx-wclient-req": "0af33fe7acb74bcfe9f82cf404544b46",
    "Content-Type": "application/json"
}

payload = {
    "hotelId": 58635410,
    "commentFilterOptions": {
        "pageIndex": 1,
        "pageSize": 10,
        "repeatComment": 1
    },
    "sceneTypes": ["CommentList"],
    "head": {
        "platform": "PC",
        "cver": "0",
        "cid": "1754985737191.9877n1SlbHlt",
        "bu": "IBU",
        "group": "trip",
        "aid": "",
        "sid": "",
        "ouid": "",
        "locale": "ko-KR",
        "timezone": "9",
        "currency": "KRW",
        "pageId": "10320668147",
        "vid": "1754985737191.9877n1SlbHlt",
        "guid": "",
        "isSSR": False
    }
}

response = requests.post(url, headers=headers, json=payload)
print(response.status_code)
if response.status_code == 200:
    data = response.json()
    print("Response keys:", data.keys())
    # Try to see if comments exist
    comment_list = data.get("comments", [])
    if not comment_list and "data" in data:
        comment_list = data.get("data", {}).get("comments", [])
    if not comment_list and "commentTagList" in data:
        print("Data is structure: ", list(data.keys()))
        print("Response data keys:", data.get('data', {}).keys() if 'data' in data else data.get("ResponseStatus"))
    else:
        print(f"Got {len(comment_list)} comments")
        if comment_list:
            print("First comment:", comment_list[0].get("content"))
else:
    print(response.text)

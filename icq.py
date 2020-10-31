import requests

fileid = "ZH7TKLerOmzrZhlldn03f95f8bf7db1be"
response = requests.get("https://api.icq.net/bot/v1/files/getInfo?token=001.3617003158.0151996798:754693810&fileId="+fileid)
data = response.json()
print(data["url"])
print("https://ub.icq.net/api/v18/files/get/ZH7TKcPe43o36GNlvqY1LBlqY1IbGpF1c84q0Ifjr41I8DvOUIjw8aHSF533k1AES4OIhrNIyGpEb4PslFHLhSrbJOZS3h74jSihpf91iRkD8G7MCYNGE6d5CIDI4h8SKfYxL1Rg9p7SnVN7KSJsF7wsFvvqY1/chunk_002.html")
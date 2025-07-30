space_id = "aaaa"

BASE_URL = "/s/{0}/api/data_views"

print(f"{BASE_URL}".format(space_id))

BASE_URL = "/s/{space_id}/api/data_views"

print(f"{BASE_URL}".format(space_id=space_id))

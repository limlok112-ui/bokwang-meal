import datetime
import os
import requests

API_KEY = os.environ.get("NEIS_API_KEY")
KAKAO_ACCESS_TOKEN = os.environ.get("KAKAO_ACCESS_TOKEN")
school_name = "보광고등학교"

today = datetime.datetime.now().strftime("%Y%m%d")

try:
  # 1. 학교 코드 조회
  info_url = "https://open.neis.go.kr/hub/schoolInfo"
  info_params = {"KEY": API_KEY, "Type": "json", "SCHUL_NM": school_name}
  info_res = requests.get(info_url, params=info_params).json()

  school_row = info_res["schoolInfo"][1]["row"][0]
  atpt_code = school_row["ATPT_OFCDC_SC_CODE"]
  sd_code = school_row["SD_SCHUL_CODE"]

  # 2. 급식 정보 조회 (중식, 석식)
  meal_url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
  meal_types = {"2": "중식", "3": "석식"}
  message = f"📌 [{today}] {school_name} 급식 메뉴\n"

  for code, name in meal_types.items():
    meal_params = {
        "KEY": API_KEY,
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": atpt_code,
        "SD_SCHUL_CODE": sd_code,
        "MLSV_YMD": today,
        "MMEAL_SC_CODE": code,
    }
    meal_res = requests.get(meal_url, params=meal_params).json()

    message += f"\n[ {name} ]\n"
    if "RESULT" in meal_res:
      message += "급식 정보가 없습니다.\n"
    else:
      row_data = meal_res["mealServiceDietInfo"][1]["row"]
      meal_menu = row_data[0]["DDISH_NM"].replace("<br/>", "\n")
      message += f"{meal_menu}\n"

  # 3. 카카오톡 나에게 보내기 (form-urlencoded 방식으로 전송)
  import json

  kakao_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
  headers = {"Authorization": f"Bearer {KAKAO_ACCESS_TOKEN}"}
  template_object = {
      "object_type": "text",
      "text": message,
      "link": {
          "web_url": "https://developers.kakao.com",
          "mobile_web_url": "https://developers.kakao.com",
      },
  }
  data = {"template_object": json.dumps(template_object)}

  res = requests.post(kakao_url, headers=headers, data=data)
  if res.status_code == 200:
    print("카카오톡 전송 완료!")
  else:
    print(f"카카오톡 전송 실패: {res.text}")

except Exception as e:
  print(f"오류 발생: {e}")

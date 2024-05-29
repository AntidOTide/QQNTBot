import requests
from datetime import datetime
from datetime import timedelta
from datetime import timezone


def download_img(url):
    img_src = url
    response = requests.get(img_src)
    date = get_bj_time()
    print(date)
    file_url = "D:\\Programming\BOT\QBot2号\py\\fonts\pic\\"+ date + ".jpg"
    with open(file_url, 'wb+') as file_obj:
        file_obj.write(response.content)
    return file_url


def get_bj_time():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    # 北京时间
    beijing_now = utc_now.astimezone(SHA_TZ)
    fmt = '%Y-%m-%d-%H-%M-%S'
    now_fmt = beijing_now.strftime(fmt)
    return now_fmt


url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-RTktDeP5gyPhK2qDvARsPqxy/user-0su9I5uTK8mAAMoZaEDMRjf1/img-ZN09mxO0gKeEPu9UeH99jMZS.png?st=2024-01-09T07%3A39%3A28Z&se=2024-01-09T09%3A39%3A28Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-01-09T06%3A30%3A35Z&ske=2024-01-10T06%3A30%3A35Z&sks=b&skv=2021-08-06&sig=R1VKiXwBfRl2XxAhswSZ2gHxLjEJ0My9pB8MkkajqGU%3D"

download_img(url)

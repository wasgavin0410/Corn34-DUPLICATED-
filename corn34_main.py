import requests
from bs4 import BeautifulSoup
import os
import sys
from tqdm import tqdm
import re

def replaceBlank(str):
    if " " in str:
        str = str.replace(" ", "_")
        return str

#TODO should i download pictures in original size?

while(True):
    try:
        main_tag = input("輸入你所要尋找的主要標籤(MAIN TAG)，你也可以透過繪師名稱搜尋：") or "NO"

        if (main_tag == ("NO" or "no")):
            sys.exit()
    except(SyntaxError, ValueError, UnicodeDecodeError):
        print("你所輸入的是錯誤的資料，或者是你可能輸入到非英文語系的字元")
        print("請再輸入一次")
        continue
    else:
        print("已將MAIN TAG資料存入\n")
        break

current_page = "http://rule34.xxx/index.php?page=post&s=list&tags=" + replaceBlank(main_tag)
array_of_tags = []

additional_tag = str()
additional_negative_tag = str()

print("==============================================")

try:
    while(additional_tag != ("NO" or "no")):
        additional_tag = input("你會想要加入其他想要的TAG嗎？\n(若無，則留白。注意若輸入其他MAIN TAG(如角色名稱、繪師名稱)會導致系統錯誤)\n") or "NO"
        if (additional_tag != ("NO" or "no")):
            if (additional_tag not in array_of_tags):
                array_of_tags.append("+" + replaceBlank(additional_tag))
            else:
                print("TAG不可重複！")
                continue
except (SyntaxError, ValueError, UnicodeDecodeError):
    print("資料輸入錯誤！\n")

try:
    while(additional_negative_tag != ("NO" or "no")):
        additional_negative_tag = input("你會想要加入其他「你不想看到」的TAG嗎？\n(若無，則留白。注意若輸入其他MAIN TAG(如角色名稱、繪師名稱)會導致系統錯誤)\n") or "NO"
        if (additional_negative_tag != ("NO" or "no")):
            if (additional_negative_tag not in array_of_tags):
                array_of_tags.append("+-" + replaceBlank(additional_negative_tag))
            else:
                print("TAG不可重複！")
                continue
except (SyntaxError, ValueError, UnicodeDecodeError):
    print("資料輸入錯誤！\n")



print("\n我們檢查一次吧！你的主要標籤(MAIN TAG)是：" , main_tag, "\n並且你的追加標籤是： ")
for elem in array_of_tags:
    current_page += elem
    print(elem, "")

print("\n它們在整合之後將得到以下網址：", current_page)
confirm = input("這個結果是正確的嗎？(若非，則留白)\n") or "NO"
if (confirm == ("NO" or "no")):
    sys.exit()
else:
    range_confirm = input("你會想要為這筆資料的爬蟲設定範圍嗎？ (若無，則留白)") or "NO"
    if (range_confirm != ("NO" or "no")):
        while(True):
            try:
                lastNum = int(input("請在這裡輸入你所想要設下的搜尋範圍(輸入最後一頁即可)"))
            except (SyntaxError, ValueError, UnicodeDecodeError):
                print("資料輸入錯誤！")
                continue
            else:
                break
    else:
        #若使用者沒有手動輸入檢索的最終頁面，則系統自動搜尋該搜尋結果的最終頁面
        request = requests.get(current_page)
        soup = BeautifulSoup(request.text, "html.parser")
        find_last_page = soup.find("div", class_ = "pagination").find("a", alt = "last page")["href"]
        regualtion = re.compile(r"\d+")

        getPID = regualtion.search(find_last_page)
        lastNum = int(getPID.group())//42
        
        #透過正規運算式"\d+" 找出二位數以上的整數

print("\n頁數的最終檢索範圍將是：%d\n    即將開始執行(若想要終止程式，請按下「Ctrl+C」)" %lastNum)
print("==============================================")

#Started

basePID = 0
savedURL = []

#網站架構：搜尋結果第一頁為rule34.xxx/index.php?page=post&s=list&tags= {搜尋的TAG} + {其他的TAG}   TAG支援複數
#TAG支援「排除特定TAG」。寫法為{"+-標籤名稱"}，如"+-guru"
#第二頁之後在後面追加"&pid={42*n}"  每一頁+=42

for i in range(lastNum): 
    print("You're now at :", current_page)
    print("==============================================")

    request = requests.get(current_page)
    soup = BeautifulSoup(request.text, "html.parser")
    # 若迴圈在第一層，因為前面已有要求過一次該頁面的request因此不再贅述
    sel = soup.select("div.content div span.thumb a")
    #如剝洋蔥一般  找到每個thumbnail它背後的LINK  之後儲存進陣列

    for each in sel:
        link = "http://rule34.xxx/" + each["href"]
        #將找到的link與網域concat
        #進入縮圖的link後  進行新的request
        second_request = requests.get(link)
        sec_soup = BeautifulSoup(second_request.text, "html.parser")
        result = sec_soup.find("div", class_="content").find("img")["src"]
        print(result)
        savedURL.append(result)
        #save image's url into the array

    print("==============================================")
    basePID += 42
    next_page = "http://rule34.xxx/index.php?page=post&s=list&tags=" + main_tag + "&pid=" + str(basePID)
    current_page = next_page

#將所有網址加入陣列之後，開始進行下載作業
if not os.path.exists(main_tag):
    os.mkdir(main_tag)
#創立資料夾， 若目錄底下存在則不創立

index = 0

for sauce in tqdm(savedURL):
    img = requests.get(sauce)

    #Dir = "H:\\...\\python crawler\\tag name\\tag name[index].png"
    #只會以MAIN TAG作為檔名，後續追加的正負TAG不會加入
    with open(main_tag + "\\" + main_tag + str(index) + ".png", "wb") as file:
        file.write(img.content)
    index += 1

    # Complete by using TQDM! TO-DO: progress bar
    #TODO: Check what will happen if the crawler encounters MP4 file?
    #-> it will get the "Buy the T-shirt" jpg instead!!

print("...Complete!")

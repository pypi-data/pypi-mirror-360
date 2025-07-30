import json
# import gradio as gr
import random
# from pathlib import Path
from mcp.server import FastMCP


mcp = FastMCP("xiaohongshu_mcp")

# gr.set_static_paths(paths=[Path.cwd().absolute()/"assets"])
# 模拟返回数据
all_results_meizhuang = [{'title': '📝美妆课笔记002 | 超详细底妆思路和步骤', 'author': '嘉南', 'image_url': 'fbd31fc7b0693c2a17942fc288e63df6.jpg', 'link': 'http://xhslink.com/a/CBFHW3mIV2ugb', 'description': '纯手工制作，价值1w+的化妆笔记分享给大家。简单详细全面的底妆知识，新手易学。'},
                         {'title': '留意这三个美妆博主，6.4号的笔记点赞爆啦', 'author': '小星妆造ip研究所📚', 'image_url': '4b6b7db8b24ebd434cbc6d23187b7005.jpg', 'link': 'http://xhslink.com/a/U2MeeGvE63ugb', 'description': '每日学习一点点，增加网感，下一个爆火的就是你啦。'},
                         {'title': '扁平淡颜来化ins早八韩妆！10min速成！可跟练', 'author': '被告张三', 'image_url': '853f111d9e783d099af9c16273c716f7.jpg', 'link': 'http://xhslink.com/a/KcV09xHaH4ugb', 'description': '我宣布韩女的淡妆就是最适合早八的！'},
                         {'title': '南京美妆私教课笔记/赶在五一前上完了', 'author': '不忌口的小梁', 'image_url': 'd06a2437b60118deb91fcfef98e9f2ef.jpg', 'link': 'http://xhslink.com/a/SsDVXtNBd5ugb', 'description': '记录2025年4.30，有上课的好物分享。'},
                         {'title': '新手从0-1保姆级跟练化妆教程', 'author': '天天5分钟化妆', 'image_url': '86ae335b9494c135f349e30fbf7a482f.jpg', 'link': 'http://xhslink.com/a/lfmoAQS0Q5ugb', 'description': '新手化妆步骤、教程，适合零基础入门。'},
                         {'title': '上周（2.24-3.2）🔥的10篇美妆笔记📓', 'author': '可可的陪跑笔记', 'image_url': '8f02a60f4bbbebc8c90d7962c6050667.jpg', 'link': 'http://xhslink.com/a/3AOUzMtrn6ugb', 'description': '宝子们，又到了一周美妆爆文盘点时刻啦！可可这次整理的10篇笔记，都来自粉丝量不高但数据超厉害的账号。'},
                         {'title': '手把手跟练ins白女妆容，直接换人种了…', 'author': '阿里北杯', 'image_url': '3db9232c3e662f829bdc28230d7071f5.jpg', 'link': 'http://xhslink.com/a/Ys8XHOwwK6ugb', 'description': '手把手跟练ins白女妆容，直接换人种了…'},
                         {'title': '超详细底妆复盘记录', 'author': '蒋蒋豇豇', 'image_url': '2b0ac43db9ffe67f78b06ed6ba9077a7.jpg', 'link': 'http://xhslink.com/a/r6CaXmICf7ugb', 'description': '根据喜欢的美妆博主的教程以及化妆中发现的问题，在小红书上狠狠钻研并实践后诞生的笔记。'},
                         {'title': '在韩化妆私教课｜美妆笔记分享', 'author': '徐江美妆', 'image_url': '09c5254cacd57c6f6c1281ca3aa10ac1.jpg', 'link': 'http://xhslink.com/a/Qwb0mMcdj9ugb', 'description': '通过色彩的底层逻辑，让大家正确找对适合自己的色彩。'},
                         {'title': '沉浸式/4min跟练 肿内双🪆俄式洋娃娃🧸妆', 'author': '饼干不吃夹心的', 'image_url': '209af226c115ffda98149d6ae21e9e07.jpg', 'link': 'http://xhslink.com/a/RzzwzoC1A9ugb', 'description': '沉浸式化妆，适合普通人跟练。'},
                         {'title': '旅游四天❗️三天都在化的无睫毛版懒人上镜妆', 'author': '裴幸運', 'image_url': '9b4ac6049caa1bcaa958bf00e61ba689.jpg', 'link': 'https://www.xiaohongshu.com/search_result/66744cea000000001c036333?xsec_token=ABen8V9Me5kEOM4VEySOQQRolq4f_9t23aBspEsTFYLQ4=&xsec_source=', 'description': '旅游四天，三天都在用的无睫毛版懒人上镜妆，适合海边，不怕风吹掉假睫毛，轻松打造松弛感妆容。'},
                         {'title': '黄黑皮海岛度假亚裔妆容🏝️雀斑好有生命力', 'author': '哥是冷酷暗夜杀手', 'image_url': '2d30f2c9a21550d414f9355e6cb2c8d5.jpg', 'link': 'https://www.xiaohongshu.com/search_result/6724c91e000000001a035b48?xsec_token=ABLADTuXY7PiSew8d-J4BlWaj_m4I4rDeJuG6vchZ9Ci4=&xsec_source=pc_search', 'description': '适合黄黑皮的海岛度假妆容，突出雀斑妆感，打造自然生命力感，轻松驾驭海边度假氛围。'},
                         {'title': '✨浪屿海岸🌊夏日度假氛围感眼妆教程', 'author': '一打冰茶', 'image_url': '0bef768097c66913658c115f68e58711.jpg', 'link': 'https://www.xiaohongshu.com/search_result/66664f01000000000f00f31a?xsec_token=AB_mJnDUx83WyM0dUAN5M2OxkKYjSM8oPe9mrhe5Qz53g=&xsec_source=pc_search', 'description': '清新感满满的清凉小撞色眼妆，适合海边度假，日常又吸睛，轻松打造夏日度假氛围。'},
                         {'title': '沁爽柠檬🏝️海岛度假妆教程', 'author': '芒果柚柚子', 'image_url': '640b1d8f97f2c1f6bd1a1d809ff10e52.jpg', 'link': 'https://www.xiaohongshu.com/search_result/6808a16e000000001c02e190?xsec_token=ABWkNUdMgeui1wqO4kbgERc4IJ_jUo9Rh98fAV5GT2SYI=&xsec_source=pc_search', 'description': '黄蓝撞色妆容，像盛夏的冰柠檬汽水，适合海岛度假，清新又吸睛，打造视觉降温妆。'},
                         {'title': '妆教|夏日欧若妆🐚\U0001fae7去薄荷味海边度假啦～', 'author': '羊角羔', 'image_url': '86873071aa9b4e36a19057804c2e2141.jpg', 'link': 'https://www.xiaohongshu.com/search_result/682702a60000000020029e44?xsec_token=ABQ9X80rLeKxY0MfxZFItueh8vpYNQI45Ift6Kyugd6BY=&xsec_source=pc_search', 'description': '薄荷味夏日妆容，打造清新海边度假氛围，适合夏季出游，妆感自然又不失精致。'},
                         {'title': '𝑀𝑎𝑘𝑒 𝑢𝑝 / 海岛度假清透妆', 'author': '了了or', 'image_url': 'a6f50b0f5cb95b30ac0c770db7409b4e.jpg', 'link': 'https://www.xiaohongshu.com/search_result/66a4f761000000000600ea95?xsec_token=ABNo4LN7BOYIHZH5EufW3C6CdHNP5qQCrz_jrVl6Hi_xM=&xsec_source=pc_search', 'description': '五分钟快速海岛妆容，腮红+野生眉，打造水光肌感，适合海边度假轻松上妆。'},
                         {'title': '妆教|五一出游的老婆看过来！海边🏝️出游妆', 'author': '小帆bu烦', 'image_url': 'd01095de2e53390d1df53425d2314f70.jpg', 'link': 'https://www.xiaohongshu.com/search_result/6805002f000000001202d884?xsec_token=ABp7j62ygAEditBtyQaqsrAyZU2rkEvBv7hajyiWjZGrs=&xsec_source=pc_search', 'description': '五一假期出游妆容，适合海边度假，妆容自然，适合日常出游轻松打造。'},
                         {'title': '快来画这种海岛🏝️度假亚裔妆容', 'author': 'IZZO', 'image_url': '537764f9e37a6b13b6c05f940c943b2e.jpg', 'link': 'https://www.xiaohongshu.com/search_result/6800acbb000000000b02f931?xsec_token=ABy0W7Czbj1M2HkNSMnFvHIB288mdUxDnnZADS9D-ztn4=&xsec_source=pc_search', 'description': '海岛度假妆容，突出生命力感，搭配小花花元素，适合海边拍照，妆容自然又吸睛。'},
                         {'title': '方圆脸都来学生命力旺盛🌸海岛亚裔妆🏝️☀️', 'author': '胖头鱼（女强人版）', 'image_url': '432e7b9b3b396b9e33be7ff71f8f3ffb.jpg', 'link': 'https://www.xiaohongshu.com/search_result/67b9a2e2000000000900f9b3?xsec_token=ABUReiSILzmsa-yjX7SkNxASkYeIufmVMxzUuhi3KDDFM=&xsec_source=pc_search', 'description': '适合方圆脸的海岛妆容，突出亚裔妆感，打造自然阳光感，适合海边度假拍照。'},
                         {'title': '初恋红豆饼 | 海岛晒伤妆 | 夏日度假风妆容🌴', 'author': '初恋红豆饼', 'image_url': '1edac95296260a67cf2d2773daeffc1f.jpg', 'link': 'https://www.xiaohongshu.com/search_result/67fe4c04000000001e00982e?xsec_token=AB9-QaOQxeNbT1uzl0Ua2T5DNelAEf8-nJXC-gC3abZwo=&xsec_source=pc_search', 'description': '海岛晒伤妆容，打造夏日度假氛围，适合海边度假妆，妆容自然又不失夏日感。'},
                         {'username': '撒拉', 'title': '美学', 'link': 'https://www.xiaohongshu.com/search_result/66d9aefb000000001e0193ec?xsec_token=ABxjkh7T6vUrU-nHerAHLD7Lp6v1vFWjr0nUBGdnPPcOw=&xsec_source=', 'brief': '今年夏天最火的妆是什么？轻泰妆夏天最火的妆容是什么？绝对是轻泰妆，美得很明艳大气...', 'likes': 161, 'bookmarks': 137, 'author': '撒拉', 'description': '今年夏天最火的妆是什么？轻泰妆(https://www.xiaohongshu.com/search_result/66d9aefb000000001e0193ec?xsec_token=ABxjkh7T6vUrU-nHerAHLD7Lp6v1vFWjr0nUBGdnPPcOw=&xsec_source=)', 'image_url': '1611748255905_.pic_thumb.jpg'},
                         {'username': 'January婧', 'title': '权威泰妆！邝玲玲浓颜骨相泰妆', 'link': 'https://www.xiaohongshu.com/search_result/681f4a81000000002001ec93?xsec_token=ABoyuldRpBmbNPHyxFNPOW7CONSHvOtkXiMfoM14Qznag=&xsec_source=pc_search', 'brief': '权威泰妆！邝玲玲浓颜骨相泰妆', 'likes': 5303, 'bookmarks': 0, 'author': 'January婧', 'description': '精致建模感(https://www.xiaohongshu.com/search_result/681f4a81000000002001ec93?xsec_token=ABoyuldRpBmbNPHyxFNPOW7CONSHvOtkXiMfoM14Qznag=&xsec_source=pc_search)', 'image_url': '1571748255902_.pic_thumb.jpg'},
                         {'username': 'kyra杨可', 'title': '邝玲玲仿妆！娇憨感清透泰妆全妆跟练', 'link': 'https://www.xiaohongshu.com/search_result/68285ba8000000002301250b?xsec_token=AB7Q-sJLQwEGVoUqR7MwtfF0emInXSVVCMke838uQaj0c=&xsec_source=pc_search', 'brief': '', 'likes': 4415, 'bookmarks': 2614, 'author': 'kyra杨可', 'description': '邝玲玲仿妆！娇憨感清透泰妆全妆跟练...(https://www.xiaohongshu.com/search_result/68285ba8000000002301250b?xsec_token=AB7Q-sJLQwEGVoUqR7MwtfF0emInXSVVCMke838uQaj0c=&xsec_source=pc_search)', 'image_url': '1601748255904_.pic_thumb.jpg'},
                         {'username': '元小双', 'title': '邝玲玲ins娇憨感泰妆', 'link': 'https://www.xiaohongshu.com/search_result/68231f1e000000002100922e?xsec_token=ABigV5uf2aWOqIJbZlT0jXGwnvZQYD1NNHayvkrcpuyfQ=&xsec_source=pc_search', 'brief': '', 'likes': 0, 'bookmarks': 0, 'author': '元小双', 'description': '邝玲玲ins娇憨感泰妆骨相和韩系色彩的结合，一眼惊艳！...(https://www.xiaohongshu.com/search_result/68231f1e000000002100922e?xsec_token=ABigV5uf2aWOqIJbZlT0jXGwnvZQYD1NNHayvkrcpuyfQ=&xsec_source=pc_search)', 'image_url': '1561748255901_.pic_thumb.jpg'},
                         {'username': '羊土豆豆腐', 'title': '刘诗诗高智感美女', 'link': 'https://www.xiaohongshu.com/search_result/66d9263d000000001f039478?xsec_token=ABxjkh7T6vUrU-nHerAHLD7BMAfn92a9kaczXtOJqukp4=&xsec_source=pc_search', 'brief': '', 'likes': 991, 'bookmarks': 223, 'author': '羊土豆豆腐', 'description': '轻松get刘诗诗同款轻泰妆...(https://www.xiaohongshu.com/search_result/66d9263d000000001f039478?xsec_token=ABxjkh7T6vUrU-nHerAHLD7BMAfn92a9kaczXtOJqukp4=&xsec_source=pc_search)', 'image_url': '1631748255907_.pic_thumb.jpg'},
                         {'username': '耶耶耶', 'title': '小水ins更新：这个妆造太美了吧🖤🖤', 'link': 'https://www.xiaohongshu.com/search_result/6731b870000000001b02fdab?xsec_token=ABe8MnVEXE_muD3_eTVH8984hsjLlKY43uQWXp2kW35Uw=&xsec_source=pc_search', 'brief': '', 'likes': 87, 'bookmarks': 27, 'author': '耶耶耶', 'description': '小水ins更新：这个妆造太美了吧🖤🖤...(https://www.xiaohongshu.com/search_result/6731b870000000001b02fdab?xsec_token=ABe8MnVEXE_muD3_eTVH8984hsjLlKY43uQWXp2kW35Uw=&xsec_source=pc_search)', 'image_url': '1541748255898_.pic_thumb.jpg'},
                         {'username': '华天崎', 'title': '给林允化的轻泰妆，妆教来啦，好美好闪！', 'link': 'https://www.xiaohongshu.com/search_result/6672c7b9000000001d0140df?xsec_token=ABZx3a08NBCKhCmuv4zQIS0pGXbWqgsyJOydfIvyM_hQ=&xsec_source=pc_search', 'brief': '', 'likes': 8697, 'bookmarks': 4986, 'author': '华天崎', 'description': '给林允化的轻泰妆，妆教来啦，好美好闪！...(https://www.xiaohongshu.com/search_result/6672c7b9000000001d0140df?xsec_token=ABZx3a08NBCKhCmuv4zQIS0pGXbWqgsyJOydfIvyM_hQ=&xsec_source=pc_search)', 'image_url': '1591748255904_.pic_thumb.jpg'},
                         {'username': '高雯A-WEN', 'title': '美到失语！邝玲玲浓颜系泰妆', 'link': 'https://www.xiaohongshu.com/search_result/682c9082000000000f038878?xsec_token=AB8bEdTijpv_otkRHz4a9FNUkrpxwYxrEYJrgLs20GCEk=&xsec_source=pc_search', 'brief': '又韩又泰的一张脸～画好了直接一个换头的大动作...', 'likes': 1861, 'bookmarks': 853, 'author': '高雯A-WEN', 'description': '全妆跟练版(https://www.xiaohongshu.com/search_result/682c9082000000000f038878?xsec_token=AB8bEdTijpv_otkRHz4a9FNUkrpxwYxrEYJrgLs20GCEk=&xsec_source=pc_search)', 'image_url': '1551748255899_.pic_thumb.jpg'},
                         {'username': '🐰顽皮斯_', 'title': '仿妆？仿的就是邝玲玲妆容！', 'link': 'https://www.xiaohongshu.com/search_result/68234b1b000000000303d99b?xsec_token=ABigV5uf2aWOqIJbZlT0jXG5sI-cYfIfY9HuD7vgkRJB8=&xsec_source=pc_search', 'brief': '', 'likes': 20, 'bookmarks': 9, 'author': '🐰顽皮斯_', 'description': '清冷贵气感的泰妆真的好美啊～直接焊在脸上可以吗！...(https://www.xiaohongshu.com/search_result/68234b1b000000000303d99b?xsec_token=ABigV5uf2aWOqIJbZlT0jXG5sI-cYfIfY9HuD7vgkRJB8=&xsec_source=pc_search)', 'image_url': '1581748255903_.pic_thumb.jpg'},
                         {'username': '刘诗诗的竹室（淮水竹亭赴约版）', 'title': '刘诗诗的轻泰妆果然有它独特的魅力', 'link': 'https://www.xiaohongshu.com/search_result/66de68a30000000027005e3e?xsec_token=ABNa4q4fc30Z0L1C1pDZ3Zp_LhzcB9_W9Krw8w5oW0Wtw=&xsec_source=pc_search', 'brief': '', 'likes': 0, 'bookmarks': 0, 'author': '刘诗诗的竹室（淮水竹亭赴约版）', 'description': '有人能懂吗？！！诗诗的轻泰妆真的很有特色又突出美貌...(https://www.xiaohongshu.com/search_result/66de68a30000000027005e3e?xsec_token=ABNa4q4fc30Z0L1C1pDZ3Zp_LhzcB9_W9Krw8w5oW0Wtw=&xsec_source=pc_search)', 'image_url': '1621748255906_.pic_thumb.jpg'}]
all_results_chuanda = [{'title': '30套早春通勤穿搭✨气质温柔～不露腿也很好看', 'author': '叫我O老师', 'image_url': '4dd9fa92afcc54f1117924616cd63e4e.webp', 'link': 'https://www.xiaohongshu.com/search_result/67d841e5000000000703505c?xsec_token=ABzr-f55eGN8uWm09BCx4RLwsn_yn-6DUcxpQpTcFebgc=&xsec_source=pc_search', 'description': '30套早春通勤穿搭✨气质温柔～不露腿也很好看 #教师穿搭 #通勤穿搭 #日常通勤穿搭 #一周通勤不重样 #温柔知性穿搭 #简约穿搭 #心动浅春系 #连衣裙 #衬衫 #半身裙'},
                       {'title': '美到犯规！哥弟蓝格纹衬衫✨法式优雅的代名词', 'author': '阿玛施GIRDEAR哥弟服装店', 'image_url': 'fcccf3d1fbe5b4da55d7446f2642767d.webp', 'link': 'https://www.xiaohongshu.com/search_result/680103ef000000001d0251e4?xsec_token=ABBzFNwMA-iHCwh7O8Ar1N8FrS6AomsrhJSw6Awg9JR1A=&xsec_source=pc_search', 'description': '宝子们，被这件短袖衬衫拿捏了！泡泡袖俏皮可爱，像是藏着少女心事，荷叶边轻盈灵动，走路都带风。黑白条纹经典不过时，怎么搭都不会出错。#哥弟 #阿玛施 #春日秀场 #浅春系穿搭 #小红书RFL时尚轻单'},
                       {'title': '不同科目教师怎么穿❓一周显瘦通勤不露腿', 'author': '独角兽的粉粉', 'image_url': '74957e27a8c017eaccc840ba1d2cc990.webp', 'link': 'https://www.xiaohongshu.com/search_result/67d91ecb000000001d023522?xsec_token=ABV8ASA1FWB__6LkfCb1SKuicJxBthVOJZBIVn1YeAaHQ=&xsec_source=pc_search', 'description': '不同科目教师怎么穿❓一周显瘦通勤不露腿 #通勤穿搭 #衬衫 #韩系穿搭 #教师穿搭 #一周穿搭不重样 #日常通勤穿搭 #书卷气穿搭 #体制内穿搭 #不露腿穿搭 #初入职场穿搭'},
                       {'title': '美貌如黄亦玫 也经不住生活的消磨|35+智感', 'author': '乔万尼的穿搭日记', 'image_url': '4f9465f453e9009958d3ed01de505bf5.webp', 'link': 'https://www.xiaohongshu.com/search_result/6679624b000000001e011613?xsec_token=ABgHU573_01SY5UGOAQi_glt3b-Q_aFVzDPH5OeAubY0Q=&xsec_source=pc_search', 'description': '美貌如黄亦玫 也经不住生活的消磨|35+智感 #黄亦玫穿搭 #玫瑰的故事 #刘亦菲 #明星穿搭回归现实 #跟着明星学穿搭'},
                       {'title': '不露腿的一周通勤穿搭～这几套都好好看喔', 'author': '小C呢', 'image_url': '62e9ceafa9cd589b8226bc23cefd318b.webp', 'link': 'https://www.xiaohongshu.com/search_result/66ae1a5e00000000090175ee?xsec_token=AB6zx-iQzF0vWBXHPfJGV14LLzjFGrJMgyOqjd5P_EKSc=&xsec_source=pc_search', 'description': '不露腿的一周通勤穿搭～这几套都好好看喔 #职场通勤穿搭 #温柔通勤气质穿搭 #穿搭合集 #今日look #不露腿穿搭 #通勤穿搭 #我的上班通勤穿搭 #一周#一周tong\u2006q#一周穿搭不重样'},
                       {'title': '平价🛒分享/月光族 通勤一周ootd', 'author': '猪丽叶👗', 'image_url': 'ca46cd2c4aa07e640772d2f611357e1b.webp', 'link': 'https://www.xiaohongshu.com/search_result/6831436a000000002301ff0f?xsec_token=ABSF3KxATmJtn1anIdAKIryqvY_dM6uhPxlk5SZ3pNOMw=&xsec_source=pc_search', 'description': '平价🛒分享/月光族 通勤一周ootd #穿搭合集 #平价穿搭 #穿搭好物 #一周通勤不重样 #平价但不廉价 #打工人的多面时尚 #鞋子推荐 #包包分享 #日常通勤穿搭 #日常穿搭'},
                       {'title': '150斤live｜关于我月收入5500通勤穿搭18套', 'author': '一大坨答辩', 'image_url': 'dc7c5bd4ae4e1c2b08ecc5fb7ca17581.webp', 'link': 'https://www.xiaohongshu.com/search_result/66e01665000000002503349f?xsec_token=ABsf4Q4NJvneYdZYCWzUHl3UFRslGaAvkBxleyTyU5IKM=&xsec_source=pc_search', 'description': '150斤live｜关于我月收入5500通勤穿搭18套 #新年新look #ootd每日穿搭 #大码穿搭 #宝宝辅食 #笔记灵感 #穿搭合集 #通勤穿搭 #秋季穿搭 #国庆 #显瘦穿搭'},
                       {'title': 'MM/麦檬 出游度假穿搭，这样穿也太好看了吧', 'author': 'MM麦檬集合店', 'image_url': '9b26c6d17155546b520e3e357b44e41b.webp', 'link': 'https://www.xiaohongshu.com/search_result/681a05860000000022028c40?xsec_token=ABcfRkkYZLfS5iZtKbJTfL61jhGaKiTiaKnQLSO-dwXMM=&xsec_source=pc_search', 'description': 'MM/麦檬 出游度假穿搭，这样穿也太好看了吧 #MM麦檬 #度假风穿搭 #小个子穿搭 #蓝色系 #小个子穿搭 #出游穿搭 #显瘦穿搭 #韩系女装'},
                       {'title': '40套合集|职场通勤穿搭推荐', 'author': '莉莉时尚', 'image_url': 'c2d611e9ebba8d69a5aa76e1da7e3cf0.webp', 'link': 'https://www.xiaohongshu.com/search_result/665dcf9100000000050076f8?xsec_token=AB32dWQTFejjbRuc19J3vnnWqaPR6-a7eB5hRqqDM1SjI=&xsec_source=pc_search', 'description': '40套合集|职场通勤穿搭推荐 #通勤风穿搭 #职场通勤穿搭 #温柔通勤气质穿搭 #一衣多搭 #穿搭合集 #穿搭干货 #挑战一周穿搭不重样 #实用穿搭 #穿搭技巧 #简约穿搭'},
                       {'title': '🔥早八人必看 | 5套「懒人通勤穿搭」❗️❗️❗️', 'author': '爱穿搭的小白', 'image_url': '20e5bece8004dcea70e1039f0cf4fa2b.webp', 'link': 'https://www.xiaohongshu.com/search_result/67e2c115000000001e004634?xsec_token=AB7olEZjCS1tmii1NzoiMI2AcKmYVhQT9yLqogy-fyOX0=&xsec_source=pc_search', 'description': '哈喽姐妹，我是爱穿搭的小白！\U0001faf6🏻 早八人的痛啊！每天多睡10分钟比啥都强🤯 今天分享我的5套「零思考穿搭公式」，全是基础款混搭！ #小红书时装周群聊 #通勤穿搭 #OOTD #早八人 #穿搭技巧 #搭配技巧 #一周通勤不重样 #通勤风穿搭 #打工人的多面时尚 #穿搭'}]
all_results_hufu = [{'title': '快看！不同年龄段如何护肤？护肤步骤大公开', 'author': 'life engines 倩之密', 'image_url': '17c03d72495ac50ff8aedc1817b69e4a.webp', 'link': 'https://www.xiaohongshu.com/search_result/67d7e1f4000000000e004a21?xsec_token=ABuPz6htK3TBWtXx5rXilPri4DRrW7bJamCS9xmubcUNc=&xsec_source=', 'description': '提供了针对不同年龄段（12-18岁、19-24岁、25-30岁、30岁以上）的护肤重点和详细步骤，包括清洁、保湿、防晒及抗老建议。'},
                    {'title': '不同年龄段的不同护肤攻略，看看你是哪种吧', 'author': '汀兰', 'image_url': 'a6acb26ee984c0d8f2b1fcdbd05a77a1.webp', 'link': 'https://www.xiaohongshu.com/search_result/66f2aeb6000000001a023607?xsec_token=AB5fweC9U4NPuDQCp2BE4nQMvbh0EAa5Yeclv5rtndHuY=&xsec_source=pc_search', 'description': '强调选对护肤品和护肤方式的重要性，并给出不同年龄段的具体护肤建议。'},
                    {'title': '不同年龄段该怎么正确科学护肤呢？', 'author': '小夜学长', 'image_url': '8133713bd642b4c76d79b921f971a90a.webp', 'link': 'https://www.xiaohongshu.com/search_result/669a7c28000000000a025afd?xsec_token=AB2s1XCwSY2dvVi-0BOlMfCSVWl8hMb6ertE9ETC0Lqhw=&xsec_source=pc_search', 'description': '科学护肤指南，提供从青少年到中老年人的护肤策略，强调基础护理与抗老结合。'},
                    {'title': '不同年龄段该如何护肤？', 'author': '叉锂先锋小助理', 'image_url': 'bbb5b4657238f49c4ef185e007c197c0.webp', 'link': 'https://www.xiaohongshu.com/search_result/678db6a6000000001903015e?xsec_token=ABb80elaWV8pYd4XimKpM56pebCGV2R6Ro65xBymsl3vE=&xsec_source=pc_search', 'description': '分析各年龄段护肤需求，包括儿童、青年、中年和老年阶段的护肤重点。'},
                    {'title': '不看后悔❗不同年龄段该如何正确护肤', 'author': 'Marry护肤姐', 'image_url': 'be1b0cda1407c80620e1a80efb1930af.webp', 'link': 'https://www.xiaohongshu.com/search_result/66a8ac3d000000002701ddb6?xsec_token=AB-Ry7fhlEIgGMjHVntMU2D-P5aZkpqeQzzmSeY1LpDaA=&xsec_source=pc_search', 'description': '针对青春期、青春期后、轻熟肌和熟龄肌分别提出护肤建议，涵盖清洁、保湿、防晒和抗老。'},
                    {'title': '🌟【护肤大揭秘！不同年龄段护肤重点全攻略】🌟', 'author': '沈故', 'image_url': '91323b8745f9b4de4d104d06c5c15d9a.webp', 'link': 'https://www.xiaohongshu.com/search_result/67de149d000000000b01556e?xsec_token=ABPkGhrTPyD0xDc3-aTBWV1Hp6oJYk05YlbwpdfhhwX_s=&xsec_source=pc_search', 'description': '提供从20岁+到40岁+的护肤重点，强调抗氧化、抗初老、紧致修复等关键步骤。'},
                    {'title': '不同年龄阶段的护肤攻略', 'author': '小平谈护肤', 'image_url': '6f9d5fafa1bd7775c01f0150c2f1c593.webp', 'link': 'https://www.xiaohongshu.com/search_result/67579e990000000002035b3a?xsec_token=ABSCHurxWWf9eqIKsD_fRsKdcPm6wHQnGR2UVn_N_TTDU=&xsec_source=pc_search', 'description': '简洁明了地总结不同年龄段的护肤策略，适合快速了解基本要点。'},
                    {'title': '上班族姐妹护肤小指南', 'author': '独自闪耀女性健康养护', 'image_url': '9ea9aa8d68f67456ec06a66eba34327e.webp', 'link': 'https://www.xiaohongshu.com/search_result/68075a26000000001c032c7a?xsec_token=ABRjqHMpLfJ28SsHQnqLLo2FHnl16J9fQjDlA-A3IAG7Y=&xsec_source=pc_search', 'description': '针对上班族的护肤建议，包括日常清洁、保湿、防晒及放松心情的方法。'},
                    {'title': '不看后悔！不同年龄段该如何护肤', 'author': '米奇妙妙吴', 'image_url': '820a2795e237a7e8d15168741fa11f17.webp', 'link': 'https://www.xiaohongshu.com/search_result/67811732000000001a010fb2?xsec_token=ABOe2ZLNNs0tPu-eC8ZNyAxpClp_Ks5qA2v19VorqQnqQ=&xsec_source=pc_search', 'description': '提供从15岁到45岁以上的详细护肤方案，强调抗初老和滋养修复的重要性。'},
                    {'title': '悦己｜30+办公室女性低成本保养方案💃', 'author': '紫晴的星星', 'image_url': 'c033bd9b8670bc9f58af1b91371fe1fa.webp', 'link': 'https://www.xiaohongshu.com/search_result/67ac74b400000000180085e1?xsec_token=ABlDISF5krOlC8SOSfyjWTTPFy9keHWbX-ibcijwZ_hiw=&xsec_source=pc_search', 'description': '针对30+职场女性的低成本保养方案，涵盖护肤、饮食、运动、心理健康等多个方面。'}]
all_results = all_results_hufu + all_results_meizhuang + all_results_chuanda


buy_results_meizhuang = [{'title': '欧莱雅纷泽小眼影盘&哥特盘&仿生膜口红','buy':'http://xhslink.com/a/e6kY8UUXMCfgb', 'author': 'Annの安利', 'image_url': '39e9951149d301cabd593bed94ce5729.webp', 'link': 'https://www.xiaohongshu.com/search_result/659502e2000000000f01c6d4?xsec_token=ABCVL3hQuvsuSWhXKk2IXCsMZgiGCKbaaaQe1SQAJJoBw=&xsec_source=', 'description': '欧莱雅这款五色小盘非常小巧精致。其实欧莱雅本家出的护肤彩妆都很平价实用。'},
                         {'title': '欧莱雅梦女是吗','buy':'http://xhslink.com/a/yEpp60TU9Cfgb', 'author': '钞票捕手咩杜莎', 'image_url': 'ab77186642e3557d83b16a7d2dc9920c.webp', 'link': 'https://www.xiaohongshu.com/search_result/67b3ea540000000007028670?xsec_token=ABbTNhFoyTJKF_4kFdj_YFli4dHK4NExOgsJjhJr_qrWM=&xsec_source=pc_search', 'description': '手里的黑金普通版气垫还没用完看到出了限定包装又下单了，普通版的替换装也囤上了。'},
                         {'title': '欧莱雅限定裸色细管唇霜', 'buy':'http://xhslink.com/a/UD8tsybnFDfgb', 'author': '炸毛葛（起飞版）', 'image_url': 'fb1474d4aa19a756eb1be4c28edba87a.webp', 'link': 'https://www.xiaohongshu.com/search_result/6276083e000000000102b1d3?xsec_token=ABvq0kZCuI2fnVMHyMZ1YsqMckOff29hihk0zA51buPbQ=&xsec_source=pc_search', 'description': '欧莱雅限定裸色细管唇霜611小雀斑，名字起的好，明媚的橘棕色，温暖的夏日氛围，是二十多岁的姑娘，一点点蠢蠢欲动一点点妩媚一点点天真的样子。'},
                         {'title': '欧莱雅『口眼袋影盘』', 'buy':'http://xhslink.com/a/J23NdAlBLEfgb','author': '欧莱雅柜姐果果长沙梅溪湖店', 'image_url': '0c0cfbb0e69fb391d445ae62408e8b10.webp', 'link': 'https://www.xiaohongshu.com/search_result/66754dcf000000001f006af1?xsec_token=ABzvylnlGsJmXva2GWdNHPGfiKqikJDUMwLxCyLXuv2QQ=&xsec_source=pc_search', 'description': '欧莱雅『口眼袋影盘』'},
                         {'title': '欧莱雅八色眼影盘', 'buy':'http://xhslink.com/a/J23NdAlBLEfgb','author': '欧莱雅柜姐果果', 'image_url': '8bec11b049c8d4b331557833814043e4.webp', 'link': 'http://xhslink.com/a/7EOOXqUFDdvgb', 'description': '媱一盘欧莱雅八色眼影盘 拆封未使用 可走平台'},
                         {'title': '欧莱雅纷泽小白管口红195#试色.199#试色', 'buy':'http://xhslink.com/a/6RQkcid8bFfgb','author': '欧莱雅专柜小姐姐一枚', 'image_url': '448fb37100aab43b6c52b95f7e56c773.webp', 'link': 'https://www.xiaohongshu.com/search_result/6828299d00000000120060a5?xsec_token=AB7Q-sJLQwEGVoUqR7MwtfF1ZeHp4UeBFe5ufMRmYVjZU=&xsec_source=pc_search', 'description': '欧莱雅纷泽小白管口红195#试色.199#试色分享给爱美的你。'},
                         {'title': '欧莱雅也出口红啦！冷感裸色“虐爱啦”','buy':'http://xhslink.com/a/nlmjBiiVvFfgb', 'author': '分享达人', 'image_url': 'b328abd9b50e691c1b29ed2a7c18b0d8.webp', 'link': 'https://www.xiaohongshu.com/search_result/68011831000000001d015e66?xsec_token=ABBzFNwMA-iHCwh7O8Ar1N8Fs6YKblWv8WTw8i2KLFT6M=&xsec_source=pc_search', 'description': '欧莱雅也出口红啦！冷感裸色“虐爱啦”姐妹们！谁知道欧莱雅还会出口红了呢。'},
                         {'title': '欧莱雅眼影', 'buy':'http://xhslink.com/a/Sasr5oZmMFfgb','author': '盛朝宇', 'image_url': 'eabcc7cc297cef93d1cb3830374a08c0.webp', 'link': 'https://www.xiaohongshu.com/search_result/682765cc000000000f038840?xsec_token=ABQ9X80rLeKxY0MfxZFItueuq9FjYd29on275O5ZzKINM=&xsec_source=pc_search', 'description': '欧莱雅眼影'},
                         {'title': '欧莱雅#200口红💄','buy':'http://xhslink.com/a/nlmjBiiVvFfgb', 'author': '欧莱雅路露', 'image_url': '2eade71b4bca6cb0930dec53d0e14524.webp', 'link': 'https://www.xiaohongshu.com/search_result/652e53a9000000002301ba8b?xsec_token=AB8UPDSpBSp5tc8bZGTsmfnK_npkUYuNpLUBnOQWrnw9A=&xsec_source=pc_search', 'description': '欧莱雅#200口红💄我最近的心头爱#欧莱雅200凡尔赛棕，橘调红棕色非常适合秋冬使用，温柔中带着一丝清冷～'},
                         {'title': '适合夏天黄黑皮女生口红', 'buy':'http://xhslink.com/a/Y4oa9pxkgGfgb','author': '阿喵。', 'image_url': '15734c923c2ea8fc20c6fbc3b738c8d1.webp', 'link': 'http://xhslink.com/a/tyzwBtowZevgb', 'description': '黄皮救星色，显白显气色#欧莱加口红测评'}]
buy_results_chuanda = [{'title': '原来5k➕就可以搞定一年四季穿搭', 'buy':'http://xhslink.com/a/25R9y51q0Gfgb','author': '桃桃不淘气', 'image_url': '1d97926f60ec0f65b919b2363747f946.webp', 'link': 'https://www.xiaohongshu.com/search_result/677a07fd000000001300d4b3?xsec_token=AB6MzmrLQykN8mTiT8q1SRNyS7n76waU1G3n_sK30gxwc=&xsec_source=', 'description': '分享了不同季节的穿搭建议，以及如何用有限的预算买到高质量的衣服。'},
                       {'title': '从乱买到会买！告别次抛衣的长期主义购衣法','buy':'http://xhslink.com/a/Dn0xkN9f6Gfgb', 'author': '有竹-', 'image_url': 'b2fdf4831935c2737f136e07a9845dd8.webp', 'link': 'https://www.xiaohongshu.com/search_result/68273a5d00000000230148ea?xsec_token=ABQ9X80rLeKxY0MfxZFItuen6M4smkn-J_KZILnsw5c8o=&xsec_source=pc_search', 'description': '提供了一套长期主义的购物思路，帮助减少不必要的购物浪费。'},
                       {'title': '当我问deepseek，女生一年需要多少衣服👗', 'buy':'http://xhslink.com/a/2DqhNkCqaHfgb','author': '呼呼雅', 'image_url': '741ad592bec39a500b03e80a56dce41f.webp', 'link': 'https://www.xiaohongshu.com/search_result/67cbfab7000000002803f33f?xsec_token=ABRcSIQ89sfsPVL5lQXsV8vsuLinWmXdHC6opRNUfxDwU=&xsec_source=pc_search', 'description': '探讨了女性在一年中究竟需要多少衣服的问题，并分享了一些购物建议。'},
                       {'title': '拒绝廉价 | 超有质感的老钱风店铺', 'buy':'http://xhslink.com/a/uBj4CgEocHfgb','author': '溜小溜', 'image_url': '16f2c6d3a0b1c34aa4065d4b658e716e.webp', 'link': 'https://www.xiaohongshu.com/search_result/66cebd81000000001f038ac3?xsec_token=AB-2c5S6aJik64EF4bGsaEp6MBl-1lqXAQCfL8I7eU3sU=&xsec_source=pc_search', 'description': '推荐了几家具有高级质感的老钱风店铺，适合追求品质穿搭的人群。'},
                       {'title': '一套衣服穿一年四季不过分吧 不信你看！','buy':'http://xhslink.com/a/CMpc5db4eHfgb', 'author': '谷老师', 'image_url': 'c109d6d2db1255b6e9c49109bf4db96c.webp', 'link': 'https://www.xiaohongshu.com/search_result/67ab3a0a000000001902cead?xsec_token=ABSWr7hA_5F7SVxSQ19u5p4zJOHXnmWGr_NaEaA1AKJbw=&xsec_source=pc_search', 'description': '展示了一套可以适应四季穿搭的衣服，强调实用性和多样性。'}]
buy_results_hufu = [{'title': '欧莱雅皮肤科学美容部核心产品线','buy':'http://xhslink.com/a/wiNRLd7ZuIfgb', 'author': '努力搬砖的小黄', 'image_url': '33ad246e270a6ee1e3a2a8437ebddd75.webp', 'link': 'https://www.xiaohongshu.com/search_result/66575e6f000000001601065e?xsec_token=ABG9OwVR1x9EOP_jfubEsvxrXBHq3Rzcvys0TAG1g8MEs=&xsec_source=', 'description': '盘点欧莱雅皮肤科学美容部的核心品牌与产品，包括修丽可、理肤泉、适乐肤、薇姿等。重点介绍各品牌的拳头产品及其功效。'},
                    {'title': '欧莱雅哪个系列适合干皮', 'buy':'http://xhslink.com/a/a7h6CA7ByIfgb','author': '方阿不', 'image_url': '374f3457e27005e1f224dc8ab8ad22a5.webp', 'link': 'https://www.xiaohongshu.com/search_result/67e7c6b2000000000903840b?xsec_token=ABUomeWbd6ZTB0SScsMWWeUokjNC2O9oqiRBtCyhroqgQ=&xsec_source=pc_search', 'description': '推荐适合干皮人群使用的欧莱雅护肤系列，并分析不同系列的适用场景。'},
                    {'title': '欧莱雅第二代怎么使用，来这里抄作业！', 'buy':'http://xhslink.com/a/enqwIIYPFIfgb','author': '欧莱雅专柜柜姐护肤', 'image_url': 'a666f34748c16ce301a37b2693c9dc08.webp', 'link': 'https://www.xiaohongshu.com/search_result/670f8a2a000000001b02fc24?xsec_token=ABnVFmiY5Ux0sAKCgjQeR10NDrvmXYdA31FEvdP_3emWs=&xsec_source=pc_search', 'description': '分享欧莱雅第二代水乳的正确使用方法及搭配建议，避免搓泥问题。'},
                    {'title': '省薪挑选!欧莱雅爆款面霜攻略~','buy':'http://xhslink.com/a/ubtlQKZEhJfgb', 'author': '晏尚美妆', 'image_url': '44dd930ab3b58ec9a7a9f1b875c6a261.webp', 'link': 'https://www.xiaohongshu.com/search_result/667b4cfb000000001c026036?xsec_token=ABvEiTRmOj5VLqvXK804UwbRZsuwnTXQ_jKOau7yMjF5w=&xsec_source=pc_search', 'description': '推荐欧莱雅几款热门面霜，并分析其适用肤质及主要功效。'},
                    {'title': '欧莱雅紫熨斗眼霜套盒 母亲节首选','buy':'http://xhslink.com/a/ThHYD1oWzJfgb', 'author': '欧莱雅渼澜', 'image_url': '5fe7cd88a30eda9100860ca427505f34.webp', 'link': 'https://www.xiaohongshu.com/search_result/6819d3370000000012006ffa?xsec_token=ABT5sAicJ21fIMs8vXAPIaHojfE-AXRmPSO8SXgypi7xU=&xsec_source=pc_search', 'description': '推荐欧莱雅紫熨斗眼霜套盒，详细介绍其抗老、保湿和修护功能。'},
                    {'title': '欧莱雅全系列水乳怎么选？史上最全合集！','buy':'http://xhslink.com/a/3YhpE0C1AIfgb', 'author': '阳阳护肤直播', 'image_url': 'ecd136a31c9faa2c05be3a7c2c0530c6.webp', 'link': 'https://www.xiaohongshu.com/search_result/67136f3500000000260350d5?xsec_token=ABehjY5sgDeSvkkXBdQoXMuIvZXE1-Eg066luNjAdKJSk=&xsec_source=pc_search', 'description': '提供欧莱雅所有系列水乳的详细对比，帮助用户根据自身需求选择合适的产品。'},
                    {'title': '25岁释怀了，从此我不会再被抗老水乳欺骗', 'buy':'http://xhslink.com/a/3YhpE0C1AIfgb','author': '垣小椰', 'image_url': 'e55f9bd9c3fc7f61833693c593d7e5c1.webp', 'link': 'https://www.xiaohongshu.com/search_result/6699ebb00000000025006beb?xsec_token=AB7Fj3j15M70XnKA8xcSSZt5BGUaGOSG9hJT95-1WUexE=&xsec_source=pc_search', 'description': '使用欧莱雅第二代玻色因水乳后的体验分享，强调其抗老效果显著。'},
                    {'title': '25+岁的你，不会还在为抗初老而发愁吧❓','buy':'http://xhslink.com/a/byNyKyjt8Jfgb', 'author': '欧莱雅专柜柜姐护肤', 'image_url': '19d39e335ae3f2ea2ebb48843995e17b.webp', 'link': 'https://www.xiaohongshu.com/search_result/66ac5eb0000000000600c2eb?xsec_token=AB5gPFBRzhWDXKb1CgQ5Zc65ph2AqlYdFHyRq70lnntlw=&xsec_source=pc_search', 'description': '推荐25岁以上女性必入的抗老产品组合，强调金致臻颜花蜜系列的紧致提亮效果。'},
                    {'title': '问问欧莱雅和olay哪个更好','buy':'http://xhslink.com/a/n4E9j3VQpKfgb', 'author': '鲜橙饺子🍀', 'image_url': '4b83873a6b39a0aed07bef4d0098785c.webp', 'link': 'https://www.xiaohongshu.com/search_result/681a65f700000000220370eb?xsec_token=ABcfRkkYZLfS5iZtKbJTfL68FbhQ9FGeKYb9bEbM90tPE=&xsec_source=pc_search', 'description': '用户提问并寻求欧莱雅和OLAY两个品牌护肤品的比较推荐。'},
                    {'title': '小蜜罐家族@你｜抗老全套搭子上线啦','buy':'http://xhslink.com/a/Z1ZfKr7sEKfgb', 'author': "L'OREAL欧莱雅", 'image_url': '5e961345f7f23ee7ba03e39dd255506d.webp', 'link': 'https://www.xiaohongshu.com/search_result/67c04cbd000000002803f571?xsec_token=ABYbn9W5oa3EAbfWjMfflUXc5MpOvJoUz00aCX0CVivQM=&xsec_source=pc_search', 'description': '官方账号推广小蜜罐系列产品，强调其抗老及胶原蛋白补充功效。'}]
buy_all_results = buy_results_hufu + buy_results_chuanda + buy_results_meizhuang


def search_makeup_notes(query):
    """搜索小红书妆容笔记"""
    if query == '美妆':
        mock_results = random.sample(all_results_meizhuang, 2)
    elif query == '护肤':
        mock_results = random.sample(all_results_hufu, 2)
    elif query == '穿搭':
        mock_results = random.sample(all_results_chuanda, 2)
    else:
        mock_results = random.sample(all_results, 2)
    return mock_results

def search_buy_notes(query):
    """搜索购买链接"""
    if query == '美妆':
        mock_results = random.sample(buy_results_meizhuang, 2)
    elif query == '护肤':
        mock_results = random.sample(buy_results_hufu, 2)
    elif query == '穿搭':
        mock_results = random.sample(buy_results_chuanda, 2)
    else:
        mock_results = random.sample(buy_all_results, 2)
    return mock_results

@mcp.tool()
def generate_xiaohongshu_notes(text):
    """
    Analyze the sentiment of the given text.

    Args:
        text (str): The text to analyze

    Returns:
        str: A JSON string containing polarity, subjectivity, and assessment
    """
    zhuangrong=search_makeup_notes(text)
    goumai=search_buy_notes(text)   
    
    zhuangrong_html=generate_notes_preview(zhuangrong)
    goumai_html=generate_buy_preview(goumai)

    return zhuangrong_html,goumai_html

def generate_buy_preview(notes):
    """生成小红书笔记预览HTML"""
    html = """
    <div style="display: grid; 
                grid-template-columns: repeat(2, 1fr); 
                gap: 15px; 
                padding: 20px; 
                background: #f8f9fa; 
                border-radius: 10px;">
    """
    
    for note in notes:
        html += f"""
<div style="width: 100%; 
background: white; 
border-radius: 12px; 
box-shadow: 0 2px 8px rgba(0,0,0,0.1);
overflow: hidden;
transition: transform 0.2s;
cursor: pointer;
display: flex;
flex-direction: column;"
onclick="window.open('{note['link']}', '_blank')">
<img src='/gradio_api/file=assets/{note['image_url']}' style="width: 100%; height: 180px; object-fit: cover;" alt="">
<div style="padding: 15px; flex-grow: 1; display: flex; flex-direction: column;">
   <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #333; line-height: 1.4;">{note['title']}</h3>
   <p style="margin: 0 0 8px 0; color: #666; font-size: 14px;">@{note['author']}</p>
   <p style="margin: 0 0 12px 0; color: #888; font-size: 13px; line-height: 1.3; flex-grow: 1;">{note['description']}</p>
   <a href="{note['buy']}" 
      target="_blank" 
      style="color: #333; 
             font-weight: 500; 
             font-size: 14px; 
             font-family: 'Microsoft YaHei', '微软雅黑', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
             text-decoration: none; 
             display: inline-block; 
             padding: 8px 20px; 
             border-radius: 20px; 
             background: linear-gradient(135deg, #E6F3FF 0%, #B3D9FF 100%); 
             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
             transition: all 0.3s ease;
             letter-spacing: 0.5px;
             align-self: flex-start;
             margin-top: auto;"
      onclick="event.stopPropagation();"
      onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(0, 0, 0, 0.15)'"
      onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0, 0, 0, 0.1)'">
      点击购买
   </a>
</div>
</div>
        """
    
    html += "</div>"
    return html



def generate_notes_preview(notes):
    """生成小红书笔记预览HTML"""
    html = """
    <div style="display: grid; 
                grid-template-columns: repeat(2, 1fr); 
                gap: 15px; 
                padding: 20px; 
                background: #f8f9fa; 
                border-radius: 10px;">
    """
    
    for note in notes:
        html += f"""
<div style="width: 100%; 
background: white; 
border-radius: 12px; 
box-shadow: 0 2px 8px rgba(0,0,0,0.1);
overflow: hidden;
transition: transform 0.2s;
cursor: pointer;"
onclick="window.open('{note['link']}', '_blank')">
<img src='/gradio_api/file=assets/{note['image_url']}' style="width: 100%; height: 180px; object-fit: cover;" alt="">
<div style="padding: 15px;">
    <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #333; line-height: 1.4;">{note['title']}</h3>
    <p style="margin: 0 0 8px 0; color: #666; font-size: 14px;">@{note['author']}</p>
    <p style="margin: 0; color: #888; font-size: 13px; line-height: 1.3;">{note['description']}</p>
</div>
</div>
        """
    
    html += "</div>"
    return html

# # Create the Gradio interface
# demo = gr.Interface(
#     fn=generate_xiaohongshu_notes,
#     inputs=gr.Textbox(placeholder="Enter text to analyze..."),
#     outputs=[gr.HTML(label="相关笔记预览"), gr.HTML(label="购买链接预览")],  # Changed from gr.JSON() to gr.Textbox()
#     title="Text Sentiment Analysis",
#     description="Analyze the sentiment of text using TextBlob"
# )

# Launch the interface and MCP server
# if __name__ == "__main__":
#     demo.launch()

if __name__ == "__main__":
    mcp.run()


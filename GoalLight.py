import asyncio
from kasa import SmartBulb
import time
import requests
import json
import schedule
from datetime import datetime
from datetime import timedelta
import pytz
from multiprocessing import Process


bulb_bed_room = SmartBulb("192.168.2.134")
bulb_living_room = SmartBulb("192.168.2.135")

def gamesToday():
    date = datetime.today().strftime('%Y-%m-%d')
    url = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=3&startDate={}&endDate={}".format(date,date)
    data = requests.get(url).json()
    if len(data['dates']) > 0:
        return data['dates'][0]['games'][0]['link']
    else:
        return 0
def live_game(game_url):
    game_feed = requests.get(game_url).json()
    game_time = game_feed['gameData']['datetime']['dateTime']
    d = datetime.fromisoformat(game_time[:-1]).astimezone(pytz.timezone("US/Eastern"))
    
    new_temp = d - timedelta(hours=4)
    new_time = new_temp.strftime('%H:%M')
    currentGoals = 0
    while 1:
        if datetime.now().strftime("%H:%M") == new_time:
            gameStartedProcess1 = Process(target=living_room_start_callback)
            gameStartedProcess2 = Process(target=bed_room_start_callback)
            gameStartedProcess1.start()
            gameStartedProcess2.start()
            gameStartedProcess1.join()
            gameStartedProcess2.join()
            time.sleep(60)
        elif datetime.now().strftime("%H:%M") > new_time:
            is_goal = requests.get(game_url).json()
            if is_goal['gameData']['status']['detailedState'] == "Final":
                break
            elif is_goal['liveData']['linescore']['teams']['home']['team']['id'] == 3:
                if is_goal['liveData']['linescore']['teams']['home']['goals'] > currentGoals:
                    goalProcess1 = Process(target=living_room_goal_callback)
                    goalProcess2 = Process(target=bed_room_goal_callback)
                    goalProcess1.start()
                    goalProcess2.start()
                    goalProcess1.join()
                    goalProcess2.join()
                    currentGoals+=1                   
            else:
                if is_goal['liveData']['linescore']['teams']['away']['goals'] > currentGoals:
                    goalProcess1 = Process(target=living_room_goal_callback)
                    goalProcess2 = Process(target=bed_room_goal_callback)
                    goalProcess1.start()
                    goalProcess2.start()
                    goalProcess1.join()
                    goalProcess2.join()
                    currentGoals+=1
                       
def living_room_start_callback():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(living_room_game_start())
    loop.close()
    
def bed_room_start_callback():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bed_room_game_start())
    loop.close()
    
def living_room_goal_callback():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(living_room_goal())
    loop.close()
    
def bed_room_goal_callback():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bed_room_goal())
    loop.close()

async def living_room_game_start():
    try:
        await bulb_living_room.update()
        await bulb_living_room.set_hsv(180,100,50)
        await bulb_living_room.set_brightness(100)
        for i in range(5):
            await bulb_living_room.turn_off()
            time.sleep(0.5)
            await bulb_living_room.turn_on()
            time.sleep(1) 
        await bulb_living_room.set_color_temp(3000)
    except Exception:
        pass
    
async def bed_room_game_start():
    try:
        await bulb_bed_room.update()
        await bulb_bed_room.set_hsv(180,100,50)
        await bulb_bed_room.set_brightness(100)
        for i in range(5):
            await bulb_bed_room.turn_off()
            time.sleep(0.5)
            await bulb_bed_room.turn_on()
            time.sleep(1) 
        await bulb_bed_room.set_color_temp(3000)
    except Exception:
        pass

async def living_room_goal():
    try:
        await bulb_living_room.update()
        await bulb_living_room.set_hsv(0,100,50)
        await bulb_living_room.set_brightness(100)
        for i in range(5):
            await bulb_living_room.turn_off()
            time.sleep(0.5)
            await bulb_living_room.turn_on()
            time.sleep(1) 
        await bulb_living_room.set_color_temp(3000)
    except Exception:
        pass
    
async def bed_room_goal():
    try:
        await bulb_bed_room.update()
        await bulb_bed_room.set_hsv(0,100,50)
        await bulb_bed_room.set_brightness(100)
        for i in range(5):
            await bulb_bed_room.turn_off()
            time.sleep(0.5)
            await bulb_bed_room.turn_on()
            time.sleep(1) 
        await bulb_bed_room.set_color_temp(3000)
    except Exception:
        pass
                                        
def get_games():
    game_link = 0
    game_link = gamesToday()
    if game_link != 0:
        game_url = "https://statsapi.web.nhl.com{}".format(game_link)
        live_game(game_url)
    
schedule.every().day.at('06:00').do(get_games)

if __name__ == "__main__":
    while 1:
        schedule.run_pending()
        time.sleep(1)
        

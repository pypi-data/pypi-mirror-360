from tkinter import *
import tkinter as tk
from tkinter import BOTTOM
import pytz
import requests
from datetime import datetime
from geopy.geocoders import Nominatim
from PIL import ImageTk, Image
from timezonefinder import TimezoneFinder
import tkinter.messagebox as messagebox
import pystray
import PIL.Image
import sys

class weatherApp:

    def run(self, api_key, path="default"):
        if path == "default":
            self.file=f"{sys.executable.replace('python.exe','').replace('pythonw.exe','')}\Lib\site-packages\openweatherappapi"
        else:
            self.file=path
        root=Tk()
        root.title("Weather App By Ali")
        root.geometry("750x470+300+200")
        root.resizable(False,False)
        root.config(bg="#202731")
        import threading

        def getweather():
            city = self.textfield.get()
            self.geolocator = Nominatim(user_agent="newgeoapiExercises")
            try:
                location = self.geolocator.geocode(city)
                if location is None:
                    self.timezone.config(text="Location not found")
                    return
                obj = TimezoneFinder()
                result = obj.timezone_at(lat=location.latitude, lng=location.longitude)
                self.timezone.config(text=result)
                self.long_lat.config(text=f'{round(location.latitude, 4)}°N {round(location.longitude, 4)}°E')
                home = pytz.timezone(result)
                local_time = datetime.now(home)
                current_time = local_time.strftime("%H:%M:%S")
                self.clock.config(text=current_time)
                self.api_key = api_key
                self.api_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units=metric"
                self.response = requests.get(self.api_url).json()
                self.current = self.response['list'][0]
                temp = self.current['main'].get('temp', 'N/A')
                humidity = self.current['main'].get('humidity', 'N/A')
                pressure = self.current['main'].get('pressure', 'N/A')
                wind_speed = self.current['wind'].get('speed', 'N/A')
                description = self.current['weather'][0].get('description', 'N/A')
                # Ensure these widgets exist before updating
                if not hasattr(self, 'temp'):
                    self.temp = tk.Label(root, font=("Helvetica", 11), fg="#323661", bg="#aad1c8")
                    self.temp.place(x=150, y=120)
                if not hasattr(self, 'humidity'):
                    self.humidity = tk.Label(root, font=("Helvetica", 11), fg="#323661", bg="#aad1c8")
                    self.humidity.place(x=150, y=140)
                if not hasattr(self, 'pressure'):
                    self.pressure = tk.Label(root, font=("Helvetica", 11), fg="#323661", bg="#aad1c8")
                    self.pressure.place(x=150, y=160)
                if not hasattr(self, 'wind_speed'):
                    self.wind_speed = tk.Label(root, font=("Helvetica", 11), fg="#323661", bg="#aad1c8")
                    self.wind_speed.place(x=150, y=180)
                if not hasattr(self, 'description'):
                    self.description = tk.Label(root, font=("Helvetica", 11), fg="#323661", bg="#aad1c8")
                    self.description.place(x=150, y=200)
                self.temp.config(text=f"{temp}°C")
                self.humidity.config(text=f"{humidity}%")
                self.pressure.config(text=f"{pressure}hPa")
                self.wind_speed.config(text=f"{wind_speed}m/s")
                self.description.config(text=f"{description}")
                self.daily_data = []
                for i in self.response['list']:
                    if "12:00:00" in i['dt_txt']:
                        self.daily_data.append(i)
                self.icons = []
                self.temps = []
                for i in range(5):
                    if i >= len(self.daily_data):
                        break
                    self.icon_code = self.daily_data[i]['weather'][0]['icon']
                    self.img = Image.open(f"{self.file}\{self.icon_code}@2x.png")
                    self.icons.append(ImageTk.PhotoImage(self.img))
                    self.temps.append((self.daily_data[i]['main']['temp_max'], self.daily_data[i]['main']['feels_like']))
                day_widget = [
                    (self.firstimage, self.day1, self.day1temp),
                    (self.secondimage, self.day2, self.day2temp),
                    (self.thirdimage, self.day3, self.day3temp),
                    (self.fourthimage, self.day4, self.day4temp),
                    (self.fifthimage, self.day5, self.day5temp)
                ]
                from datetime import timedelta

                for i, (img_label, day_label, temp_label) in enumerate(day_widget):
                    if i >= len(self.icons):
                        break
                    img_label.config(image=self.icons[i])
                    img_label.image = self.icons[i]
                    temp_label.config(text=f"Day: {self.temps[i][0]}\nNight: {self.temps[i][1]}")
                    self.future_date = datetime.now() + timedelta(days=i)
                    day_label.config(text=self.future_date.strftime("%A"))

            except Exception:
                pass

            # Auto update every 10 minutes (600000 ms)
        import time
        def schedule_update():
            while True:
                time.sleep(0.5)
                getweather()
        image = PIL.Image.open(f"{self.file}\logo.png")



        self.update_thread = threading.Thread(target=schedule_update)
        self.update_thread.start()
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.icon.stop()
                del self.thread1
                del self.update_thread

                root.quit()
        import webbrowser
        def on_clicked(_icon, item):
            if str(item) == 'О себя':
                messagebox.showinfo("О себя", "Telegram: https://t.me/ALIKUSHBAEVYT\nDiscord: https://discord.gg/nEYmfYQWcw\nSites: https://alikushbaev.github.io/Sites/\nВладелиц: Ali Kushbaev")
            elif str(item) == 'Выход':
                on_closing()
            elif str(item) == 'Другие Работы ;)':
                webbrowser.open("https://alikushbaev.github.io/Sites/")

        self.icon = pystray.Icon('Wether App By Ali', image, menu=pystray.Menu(
            pystray.MenuItem('О себя', on_clicked),
            pystray.MenuItem('Выход', on_clicked),
            pystray.MenuItem('Другие Работы ;)', on_clicked)

        ))
        def theard_close():
            self.icon.run()
        self.thread1 = threading.Thread(target=theard_close)
        self.thread1.start()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        self.image_icon=PhotoImage(file=f"{self.file}\logo.png")
        root.iconphoto(False,self.image_icon)
        self.round_box=PhotoImage(file=f"{self.file}\Rounded Rectangle 1.png")
        Label(root,image=self.round_box,bg="#202731").place(x=30,y=60)
        Label(root, text= "by Ali_Dev", bg='#202731', fg='#ffffff').place(x=670, y=60)
        self.label1=Label (root, text="Temperature", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        self.label1.place(x=50,y=120)

        self.label2=Label (root, text="Humidity", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        self.label2.place(x=50,y=140)

        self.label3=Label (root, text="Pressure", font=("Helvetica", 11), fg="#323661", bg="#aad1c8") 
        self.label3.place(x=50,y=160)

        self.label4=Label (root, text="Wind Speed", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        self.label4.place(x=50,y=180)

        self.label5=Label (root, text="Description", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        self.label5.place(x=50,y=200)
        self.Search_image = PhotoImage(file=f"{self.file}\Rounded Rectangle 3.png")

        self.myimage = Label(root, image=self.Search_image, bg="#202731")

        self.myimage.place(x=270, y=122)

        self.weather_image = PhotoImage(file=f"{self.file}\Layer 7.png")

        self.weatherimage = Label(root, image=self.weather_image, bg="#333c4c")

        self.weatherimage.place(x=290, y=127)

        self.textfield = tk.Entry(root, justify="center", width=15, font=("poppins", 25, "bold"), bg="#333c4c", border=0, fg="white")

        self.textfield.place(x=370, y=130)

        self.Search_icon = PhotoImage(file=f"{self.file}\Layer 6.png")
        # on click bg

        self.myimage_icon = Button(root, image=self.Search_icon, borderwidth=0, cursor="hand2", bg="#333c4c", highlightcolor="#333c4c", activebackground="#333c4c", command=getweather)

        self.myimage_icon.place(x=640, y=135)
        #Bottom boX

        self.frame=Frame (root, width=900,height=180, bg="#7094d4")

        self.frame.pack(side=BOTTOM)

        #boxes
        self.firstbox = PhotoImage(file=f"{self.file}\Rounded Rectangle 2.png")

        self.secondbox = PhotoImage(file=f"{self.file}\Rounded Rectangle 2 copy.png")
        self.secondbox = PhotoImage(file=f"{self.file}\Rounded Rectangle 2 copy.png")

        Label (self.frame, image=self.firstbox,bg="#7094d4").place(x=30,y=20)

        Label (self.frame, image=self.secondbox, bg="#7094d4").place(x=300,y=30)

        Label (self.frame, image=self.secondbox, bg="#7094d4").place(x=400,y=30)

        Label (self.frame, image=self.secondbox, bg="#7094d4").place(x=500,y=30)

        Label (self.frame, image=self.secondbox, bg="#7094d4").place(x=600,y=30)
        #clock

        self.clock=Label (root, font=("Helvetica", 20), bg="#202731",fg="white")

        self.clock.place(x=30,y=20)

        #timezone

        self.timezone=Label(root, font=("Helvetica", 20), bg="#202731", fg="white")

        self.timezone.place(x=500,y=20)

        self.long_lat=Label(root, font=("Helvetica", 10), bg="#202731", fg="white")

        self.long_lat.place (x=500,y=50)

        #thpwd

        self.t=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        self.t.place(x=150,y=120)
        self.h=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        self.h.place(x=150,y=140)
        self.p=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        self.p.place(x=150,y=160)
        self.w=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        self.w.place(x=150,y=180)
        self.d=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        self.d.place(x=150,y=200)
        # #
        self.firstframe = Frame(root, width=230, height=132, bg="#323661")
        self.firstframe.place(x=35, y=315)

        self.firstimage = Label(self.firstframe, bg="#323661")
        self.firstimage.place(x=0, y=15)
        self.day1 = Label(self.firstframe, font=("arial 20"), bg="#323661", fg="white")
        self.day1.place(x=1000, y=5)
        self.day1temp = Label(self.firstframe, font=("arial 15 bold"), bg="#323661", fg="white")
        self.day1temp.place(x=100, y=50)
        self.image_label = Label(self.firstframe, bg="#323661")
        self.image_label.place(x=0, y=15)
        self.city = Label(self.firstframe, font=("arial 20"), bg="#323661", fg="white")
        self.city.place(x=0, y=45)

        self.daytime = Label(self.firstframe, font=("arial 15 bold"), bg="#323661", fg="white")
        self.daytime.place(x=0, y=50)

        secondframe = Frame(root, width=70, height=115, bg="#eefefa")
        secondframe.place(x=305, y=325)

        self.secondimage = Label(secondframe, bg="#eefefa")
        self.secondimage.place(x=7, y=10)
        self.day2 = Label(secondframe, bg="#eefefa", fg="#000")
        self.day2.place(x=10, y=5)
        self.day2temp = Label(secondframe, bg="#eefefa", fg="#000")
        self.day2temp.place(x=2, y=70)
        self.thirdframe = Frame(root, width=70, height=115, bg="#eefefa")
        self.thirdframe.place(x=405, y=325)

        self.thirdimage = Label(self.thirdframe, bg="#eefefa")
        self.thirdimage.place(x=7, y=20)
        self.day3 = Label(self.thirdframe, bg="#eefefa", fg="#000")
        self.day3.place(x=10, y=5)
        self.day3temp = Label(self.thirdframe, bg="#eefefa", fg="#000")
        self.day3temp.place(x=2, y=70)
        self.fourthframe = Frame(root, width=70, height=115, bg="#eefefa")
        self.fourthframe.place(x=505, y=325)

        self.fourthimage = Label(self.fourthframe, bg="#eefefa")
        self.fourthimage.place(x=7, y=20)

        self.day4 = Label(self.fourthframe, bg="#eefefa", fg="#000")
        self.day4.place(x=10, y=5)

        self.day4temp = Label(self.fourthframe, bg="#eefefa", fg="#000")
        self.day4temp.place(x=2, y=70)
        self.fifthframe = Frame(root, width=70, height=115, bg="#eefefa")
        self.fifthframe.place(x=605, y=325)

        self.fifthimage = Label(self.fifthframe, bg="#eefefa")
        self.fifthimage.place(x=7, y=20)

        self.day5 = Label(self.fifthframe, bg="#eefefa", fg="#000")
        self.day5.place(x=10, y=5)

        self.day5temp = Label(self.fifthframe, bg="#eefefa", fg="#000")
        self.day5temp.place(x=2, y=70)
        root.mainloop()

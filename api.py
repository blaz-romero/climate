import requests
from tkinter import Tk, Entry, Button, Label, messagebox, Frame, Toplevel
from PIL import Image, ImageTk  
import os  
from datetime import datetime, timedelta

ACLARACION_FONT = 'Helvetica 9 bold'
API_KEY = '630f09278100f36b31d5817b9a25697f'

def consume_api(city):    
    city_data =[]
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        timezone = data['timezone']
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        city_data = [city, temperature, description, humidity, wind, timezone, lat, lon]
        
        return city_data
        
    else:
        print(f'Error: {response.status_code}')
        return None

def get_local_time(timezone_offset):
    utc_now = datetime.utcnow()
    try:
        timezone_offset_seconds = int(timezone_offset)
    except ValueError:
        print(f"Error: timezone_offset no es un número válido. Valor recibido: {timezone_offset}")
        return None  

    local_time = utc_now + timedelta(seconds=timezone_offset_seconds)
    return local_time

def fixed_cities():
    city = get_user_location()
    return [
        consume_api('london'),
        consume_api('rio de janeiro'),
        consume_api(city),
        consume_api('new york'),
        consume_api('santiago')
    ]

def show_images_complete(window, image_path, city, time_str, temperature, description, humidity, wind, row, col):
    try:
        
        frame = Frame(window, bg='light blue', bd=2, relief="groove", padx=10, pady=10)
        frame.grid(row=row, column=col, padx=5, pady=5)
       
        image = Image.open(os.path.abspath(image_path))
        photo = ImageTk.PhotoImage(image)
        label_img = Label(frame, image=photo, bg='light blue')
        label_img.image = photo
        label_img.pack()

        def add_icon_label(frame, icon_path, text):
            icon = Image.open(os.path.abspath(icon_path))
            icon = icon.resize((20, 20))  
            icon_photo = ImageTk.PhotoImage(icon)
            label = Label(frame, image=icon_photo, text=text, compound="left", bg='light blue', font=(ACLARACION_FONT, 12))
            label.image = icon_photo
            label.pack(anchor="w")  
            return label
        
        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12, "bold"), text=f"  {city.title()}").pack()

        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12, "bold"), text=f"  {time_str}").pack()

        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12), text=f"  {description.title()}").pack()

        add_icon_label(frame, "static/images/icono-temperatura.png", f"  {temperature}°C")

        add_icon_label(frame, "static/images/icono-humedad.png", f"  {humidity}%")

        add_icon_label(frame, "static/images/icono-viento.png", f"  {wind} km/h")

    except Exception as e:
        print(f"Error loading images: {e}")

def show_cities(cities, window):

    row = 0
    col = 0

    for city in cities:
        if city is not None:
            
            city_name, temperature, description, humidity, wind, timezone_offset, lat, lon = city
            local_time = get_local_time(timezone_offset)
            time_str = local_time.strftime("%H:%M") if local_time else "N/A"
            
            image_path = images_choise(description, local_time)
            
            show_images_complete(window, image_path, city_name, time_str, temperature, description, humidity, wind, row, col)
    
            col += 1

def show_window(data, search_history):
    window = data['window']

    label_climate = Label(window, text="Welcome to the app!", font=(ACLARACION_FONT, 16, "bold"), bg="lightblue")
    label_climate.grid(row=6, column=2)

    label_msj = Label(window, text="Find the weather for any city now!", font=(ACLARACION_FONT, 16, "bold"), bg="lightblue")
    label_msj.grid(row=8, column=2)

    entry_city = Entry(window)
    entry_city.grid(row=10, column=2, padx= 20, pady=20)
    entry_city.insert(0, 'Entry city here')

    cities = fixed_cities()
    show_cities(cities, window)
    
    def find_city():

        city = entry_city.get()
        search_city(search_history, city)
        city_data = consume_api(city)
        window.iconify()
        if city_data:
             
            secundary_window = Toplevel()
            secundary_window.title(city.title())
            secundary_window.geometry('870x500')
            secundary_window.configure(bg='light blue')
            
            city_name, temperature, description, humidity, wind, timezone_offset, lat, lon = city_data
            local_time = get_local_time(timezone_offset)
            time_str = local_time.strftime("%H:%M") if local_time else "N/A"

            daily_forecasts = get_extended_weather(lat, lon)

            image_path = images_choise(description, local_time)
            frame_center = Frame(secundary_window, bg='light blue')
            frame_center.grid(row=0, column=0)  
            
            content_frame = Frame(frame_center, bg='light blue')
            content_frame.grid(row=0, column=0)

            show_find_city(content_frame, image_path, time_str, temperature, description, humidity, wind)
            
            button_back = Button(secundary_window, text="Volver", command=lambda: go_back(secundary_window))
            button_back.grid(row=10, column=2, pady=10)

            label_city = Label(secundary_window, text=f"{city_name.title()}", font=(ACLARACION_FONT, 16, "bold"), bg="lightblue")
            label_city.grid(row=9, column=2)

            def go_back(secundary_window):
                secundary_window.destroy()  

            col = 1
            row = 0
            for key, value in daily_forecasts.items():
                
                if col < 5:
                    # Asegúrate de obtener valores únicos para cada iteración
                    day = value['day_of_week']
                    temp_max = value['temp_max']  # Verifica que temp_max sea correcto para este día
                    temp_min = value['temp_min']  # Verifica que temp_min sea correcto para este día
                    desc = value['weather_description']
                    image_path = images_choise_extended(desc)

                    show_images_extended(secundary_window, image_path, day, temp_max, temp_min, desc, row, col)
                    col += 1


            def go_back(secundary_window):

                secundary_window.destroy()  
                window.deiconify()

        else:
            messagebox.showerror("Error", "Could not retrieve data for the city.")
            window.deiconify()

    
    button_find = Button(window, text='Find', bg="lightblue", pady=5, command=find_city)
    button_find.grid(row=12, column=2)

    window.update_idletasks()
    window.protocol("WM_DELETE_WINDOW", lambda: destroy_application(data))

    update_time(window, cities)

def destroy_application(data):
    respuesta = messagebox.askyesno(title='Exit the application', message='Are you sure you want to exit the application?')
    if respuesta:
        window = data['window']
        window.destroy()

def show_find_city(window, image_path, time_str, temperature, description, humidity, wind): 

    try:
        frame = Frame(window, bg='light blue', bd=2, relief="groove", padx=10, pady=10)
        frame.grid(row=0, column=1, padx=5, pady=5)
       
        image = Image.open(os.path.abspath(image_path))
        photo = ImageTk.PhotoImage(image)
        label_img = Label(frame, image=photo, bg='light blue')
        label_img.image = photo
        label_img.pack()
        
        def add_icon_label(frame, icon_path, text):

            icon = Image.open(os.path.abspath(icon_path))
            icon = icon.resize((20, 20))  
            icon_photo = ImageTk.PhotoImage(icon)
            label = Label(frame, image=icon_photo, text=text, compound="left", bg='light blue', font=(ACLARACION_FONT, 12))
            label.image = icon_photo
            label.pack(anchor="w")  
            return label
        
        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12, "bold"), text="Today").pack()

        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12, "bold"), text=f"  {time_str}").pack()

        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12), text=f"  {description.title()}").pack()

        add_icon_label(frame, "static/images/icono-temperatura.png", f"  {temperature}°C")

        add_icon_label(frame, "static/images/icono-humedad.png", f"  {humidity}%")

        add_icon_label(frame, "static/images/icono-viento.png", f"  {wind} km/h")

        

        

    except Exception as e:
        print(f"Error loading images: {e}")

    return 0

def get_extended_weather(lat, lon):
   

    url_onecall = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    respuesta_extendida = requests.get(url_onecall)
    weather_data = respuesta_extendida.json()

    daily_forecasts = {}
    today_date = datetime.now().date()

    for forecast in weather_data['list']:
        date_text = forecast['dt_txt']  # Date in text format
        date = datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")  # Convert to datetime object
        day = date.date()
        if day == today_date:
            continue  # Skip today's data

        # Initialize day entry if not already present
        if day not in daily_forecasts:
            daily_forecasts[day] = {
                'day_of_week': date.strftime('%A'),
                'temp_max': forecast['main']['temp_max'],
                'temp_min': forecast['main']['temp_min'],
                'weather_description': forecast['weather'][0]['description'],
                'temps': [forecast['main']['temp']]  # List to accumulate all temperatures
            }
        else:
            # Update the temperatures list for the day
            daily_forecasts[day]['temps'].append(forecast['main']['temp'])
            # Update the description only if it's more significant (like rain, storms, etc.)
            daily_forecasts[day]['weather_description'] = forecast['weather'][0]['description']

    # Now calculate the actual min and max temperatures for each day
    for day, info in daily_forecasts.items():
        info['temp_max'] = max(info['temps'])  # Maximum temperature of the day
        info['temp_min'] = min(info['temps'])  # Minimum temperature of the day
        del info['temps']  

    return daily_forecasts

def images_choise(description, local_time):

    if "cloud" in description:
                image_path = "static/images/nublado-transformed.png" if 6 <= local_time.hour < 18 else "static/images/nublado-noche-transformed.png"
    elif "clear" in description:
                image_path = "static/images/soleado.png" if 6 <= local_time.hour < 18 else "static/images/despejado-noche-transformed.png"
    elif "rain" in description:
                image_path = "static/images/lluvia.png"
    elif "storm" in description:
                image_path = "static/images/tormenta.png"
    elif "mist" in description:
                image_path = "static/images/cubierto.png"
    else:
                image_path = "static/images/default.png"
    return image_path

def show_images_extended(window, image_path, day, tempe_max, temp_min, description, row, col):
    try:
        
        frame = Frame(window, bg='light blue', bd=2, relief="groove", padx=10, pady=10)
        frame.grid(row=row, column=col, padx=5, pady=5)
       
        image = Image.open(os.path.abspath(image_path))
        photo = ImageTk.PhotoImage(image)
        label_img = Label(frame, image=photo, bg='light blue')
        label_img.image = photo
        label_img.pack()

        def add_icon_label(frame, icon_path, text):
            icon = Image.open(os.path.abspath(icon_path))
            icon = icon.resize((20, 20))  
            icon_photo = ImageTk.PhotoImage(icon)
            label = Label(frame, image=icon_photo, text=text, compound="left", bg='light blue', font=(ACLARACION_FONT, 12))
            label.image = icon_photo
            label.pack(anchor="w")  
            return label
        
        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12, "bold"), text=f"  {day.title()}").pack()

        Label(frame, bg='light blue', font=(ACLARACION_FONT, 12), text=f"  {description.title()}").pack()

        add_icon_label(frame, "static/images/icono-temperatura.png", f" max {tempe_max}°C")

        add_icon_label(frame, "static/images/icono-temperatura.png", f" min {temp_min}°C")

        Label(frame, bg='light blue', font=(ACLARACION_FONT), text="").pack()

        Label(frame, bg='light blue', font=(ACLARACION_FONT), text="").pack()

        

    except Exception as e:
        print(f"Error loading images: {e}")    

def images_choise_extended(description)  :

    if "cloud" in description:
                image_path = "static/images/nublado-transformed.png" 
    elif "clear" in description:
                image_path = "static/images/soleado.png" 
    elif "rain" in description:
                image_path = "static/images/lluvia.png"
    elif "storm" in description:
                image_path = "static/images/tormenta.png"
    elif "mist" in description:
                image_path = "static/images/cubierto.png"
    else:
                image_path = "static/images/default.png"

    return image_path  

def get_user_location():
    try:
        response = requests.get('https://ipinfo.io')
        data = response.json()
        city = data.get('city')
        return city
    except Exception as e:
        print(f"Error obteniendo la localización: {e}")
        return None
def search_city(search_history, city):
    search_history.append(city)

def update_time(window, cities):
    for widget in window.winfo_children():
        if isinstance(widget, Frame):
            widget.destroy()
    show_cities(cities, window)
    window.after(29000, lambda: update_time(window, cities)) 

def main(): 
    data = {}
    search_history = []
    window = Tk()
    window.title('Climate Now')
    window.geometry('1150x500')
    window.configure(bg='light blue')
    data['window'] = window
    show_window(data, search_history)
    window.mainloop()

main()
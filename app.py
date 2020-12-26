# Modüller - Modules
from flask import Flask,render_template,request,url_for,redirect,Response,flash
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,SelectField,TextField,SubmitField,ValidationError
from selenium import webdriver
from collections import defaultdict
import time
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart # pip install MIME and email-to
from email.mime.text import MIMEText # pip install MIME and email-to
import sys
import os
# Grafik Modülleri - Graphic Modules
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Uygulama - App
app = Flask(__name__)

# İletişim Formu - Contact Form
class ContactForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min = 3,max = 50,message = "İsminizin uzunluğu en az 4 en fazla 50 karakter olamlıdır.")])
    email = StringField("Email Adresi",validators=[validators.Email(message = "Lütfen Geçerli Bir Email Adresi Girin...")])
    subject = StringField("Konu Başlığı",validators=[validators.Length(min = 4,max = 100,message = "Konu Başlığı uzunluğu en az 4 en fazla 100 karakter olmalıdır.")])
    message = TextAreaField("Mesajınız")

# Webdriver Ayarları - Webdriver Settings
op = webdriver.ChromeOptions()
#op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
op.add_argument("--window-size=1366,768")
op.add_argument("--start-maximized")
op.add_argument("--headless")
op.add_argument("--no-sandbox")
op.add_argument("--disable-dev-sh-usage")
#browser = webdriver.Chrome(executable_path= os.environ.get("CHROMEDRIVER_PATH"), chrome_options=op)
browser = webdriver.Chrome(executable_path = "chromedriver.exe", chrome_options=op)

liste = []
bolum_no = ""
bolum_ismi = ""
#yks_data = pd.DataFrame()
data = pd.DataFrame()

# Veri Oluşturma - Data Create
def data_olustur():
    try:
        print("=========TRY a girdi=========")
        csv_data = pd.read_csv("csv\\" + bolum_no + ".csv")
        csv_data = csv_data.drop(["Unnamed: 0"],axis = 1)
        return csv_data
    except FileNotFoundError:
        print("=========EXCEPT e girdi=========")
        #lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        disabledButton = browser.find_element_by_css_selector("#top-link-block")            
        disabledButton.is_enabled = False
        universiteler = []
        universite_adi = []
        taban_puanlari = []
        puan = []
        ders = []
        dersler = []
        ders_not = []
        ders_not_son = []
        ders_notlari = []
        ders_notlari_son = []
    
        columnCount = browser.find_elements_by_css_selector("#mydata > thead > tr:nth-child(1) > th")
        
        sayac_dersler = 8
        while sayac_dersler <= len(columnCount):
            ders = browser.find_elements_by_css_selector("#mydata > thead > tr:nth-child(1) > th:nth-child(" + str(sayac_dersler) + ")")
            for i in ders:
                dersler.append(i.text)
            sayac_dersler += 1
            
        btnControl = browser.find_elements_by_css_selector("#mydata_paginate > ul > li.paginate_button")
        pageCount = 1
        i = 8
        not_sayac = 0
        ders_sayac = 0
        checkpoint = 0
        not_sayac_son = 0
        checkpoint2 = 0
        data_firstPage = pd.DataFrame()
        data_dictionary = defaultdict(list)
        data_Sum = pd.DataFrame()
        while pageCount <= len(btnControl)-3:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            i = 8
            time.sleep(2)
            next_btn = browser.find_element_by_css_selector("#mydata_next > a")
            universite_adi = browser.find_elements_by_css_selector("#mydata > tbody > tr > td:nth-child(2) > small > a")
            puan = browser.find_elements_by_css_selector("#mydata > tbody > tr > td:nth-child(6)")   
            for t in universite_adi:
                universiteler.append(t.text)   
            for j in puan:
                converted_taban_puanlari = float(j.text.replace(',','.'))
                taban_puanlari.append(converted_taban_puanlari) 
            while i <= len(columnCount):
                ders_not = browser.find_elements_by_css_selector("#mydata > tbody > tr > td:nth-child(" + str(i) + ")") 
                for t in ders_not:
                        if t.text == "---":
                            converted_ders_notlari = float(t.text.replace('---',"0.0"))
                        else:
                            converted_ders_notlari = float(t.text.replace(',',"."))
                        ders_notlari.append(converted_ders_notlari)
                i += 1           
            ders_sayac = 0
            while not_sayac <= len(ders_notlari):
                if not_sayac >= len(universite_adi):
                    if not_sayac % len(universite_adi) == 0:
                        data_dictionary[dersler[ders_sayac]].append(ders_notlari[checkpoint:not_sayac])
                        data_firstPage[dersler[ders_sayac]] = ders_notlari[checkpoint:not_sayac]
                        checkpoint = not_sayac
                        ders_sayac += 1
                not_sayac += 1
            data_Sum = pd.concat([data_Sum,data_firstPage],ignore_index = True) 
            next_btn.click()
            pageCount += 1  
        
        universite_adi = browser.find_elements_by_css_selector("#mydata > tbody > tr > td:nth-child(2) > small > a")
        puan = browser.find_elements_by_css_selector("#mydata > tbody > tr > td:nth-child(6)")   
        for t in universite_adi:
            universiteler.append(t.text)   
        for j in puan:
            converted_taban_puanlari_son = float(j.text.replace(',','.'))
            taban_puanlari.append(converted_taban_puanlari_son) 
        i = 8
        while i <= len(columnCount):
            ders_not_son = browser.find_elements_by_css_selector("#mydata > tbody > tr > td:nth-child(" + str(i) + ")") 
            for t in ders_not_son:
                    if t.text == "---":
                        converted_ders_notlari_son = float(t.text.replace('---','0.0'))
                    else:
                        converted_ders_notlari_son = float(t.text.replace(',','.'))
                    ders_notlari_son.append(converted_ders_notlari_son)
            i += 1            
        
        ders_sayac = 0
        liste = []
        while ders_sayac <= len(dersler)-1:
            for i in data_dictionary[dersler[ders_sayac]]:
                for j in i:
                    liste.append(j)
            ders_sayac += 1  
          
        try:
            ders_sayac = 0
            not_sayac_son = 0
            checkpoint2 = 0
            data = pd.DataFrame()
            data_lastPage = pd.DataFrame()
            while not_sayac_son <= len(ders_notlari_son):
                if not_sayac_son >= len(universite_adi):
                    if not_sayac_son % len(universite_adi) == 0:
                        data_dictionary[dersler[ders_sayac]].append(ders_notlari_son[checkpoint2:not_sayac_son])
                        data_lastPage[dersler[ders_sayac]] = ders_notlari_son[checkpoint2:not_sayac_son]
                        checkpoint2 = not_sayac_son
                        ders_sayac += 1
                not_sayac_son += 1
        except ZeroDivisionError:
            print("Bu Bölümü İçeren Üniversite Yok")

        global bolum_ismi
        try:
            bolum_ismi = browser.find_element_by_css_selector("body > div > div.row > div:nth-child(3) > div > div.panel.panel-danger > div > h2 > strong").text
        except:
            bolum_ismi = browser.find_element_by_css_selector("body > div > div.row > div.row > div.container > div.panel.panel-info > div > h2 > strong").text

        data_uni = pd.DataFrame()
        data_uni_name = pd.DataFrame(universiteler)
        data_uni_score = pd.DataFrame(taban_puanlari)
        data_uni = pd.concat([data_uni_name,data_uni_score],axis = 1,ignore_index = True)
        data = pd.concat([data_Sum,data_lastPage],ignore_index = True)
        lastData = pd.concat([data_uni,data],axis = 1)
        lastData.rename(columns={0:"Üniversite Adları"},inplace = True)
        lastData.rename(columns={1:"Taban Puanları"},inplace = True)
        lastData.to_csv("csv\\" + bolum_no + ".csv")
        return lastData

# Tablo Ortalama - Data Mean
def ortalama_hesapla():
    data_mean = pd.DataFrame(round(data[1:].mean()))
    data_mean = data_mean.T
    data_mean.insert(0, 'Üniversite Adları', "Ortalama Taban Puanları ve Net Sayıları")
    return data_mean

# Karışık Tablo - Mix Table
def mix_table():
    data_last = pd.concat([data.head(1),data.tail(1)],axis = 0)
    data_mix = pd.concat([data_last,ortalama_hesapla()],axis = 0,ignore_index = True)
    return data_mix

# Alan Yarat - Create Figure
def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    data_mix = mix_table()
    axis.bar(
        data_mix["Üniversite Adları"], 
        data_mix["Taban Puanları"], 
        color = '#ce1b45',
        align = "center"
    )
    axis.set_facecolor('#212529')
    axis.set_xticklabels(data_mix["Üniversite Adları"], rotation = -7, fontsize = 9)
    return fig

# Karışık Grafik - Mix Graphics
@app.route("/plot.png")
def mix_graphic():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)  
    return Response(output.getvalue(), mimetype = "image/png")

# Tablo Oluşturma - Table Create
def table_create():
    global bolum_ismi
    data_head = data.head(1)
    data_last = data.tail(1)
    data_mean = ortalama_hesapla()
    data_mix_table = mix_table()
    data_mix_graphic = mix_graphic()
    return render_template('tables.html',  
    bolum_adi = bolum_ismi,
    tables_all=[data.to_html(classes='table table-dark table-bordered table-hover table-striped data position-sticky')],
    tables_last=[data_last.to_html(classes='table table-dark table-bordered table-hover table-striped data')],
    tables_head=[data_head.to_html(classes='table table-dark table-bordered table-hover table-striped data')], 
    tables_mean = [data_mean.to_html(classes='table table-dark table-bordered table-hover table-striped data')], 
    tables_mix = [data_mix_table.to_html(classes='table table-dark table-bordered table-hover table-striped data')], 
    graphic_mix = data_mix_graphic,
    titles=data.columns.values
    )

# Bölümleri Listele - List Programs
def list_programs(program_url):
    sayac = 1
    url = program_url
    program_list = []
    browser.get(url)
    button1 = browser.find_element_by_xpath("//*[@id='flip2']")
    button1.click()
    button2 = browser.find_element_by_xpath("//*[@id='flip2']/div/div[2]/div/form/div/div/div/button")
    button2.click()
    bolum = browser.find_elements_by_css_selector("#flip2 > div > div.face.back > div > form > div > div > div > div > ul > li > a")
    for i in bolum:
        program_list.append(i)
        sayac += 1
    return program_list

# Bölüm Seç - Select Program
def select_program(selected_program_no, selected_program_type):
    sayac2 = 0
    selected_program = selected_program_no
    while sayac2 <= len(liste):
        if(selected_program-1 == sayac2):
            global bolum_no
            bolum_no = selected_program_type + "-" + "" + str(sayac2)
            liste[sayac2].click()
            if selected_program_type == "lisans":
                tablo_goster = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[2]//*[@id='bs-collapse']/div/div/h4")
            else:
                tablo_goster = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[3]/div/div/div/h4/a")
            tablo_goster.click()
            data = data_olustur()
        sayac2 += 1
    return data

# Ana Sayfa - Home Page
@app.route("/")
def index():
    try:
        return onlisans_page()
    except:
        browser.close()
        return onlisans_page()

# Önlisans Programı - Associate Degree Program
@app.route("/onlisans")
def onlisans_page():
    global liste
    liste = list_programs("https://yokatlas.yok.gov.tr/onlisans-anasayfa.php")
    return render_template("onlisans.html",liste = liste)

# Önlisans Tablo - Associate Program Table
@app.route("/onlisans-hesapla" , methods=['GET', 'POST'])
def onlisans_table():
    select = int(request.form.get('onlisans_sayac'))
    global data
    data = select_program(select, "onlisans")
    return table_create()

# Lisans Programı - Undergraduate Program
@app.route("/lisans")
def lisans_page():
    global liste
    liste = list_programs("https://yokatlas.yok.gov.tr/lisans-anasayfa.php")
    return render_template("lisans.html",liste = liste)

# Lisans Tablo - Undergraduate Program Table
@app.route("/lisans-hesapla", methods=['GET', 'POST'])
def lisans_table():
    select = int(request.form.get('lisans_sayac'))
    global data
    data = select_program(select, "lisans")
    return table_create()

# Hakkımızda - About
@app.route("/about")
def about():
    return render_template("about.html")

# İletişim - Contact
@app.route("/contact",methods = ["GET","POST"])
def contact():
    form = ContactForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        subject = form.subject.data
        email = form.email.data
        message = form.message.data
        mesaj = MIMEMultipart()
        mesaj["From"] = email
        mesaj["To"] = "kacnet.tk@gmail.com"
        mesaj["Subject"] = subject
        yazi = name + " adlı kullanıcı tarafından;\n\n\n\n" + subject.upper() + "\n--------------------------------------\n" + message + "\n--------------------------------------\n" + "gönderilmiştir." + "\n\n" + email
        mesaj_govdesi = MIMEText(yazi,"plain")
        mesaj.attach(mesaj_govdesi)
        try:
            mail = smtplib.SMTP("smtp.gmail.com",587)
            mail.ehlo()
            mail.starttls()
            mail.login("kacnet.tk@gmail.com","Ekox.54321")
            mail.sendmail(mesaj["From"],mesaj["To"],mesaj.as_string())
            mail.close()
            return render_template("contact.html",form = form,success = True)
        except:
            mail.close()
            return render_template("contact.html",form = form)
    else:
        return render_template("contact.html",form = form)

# Tablolar - Tables
@app.route("/tables")
def table():
    return render_template("tables.html")

if __name__ == "__main__":
    app.run(debug = True)
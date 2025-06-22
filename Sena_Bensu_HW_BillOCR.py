import cv2
import pytesseract
import re
import os

# Tesseract yolu
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

image_paths = [
    r"C:\Users\Lenovo\Desktop\TURKCELL\OCR\fatura.png",
    r"C:\Users\Lenovo\Desktop\TURKCELL\OCR\1.jpg",
    r"C:\Users\Lenovo\Desktop\TURKCELL\OCR\2.png",
    r"C:\Users\Lenovo\Desktop\TURKCELL\OCR\3.jpg",
]

for image_path in image_paths:
    print(f"\n----- {os.path.basename(image_path)} işlemi başlatıldı -----------")

    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR ayarları
    config = r'--oem 3 --psm 4'
    text = pytesseract.image_to_string(thresh, lang='tur+eng', config=config)

    # Eğer çıktı kötü ise tersini dene
    if len(text.strip()) < 10:
        inverted = cv2.bitwise_not(thresh)
        text = pytesseract.image_to_string(inverted, lang='tur+eng', config=config)

    print("OCR Çıktısı:\n", text)

    lines = [line.lower() for line in text.splitlines()]  # Satırları küçük harfe çevirip al

    ## Fatura sonucu bulunmaya başlanıyorrr------------------->>>>

    total_lines = [line for line in lines if re.search(r'\btotal\b', line)]  # "total" kelimesini tam eşleşme ile içeren

    if total_lines:# Son satırı al (genelde en son total tutar gerçek tutar)
        final_line = total_lines[-1]
        print("Bulunan toplam satır:", final_line)
    else:
        print("Total kelimesi geçen satır bulunamadı, alternatif arama yapılıyor...")

        keywords = ["grand total", "total amount", "net amount","fatura"]   # Anahtar kelimelerle arama (örneğin grand total, net amount gibi)
        amount = None
        for line in lines:
            if any(k in line for k in keywords):
                match = re.search(r'\d+\.\d{2}', line)
                if match:
                    amount = match.group()
                    print(f"Anahtar kelime '{k}' ile bulunan tutar:", amount)
                    break

        if not amount:# Hiçbir şey bulunmazsa metindeki tüm fiyatları bul, sonuncusunu al
            all_prices = re.findall(r'\d+\.\d{2}', text)
            if all_prices:
                print("Fallback: Metindeki tüm fiyatlar:", all_prices)
                print("Son fiyat otomatik toplam olarak alındı (güvenilmez olabilir):", all_prices[-1])
            else:
                print("Hiç fiyat bulunamadı.")


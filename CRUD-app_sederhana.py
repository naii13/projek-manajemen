import mysql.connector
import time
import os
import sys
from datetime import datetime
from pyfiglet import Figlet
from colorama import Fore, Style
from rich.console import Console
from rich.panel import Panel

connection = mysql.connector.connect(host="127.0.0.1", user="root", password="", database="project")

cursor = connection.cursor()

# Warna ANSI
warna_merah = "\033[91m"
warna_hijau = "\033[92m"
warna_kuning = "\033[93m"
warna_biru = "\033[94m"
warna_reset = "\033[0m"

def loading():
    loading_message = f"{warna_biru}Memuat"
    for _ in range(3):
        sys.stdout.write(f"\r{loading_message}{'.' * (_ % 3 + 1)}{warna_reset}")
        sys.stdout.flush()
        time.sleep(0.5)

    sys.stdout.write("\r" + " " * len(loading_message + '...') + "\r")
    sys.stdout.flush()


def loading2():
    clear_screen()
    loading_message = f"loading{warna_biru}"
    spinner = ['◜', '◝', '◞', '◟'] 
    for _ in range(2):
        for symbol in spinner:
            sys.stdout.write(f"\r{loading_message} {symbol}{warna_reset}")  
            sys.stdout.flush()  
            time.sleep(0.2)  

def generateKodePasien():
    # Mengambil kode pasien terakhir
    query = "SELECT kode FROM pasien ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()

    if result and result[0]: 
        # Mengambil angka terakhir dari kode pasien dan menambahkannya
        last_code = result[0]  
        if last_code.startswith("P"): 
            number = int(last_code[1:]) + 1  
            new_code = f"P{number:03d}"  
        else:
            new_code = "P001"  
    else:
        new_code = "P001"

    return new_code

# Fungsi untuk mencari index pasien berdasarkan kode
def cariIndex(dataBaru):
    query = "SELECT id FROM pasien WHERE kode = %s"
    cursor.execute(query, (dataBaru,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Mengembalikan id pasien yang ditemukan
    return -1  # Jika tidak ada pasien dengan kode tersebut, kembalikan -1

# Fungsi untuk menampilkan semua pasien
def daftar_pasien():
    query = "SELECT * FROM pasien WHERE status != 'Pulang'"  
    cursor.execute(query)
    result = cursor.fetchall()
    
    if result:
        print(f"\n{warna_biru}Daftar Pasien{warna_reset}\n")
        print("NO    |Kode\t\t|Nama\t\t|Ruangan\t|Alamat\t\t|Umur")
        print("-" * 85)
        
        for i, pasien in enumerate(result, 1):
            no = f"{i:<6}"
            kode = f"{pasien[1]:<17}"
            nama = f"{pasien[2]:<15}"
            ruangan = f"{pasien[3]:<15}"
            alamat = f"{pasien[4]:<15}"
            umur = f"{pasien[5]:<5}"
            
            print(f"{no}|{kode}|{nama}|{ruangan}|{alamat}|{umur}")
    else:
        print(f"{warna_merah}Daftar Pasien Kosong{warna_reset}")


# Fungsi untuk menampilkan daftar pasien dan memilih menu
def menampilkanDaftarPasien():
    while True:
        print('''
        1. Melihat Daftar Seluruh Pasien
        2. Melihat Nama Pasien Melalui Kode
        3. Kembali ke Menu Utama
        ''')
        a = input("Masukkan pilihan (1-3): ")
        if a == '1':
            daftar_pasien()
        elif a == '2':
            cariKode = input("Masukkan Kode Pasien: ").upper()
            index = cariIndex(cariKode)
            if index != -1:
                query = "SELECT * FROM pasien WHERE id = %s"
                cursor.execute(query, (index,))
                data = cursor.fetchone()
                print("Kode\t\t|Nama\t\t|Ruangan\t|Alamat\t\t\t|Umur")
                print(f"{data[1]}\t\t|{data[2]}\t\t|{data[3]}\t\t|{data[4]}\t\t\t|{data[5]}")
            else:
                print(f"{warna_merah}Pasien tidak ditemukan.{warna_reset}")
        elif a == '3':
            break
        else:
            print(f"{warna_merah}Pilihan tidak valid.{warna_reset}")

# Fungsi untuk menambah pasien
def menambahPasien():
    while True:
        print(''' 
            1. Pasien Check IN
            2. Kembali ke Menu Utama
                ''')
        a = input("Masukkan pilihan (1-2): ")
        
        if a == '1':
            tambah_kode = generateKodePasien()  # Kode pasien otomatis
            index = cariIndex(tambah_kode)
            if index != -1:
                print(f'{warna_merah}=============== Pasien Yang Ingin Ditambah Sudah Ada ================={warna_reset}')
                continue
            
            tambah_nama = input('Masukkan Nama Pasien: ').capitalize()
            lihat_kamar_tersedia()

            tambah_kamar= input('Masukkan Nomor Kamar: ').upper()
            tambah_alamat = input('Masukkan Alamat: ').capitalize()
            while True:
                try:
                    tambah_umur = int(input("Masukkan Umur: "))
                    break  
                except ValueError:
                    print(f"{warna_merah}Harap masukkan angka.{warna_reset}")

            checker = input(f"Apakah Anda ingin menambah Pasien? (Y/N) = ").upper()

            if checker == 'N':
                print(f"{warna_merah}Data tidak jadi ditambah{warna_reset}")
            elif checker == 'Y':
                query = "INSERT INTO pasien (kode, nama, ruangan, alamat, umur) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (tambah_kode, tambah_nama, tambah_kamar, tambah_alamat, tambah_umur))

                query_update_kamar = "UPDATE kamar SET status = 'Tidak Tersedia' WHERE nomor_kamar = %s"
                cursor.execute(query_update_kamar, (tambah_kamar,))
                connection.commit()
                loading()
                print(f"\n{warna_hijau}Pasien berhasil ditambahkan.{warna_reset}")
                break

        elif a == '2':
            menu_utama()  
            break

# Fungsi untuk mengedit data pasien
def mengeditPasien():
    while True:
        print('''
                1. Edit Data Pasien
                2. Kembali ke Menu Utama
                ''')
        a = input("Masukkan pilihan (1-2): ")
        if a == '1':
            daftar_pasien()
            edit_kode = input('\nMasukkan Kode Pasien yang Ingin Diedit: ').upper()
            index = cariIndex(edit_kode)
            if index == -1:
                print('=============== Pasien Tidak Ditemukan =================')
                continue
            edit_nama = input('Masukkan Nama Baru (Biarkan kosong jika tidak ingin mengubah): ').capitalize()
            edit_ruangan = input('Masukkan Ruangan Baru (Biarkan kosong jika tidak ingin mengubah): ').upper()
            edit_alamat = input('Masukkan Alamat Baru (Biarkan kosong jika tidak ingin mengubah): ').capitalize()
            edit_umur = input('Masukkan Umur Baru (Biarkan kosong jika tidak ingin mengubah): ')
            edit_status = input('Masukkan Status Baru (Biarkan kosong jika tidak ingin mengubah): ').capitalize()

            query = "UPDATE pasien SET nama = COALESCE(NULLIF(%s, ''), nama), ruangan = COALESCE(NULLIF(%s, ''), ruangan), alamat = COALESCE(NULLIF(%s, ''), alamat), umur = COALESCE(NULLIF(%s, ''), umur), status = COALESCE(NULLIF(%s, ''), status) WHERE id = %s"
            cursor.execute(query, (edit_nama, edit_ruangan, edit_alamat, edit_umur if edit_umur.isdigit() else None, edit_status, index))
            connection.commit()
            loading()
            print(f"\n{warna_hijau}Data pasien berhasil diupdate.{warna_reset}")
            daftar_pasien()
        elif a == '2':
            break
        else:
            print(f"{warna_merah}Pilihan tidak valid.{warna_reset}")

# Fungsi untuk checkout pasien
def checkoutPasien():
    while True:
        print(''' 
                1. Check OUT pasien 
                2. Kembali ke Menu Utama 
               ''')
        a = input("Masukkan pilihan (1-2): ")
        if a == '1':
            daftar_pasien()
            checkout_kode = input("\nMasukkan Kode Pasien yang Ingin Check Out: ").upper()
            index = cariIndex(checkout_kode)
            if index == -1:
                print(f"{warna_merah}Pasien tidak ditemukan.{warna_reset}")
                continue

            # Menanyakan konfirmasi untuk checkout
            konfirmasi = input(f"{warna_hijau}Apakah Anda yakin ingin checkout pasien dengan kode {checkout_kode}? (y/n): {warna_reset}").lower()
            if konfirmasi == 'y':
                query = "SELECT * FROM pasien WHERE id = %s"
                cursor.execute(query, (index,))
                data = cursor.fetchone()
                query_history = "INSERT INTO history (id, kode_pasien, nama_pasien, tindakan) VALUES (%s, %s, %s, %s)"
                cursor.execute(query_history, (data[0], data[1], data[2], 'Check OUT'))  

                connection.commit()
                query = "UPDATE pasien SET status = 'Pulang' WHERE id = %s"
                cursor.execute(query, (index,))
                connection.commit()
                loading()
                print(f"{warna_hijau}\nPasien berhasil checkout.{warna_reset}")
                menampilkanRiwayat()  
                break
            else:
                print(f"{warna_merah}Checkout dibatalkan.{warna_reset}")
                continue

        elif a == '2':
            break
        else:
            print(f"{warna_merah}Pilihan Tidak Valid.{warna_reset}")

# Fungsi untuk menampilkan riwayat kunjungan pasien
def menampilkanRiwayat():

    while True:
        print(''' 
                1. Lihat Semua Riwayat
                2. Lihat Riwayat Berdasarkan Kode Pasien
                3. Kembali ke Menu Utama
                ''')
        a = input("Masukkan pilihan (1-3): ")
        if a == '1':
            
            query = "SELECT * FROM history ORDER BY waktu_keluar ASC"
            cursor.execute(query)
            result = cursor.fetchall()
            if result:
                print(f"{warna_biru}Riwayat Kunjungan Pasien{warna_reset}\n")
                print(f"{'Kode Pasien':<15}| {'Nama Pasien':<20}| {'Tindakan':<20}| {'Tanggal':<20}")
                print("-" * 80)
                for i, row in enumerate(result, 1):
                    kode_pasien = f"{row[1]:<15}"
                    nama_pasien = f"{row[2] or 'N/A':<20}"  
                    tindakan = f"{row[3]:<20}"
                    waktu_keluar = f"{row[4]:<20}"
                    if isinstance(row[4], datetime):
                        waktu_keluar = row[4].strftime('%Y-%m-%d %H:%M:%S')  
                    else:
                        waktu_keluar = row[4] if row[4] else 'Tanggal tidak tersedia'

                    print(f"{kode_pasien}| {nama_pasien}| {tindakan}| {waktu_keluar}")
            else:
                print(f"{warna_merah}Tidak ada riwayat pasien{warna_reset}")

        elif a == '2':
            kode_pasien = input("Masukkan Kode Pasien: ").upper()
            query = "SELECT * FROM history WHERE kode_pasien = %s"
            cursor.execute(query, (kode_pasien,))
            result = cursor.fetchall()
            if not result:
                print(f"{warna_merah}Tidak ada riwayat untuk kode pasien ini.{warna_reset}")
                continue
            print("Kode Pasien\t| Nama Pasien\t| Tindakan\t\t| Tanggal")
            print("-" * 77)
            for row in result:
                print(f"{row[1]}\t\t| {row[2] or 'N/A'}\t\t| {row[3]}\t\t| {row[4]}")
        elif a == '3':
            break
        else:
            print(f"{warna_merah}Pilihan tidak valid.{warna_reset}")

# fungsi Melihat daftar kamar yang statusnya 'Tersedia'.
def lihat_kamar_tersedia():
    
    query = "SELECT * FROM kamar WHERE status = 'Tersedia'"
    cursor.execute(query)
    result = cursor.fetchall()

    if result:
        print(f"\n{warna_biru}Daftar Kamar Tersedia{warna_reset}\n")
        print("NO\t| Nomor Kamar\t| Jenis Kamar\t| Status")
        print("-" * 50)  
        for i, kamar in enumerate(result, start=1):
            print(f"{i}\t| {kamar[1]}\t\t| {kamar[2]}  \t\t| {kamar[3]}")
        print("\n")
    else:
        print("Tidak ada kamar yang tersedia.")

def tambah_kamar():
    while True:
        nomor_kamar = input("Masukkan nomor kamar: ").strip()  
        if not nomor_kamar:  
            print(f"{warna_merah}Nomor kamar tidak boleh kosong. Silakan masukkan nomor kamar yang valid.{warna_reset}")
            continue  

        # Mengecek apakah kamar dengan nomor yang sama sudah ada dan masih tersedia
        query_cek_kamar = "SELECT * FROM kamar WHERE nomor_kamar = %s"
        cursor.execute(query_cek_kamar, (nomor_kamar,))
        result = cursor.fetchall()
        if result:
            print(f"{warna_merah}Kamar dengan nomor '{nomor_kamar}' sudah ada. Silakan masukkan nomor kamar yang berbeda.{warna_reset}\n")
            continue  

        while True:
            jenis_kamar = input("Masukkan jenis kamar (VIP/Reg/ICU): ").strip()  
            if not jenis_kamar:  
                print(f"{warna_merah}Jenis kamar tidak boleh kosong. Silakan masukkan jenis kamar yang valid.{warna_reset}")
            else:
                break 

        konfirmasi = input(f"Apakah Anda ingin menambahkan kamar '{nomor_kamar}' dengan jenis '{jenis_kamar}'? (Y/N): ").strip().upper()
        if konfirmasi == 'Y':
            query = "INSERT INTO kamar (nomor_kamar, jenis_kamar) VALUES (%s, %s)"
            values = (nomor_kamar, jenis_kamar)
            cursor.execute(query, values)
            connection.commit()
            print(f"{warna_hijau}Kamar '{nomor_kamar}' berhasil ditambahkan{warna_reset}.\n")
            break 
        else:
            print(f"{warna_merah}Proses penambahan kamar dibatalkan.{warna_reset}\n")
            continue

def hapus_kamar():
    """Menghapus kamar berdasarkan nomor."""
    lihat_kamar_tersedia()
    nomor_kamar = input("Masukkan Nomor kamar yang ingin dihapus: ")
    check = input(f"Apakah anda ingin menghapus kamar {nomor_kamar}?(Y/N): ").upper()
    if check == 'Y':
        query = "DELETE FROM kamar WHERE nomor_kamar = %s"
        cursor.execute(query, (nomor_kamar,))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"{warna_hijau}Kamar dengan nomor {nomor_kamar} berhasil dihapus.{warna_reset}")
        else:
            print(f"{warna_merah}nomor kamar tidak ditemukan.{warna_reset}\n")
    else:
        print("kembali ke menu utama\n")
        menu_utama()

#Mengedit informasi kamar berdasarkan nomor.
def edit_kamar():
    
    lihat_kamar_tersedia()
    nomor_kamar = input("Masukkan nomor kamar yang ingin diedit: ")

    print("\nApa yang ingin Anda edit?")
    print("1. Nomor Kamar")
    print("2. Jenis Kamar")
    pilihan = input("Pilih opsi (1/2): ")

    if pilihan == "1":
        nomor_baru = input("Masukkan nomor kamar baru: ")
        query = "UPDATE kamar SET nomor_kamar = %s WHERE nomor_kamar = %s"
        cursor.execute(query, (nomor_baru, nomor_kamar))
        if cursor.rowcount > 0:
            print(f"Kamar dengan nomor {nomor_kamar} berhasil diperbarui.")
        else:
            print(f"{warna_merah}Tidak ada yang diubah{warna_reset}\n")

    elif pilihan == "2":
        jenis_baru = input("Masukkan jenis kamar baru (VIP/Reg/ICU): ").capitalize()
        query = "UPDATE kamar SET jenis_kamar = %s WHERE nomor_kamar = %s"
        cursor.execute(query, (jenis_baru, nomor_kamar))
        if cursor.rowcount > 0:
            print(f"Kamar dengan nomor {nomor_kamar} berhasil diperbarui.")
        else:
            print(f"{warna_merah}Tidak ada yang diubah{warna_reset}\n")
    else:
        print(f"{warna_merah}Pilihan tidak valid.{warna_reset}\n")
        return

    connection.commit()

# Menu utama untuk navigasi program
console = Console()    
def menu_utama():
    
    while True:
        judul = "MENU UTAMA"
        pilihan = """
        1. Pasien
        2. Kamar
        3. Karyawan
        4. Log out
        """

        panel = Panel(
            f"{pilihan}",
            title=judul,
            title_align="left",
            border_style="blue",
            padding=(0, 0),
            width=25
        )

        console.print(panel)

        pilihanmenu = input("Pilih menu yang sesuai (1-4): ")
        print("\n")

        if pilihanmenu == '1':       #pilih menu pasien
            menu_pasien = '''
        1. Tambah Pasien
        2. Daftar Pasien
        3. Edit Pasien
        4. check out pasien
        5. Lihat Riwayat Pasien
        6. Kembali Ke Menu Utama
        '''

            panel = Panel(
                menu_pasien,
                title="Pasien", 
                title_align="left",
                border_style="green", 
                padding=(0, 0), 
                width=40 
            )
            console.print(panel)

            menu_pasien = input("Masukkan pilihan (1-6): ")

            if menu_pasien == '1':
                menambahPasien()
            elif menu_pasien == '2':
                menampilkanDaftarPasien()
            elif menu_pasien == '3':
                mengeditPasien()
            elif menu_pasien == '4':
                checkoutPasien()
            elif menu_pasien == '5':
                menampilkanRiwayat()
            elif menu_pasien == '6':
                menu_utama()
            else:
                print(f"{warna_merah}pilihan tidak valid{warna_reset}\n")

        elif pilihanmenu == '2':    #pilih menu kamar
            menu_kamar = ('''
        1. Tambah Kamar
        2. Lihat Kamar Tersedia
        3. Hapus Kamar
        4. Edit Kamar
        5. kembali ke Menu Utama
                ''')
        
            panel = Panel(
                menu_kamar,
                title="kamar", 
                title_align="left",
                border_style="green", 
                padding=(0, 0), 
                width=40 
            )
            console.print(panel)

            pilihan = input("Masukkan Pilihan (1-5): ")
            print("\n")

            if pilihan == "1":
                tambah_kamar()
            elif pilihan == "2":
                lihat_kamar_tersedia()
            elif pilihan == "3":
                hapus_kamar()
            elif pilihan == "4":
                edit_kamar()
            elif pilihan == "5":
                menu_utama()
            else:
                print(f"{warna_merah}pilihan tidak valid{warna_reset}\n")

        elif pilihanmenu == '3':    #pilih menu karyawan
            judul = "Daftar Karyawan"
            daftar = """
        1. Naila Huwaida Nisa(230705018)
        2. Nayla safhira(230705032)
        3. Risma Mahara (230705029)
            """

            panel = Panel(
                f"{daftar}",
                title=judul,
                title_align="left",
                border_style="yellow",  
                padding=(0, 0),  
                width=45)  

            console.print(panel)
        
        elif pilihanmenu == '4':    #pilih menu log out
            keluar = input("Apakah Anda ingin keluar? (Y/N): ")
            if keluar == 'Y' or keluar == 'y':
                loading()
                print(f"\n\t{warna_hijau}Terima kasih, sampai jumpa!{warna_reset}")
                break
            else:
                print("Kembali ke menu utama.\n")
                # menu_utama()
        else:
            print("Pilihan tidak valid.\n")

# Fungsi untuk mewarnai teks ASCII
def colorize_text(ascii_art, frame):
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    RESET = Style.RESET_ALL

    colored_text = ""
    for i, char in enumerate(ascii_art):
        if char != " ":
            color = RED if (i + frame) % 2 == 0 else YELLOW
            new_line = color + char + RESET
        else:
            new_line = char
        colored_text += new_line
    return colored_text

# Fungsi untuk membersihkan layar
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Fungsi untuk menampilkan animasi ASCII
def show_ascii_animation(text):
    f = Figlet(font="slant")
    frame = 0
    try:
        while frame < 10:  
            clear_screen()
            ascii_art = f.renderText(text)
            colored_ascii = colorize_text(ascii_art, frame)
            print(colored_ascii)
            time.sleep(0.2)
            frame += 1
    except KeyboardInterrupt:
        print("\nAnimasi dihentikan.")
        
if __name__ == "__main__":
    loading2()
    show_ascii_animation("HOSPITAL +")
    print("Selamat datang di Sistem Manajemen Rumah Sakit!")
    menu_utama()


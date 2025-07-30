import qrcode
from PIL import Image
import os

class QRISGenerator:
    def __init__(self, config):
        self.config = {
            'merchant_id': config.get('merchant_id'),
            'base_qr_string': config.get('base_qr_string'),
            'logo_path': config.get('logo_path')
        }

    def generate_qr_with_logo(self, qr_string):
        try:
            # Buat QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_string)
            qr.make(fit=True)
            
            # Buat gambar QR
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Tambah logo jika ada
            if self.config['logo_path'] and os.path.exists(self.config['logo_path']):
                logo = Image.open(self.config['logo_path'])
                # Hitung ukuran logo (25% dari ukuran QR)
                logo_size = int(qr_image.size[0] * 0.25)
                logo = logo.resize((logo_size, logo_size))
                
                # Hitung posisi logo
                pos = ((qr_image.size[0] - logo.size[0]) // 2,
                       (qr_image.size[1] - logo.size[1]) // 2)
                
                # Buat background putih untuk logo
                white_bg = Image.new('RGB', (logo_size + 10, logo_size + 10), 'white')
                qr_image.paste(white_bg, (pos[0] - 5, pos[1] - 5))
                
                # Tambah logo
                qr_image.paste(logo, pos)
            
            return qr_image
            
        except Exception as e:
            raise Exception(f"Gagal generate QR: {str(e)}")

    def generate_qr_string(self, amount):
        try:
            qris_base = self.config['base_qr_string'][:-4].replace("010211", "010212")
            nominal_str = str(amount)
            nominal_tag = f"54{len(nominal_str):02d}{nominal_str}"
            insert_position = qris_base.find("5802ID")
            
            if insert_position == -1:
                raise Exception("Format QRIS tidak valid")
            
            qris_with_nominal = qris_base[:insert_position] + nominal_tag + qris_base[insert_position:]
            checksum = self._calculate_crc16(qris_with_nominal)
            return qris_with_nominal + checksum
            
        except Exception as e:
            raise Exception(f"Gagal generate QR string: {str(e)}")

    def _calculate_crc16(self, data):
        crc = 0xFFFF
        for byte in data.encode('utf-8'):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
        return f"{(crc & 0xFFFF):04X}" 
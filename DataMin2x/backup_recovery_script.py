#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Safe Data Recovery & Merge Script
Backup dosyalarındaki veri kaybını tespit eder ve güvenli birleştirme yapar
"""

import json
import glob
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Set, Tuple
from collections import defaultdict

class BackupRecoveryManager:
    """Backup dosyalarını analiz eden ve güvenli birleştirme yapan sınıf"""
    
    def __init__(self):
        self.logger_data = []
        self.statistics = {
            'total_files_analyzed': 0,
            'total_qa_pairs_found': 0,
            'duplicates_removed': 0,
            'data_loss_detected': 0,
            'recovered_data': 0
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log mesajı"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.logger_data.append(log_entry)
        
    def get_qa_hash(self, qa_pair: Dict) -> str:
        """Q&A çifti için unique hash üret"""
        text = f"{qa_pair.get('soru', '')}{qa_pair.get('cevap', '')}"
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    def analyze_backup_file(self, file_path: str) -> Dict:
        """Backup dosyasını analiz et"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                self.log(f"⚠️ {file_path}: Geçersiz format (list değil)", "WARNING")
                return {'file': file_path, 'count': 0, 'data': [], 'valid': False}
                
            # İlk ve son verinin soru/cevap hash'lerini al
            first_hash = self.get_qa_hash(data[0]) if data else ""
            last_hash = self.get_qa_hash(data[-1]) if data else ""
            
            analysis = {
                'file': file_path,
                'count': len(data),
                'data': data,
                'valid': True,
                'first_hash': first_hash,
                'last_hash': last_hash,
                'timestamp': os.path.basename(file_path).split('_')[-1].replace('.json', '')
            }
            
            self.log(f"✅ {os.path.basename(file_path)}: {len(data):,} veri")
            return analysis
            
        except Exception as e:
            self.log(f"❌ {file_path} okunamadı: {e}", "ERROR")
            return {'file': file_path, 'count': 0, 'data': [], 'valid': False}
            
    def detect_data_loss(self, analyses: List[Dict]) -> Dict:
        """Veri kaybını tespit et"""
        self.log("\n🔍 === VERİ KAYBI ANALİZİ ===")
        
        # Batch numaralarına göre sırala
        valid_analyses = [a for a in analyses if a['valid']]
        valid_analyses.sort(key=lambda x: int(x['file'].split('_')[2]))
        
        loss_report = {
            'has_loss': False,
            'lost_ranges': [],
            'gaps': [],
            'overlaps': [],
            'total_expected': 0,
            'total_found': 0
        }
        
        for i, analysis in enumerate(valid_analyses):
            batch_num = int(analysis['file'].split('_')[2])
            expected_count = (batch_num + 1) * 50 * 20  # Her batch 50 QA * 20 varyant
            actual_count = analysis['count']
            
            if actual_count < expected_count * 0.8:  # %80'den az varsa sorun var
                gap_size = expected_count - actual_count
                loss_report['has_loss'] = True
                loss_report['gaps'].append({
                    'batch': batch_num,
                    'expected': expected_count,
                    'found': actual_count,
                    'lost': gap_size
                })
                
        # Toplam beklenen vs bulunan
        if valid_analyses:
            last_batch = int(valid_analyses[-1]['file'].split('_')[2])
            loss_report['total_expected'] = (last_batch + 1) * 50 * 20
            loss_report['total_found'] = sum(a['count'] for a in valid_analyses)
            
        self.statistics['data_loss_detected'] = len(loss_report['gaps'])
        
        if loss_report['has_loss']:
            self.log(f"🚨 VERİ KAYBI TESPİT EDİLDİ!", "ERROR")
            for gap in loss_report['gaps']:
                self.log(f"   Batch {gap['batch']}: {gap['lost']:,} veri kayıp", "ERROR")
        else:
            self.log("✅ Veri kaybı tespit edilmedi")
            
        return loss_report
        
    def smart_merge_data(self, analyses: List[Dict]) -> List[Dict]:
        """Akıllı veri birleştirme - duplicate kontrolü ile"""
        self.log("\n🔄 === AKILLI BİRLEŞTİRME ===")
        
        seen_hashes: Set[str] = set()
        merged_data: List[Dict] = []
        duplicate_count = 0
        
        # Batch numarasına göre sırala (en eskiden yeniye)
        valid_analyses = [a for a in analyses if a['valid']]
        valid_analyses.sort(key=lambda x: int(x['file'].split('_')[2]))
        
        for analysis in valid_analyses:
            file_name = os.path.basename(analysis['file'])
            new_count = 0
            
            for qa_pair in analysis['data']:
                qa_hash = self.get_qa_hash(qa_pair)
                
                if qa_hash not in seen_hashes:
                    seen_hashes.add(qa_hash)
                    merged_data.append(qa_pair)
                    new_count += 1
                else:
                    duplicate_count += 1
                    
            self.log(f"📁 {file_name}: {new_count:,} yeni veri eklendi")
            
        self.statistics['duplicates_removed'] = duplicate_count
        self.statistics['recovered_data'] = len(merged_data)
        
        self.log(f"✅ Toplam {len(merged_data):,} benzersiz veri birleştirildi")
        self.log(f"🔄 {duplicate_count:,} duplicate kaldırıldı")
        
        return merged_data
        
    def create_recovery_report(self, loss_report: Dict, merged_count: int) -> Dict:
        """Kurtarma raporu oluştur"""
        report = {
            "recovery_timestamp": datetime.now().isoformat(),
            "analysis_summary": {
                "files_analyzed": self.statistics['total_files_analyzed'],
                "total_qa_pairs_found": self.statistics['total_qa_pairs_found'],
                "duplicates_removed": self.statistics['duplicates_removed'],
                "final_merged_count": merged_count
            },
            "data_loss_analysis": loss_report,
            "recovery_status": "PARTIAL" if loss_report['has_loss'] else "COMPLETE",
            "recommendations": [],
            "log_messages": self.logger_data
        }
        
        if loss_report['has_loss']:
            report["recommendations"].extend([
                "⚠️ Veri kaybı tespit edildi - backup sistemi düzeltilmeli",
                "🔧 data_augmenter.py'daki backup fonksiyonu güncellenmelidir",
                "💾 Resume fonksiyonu önceki backup'ları yüklemeli"
            ])
        else:
            report["recommendations"].append("✅ Tüm veriler başarıyla kurtarıldı")
            
        return report
        
    def run_recovery(self) -> Tuple[List[Dict], Dict]:
        """Ana kurtarma işlemini çalıştır"""
        self.log("🚀 === BACKUP RECOVERY BAŞLATILDI ===")
        
        # 1. Backup dosyalarını bul
        backup_files = glob.glob('backups/backup_batch_*.json')
        if not backup_files:
            self.log("❌ Backup dosyası bulunamadı!", "ERROR")
            return [], {}
            
        backup_files.sort()
        self.log(f"📁 {len(backup_files)} backup dosyası bulundu")
        self.statistics['total_files_analyzed'] = len(backup_files)
        
        # 2. Her dosyayı analiz et
        analyses = []
        for file_path in backup_files:
            analysis = self.analyze_backup_file(file_path)
            analyses.append(analysis)
            if analysis['valid']:
                self.statistics['total_qa_pairs_found'] += analysis['count']
                
        # 3. Veri kaybını tespit et
        loss_report = self.detect_data_loss(analyses)
        
        # 4. Akıllı birleştirme yap
        merged_data = self.smart_merge_data(analyses)
        
        # 5. Rapor oluştur
        recovery_report = self.create_recovery_report(loss_report, len(merged_data))
        
        self.log(f"\n🎉 === RECOVERY TAMAMLANDI ===")
        self.log(f"📊 Kurtarılan veri: {len(merged_data):,} Q&A çifti")
        
        return merged_data, recovery_report

def main():
    """Ana fonksiyon"""
    print("🔧 Ultra Safe Backup Recovery Script")
    print("=" * 50)
    
    # Recovery manager oluştur
    recovery_manager = BackupRecoveryManager()
    
    # Recovery işlemini çalıştır
    recovered_data, report = recovery_manager.run_recovery()
    
    if not recovered_data:
        print("❌ Hiçbir veri kurtarılamadı!")
        return
        
    # Güvenli kaydetme
    os.makedirs('output', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # Kurtarılan veriyi kaydet
    recovered_file = f'output/recovered_data_{timestamp}.json'
    with open(recovered_file, 'w', encoding='utf-8') as f:
        json.dump(recovered_data, f, ensure_ascii=False, indent=2)
    print(f"💾 Kurtarılan veri: {recovered_file}")
    
    # Raporu kaydet
    report_file = f'output/recovery_report_{timestamp}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"📋 Recovery raporu: {report_file}")
    
    # Özet
    print(f"\n📊 === ÖZET ===")
    print(f"🔍 Analiz edilen dosya: {report['analysis_summary']['files_analyzed']}")
    print(f"📦 Bulunan toplam veri: {report['analysis_summary']['total_qa_pairs_found']:,}")
    print(f"🔄 Kaldırılan duplicate: {report['analysis_summary']['duplicates_removed']:,}")
    print(f"✅ Kurtarılan veri: {len(recovered_data):,}")
    print(f"📈 Recovery durumu: {report['recovery_status']}")
    
    if report['data_loss_analysis']['has_loss']:
        print(f"\n⚠️ VERİ KAYBI TESPİT EDİLDİ!")
        print(f"🔧 Backup sistemi düzeltilmeli!")
    else:
        print(f"\n✅ Tüm veriler başarıyla kurtarıldı!")

if __name__ == "__main__":
    main() 